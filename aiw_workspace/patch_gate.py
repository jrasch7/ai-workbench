import datetime
from .test_runner import load_patch_preview
from .validation_plan import (
    ensure_validation_plan_snapshot,
    compare_validation_plan_snapshots,
    validation_plan_for_patch
)
from .test_coverage_intent import analyze_test_coverage_intent

def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def review_gate_for_patch(workspace_id: str, patch_id: str) -> dict:
    patch_payload = load_patch_preview(workspace_id, patch_id)
    if not patch_payload.get("ok"):
        return {"ok": False, "error": patch_payload.get("error", "patch_not_found")}

    patch = patch_payload.get("patch", {})
    patch_status = patch.get("status", "preview")

    if patch_status == "applied":
        return _build_gate_response(workspace_id, patch_id, "applied", 100, False, [], "Patch já foi aplicado.")
    if patch_status == "rolled_back":
        return _build_gate_response(workspace_id, patch_id, "rolled_back", 0, False, [], "Patch foi revertido.")

    # Check 5: Test coverage intent
    coverage_intent = analyze_test_coverage_intent(workspace_id, patch_id, patch_payload_override=patch_payload)
    intent_class = coverage_intent.get("classification", "unknown")
    intent_severity = coverage_intent.get("severity", "none")

    intent_status = "unknown"
    if intent_class in ("code_with_tests", "docs_only"):
        intent_status = "passed"
    elif intent_class == "code_without_tests" or (intent_class == "mixed" and intent_severity == "warning"):
        intent_status = "warning"
    elif intent_class in ("tests_only", "config_only") or (intent_class == "mixed" and intent_severity == "info"):
        intent_status = "info"

    coverage_check = {"name": "Test coverage intent", "status": intent_status, "reason": coverage_intent.get("summary", "")}

    checks = []
    score = 0


    # Check 1: Patch metadata
    changed_files = patch.get("changed_files", [])
    if changed_files:
        checks.append({"name": "Patch metadata", "status": "passed", "reason": "Patch preview existe e possui changed_files."})
        score += 20
    else:
        checks.append({"name": "Patch metadata", "status": "failed", "reason": "Patch não possui arquivos alterados listados."})

    # Check 2: Validation plan
    plan_payload = ensure_validation_plan_snapshot(workspace_id, patch_id)
    if not plan_payload.get("ok"):
        checks.append({"name": "Validation plan", "status": "failed", "reason": f"Falha ao obter validation plan: {plan_payload.get('error')}"})
        return _build_gate_response(workspace_id, patch_id, "needs_validation", score, False, checks, "Falha ao gerar plano de validação.", coverage_intent)

    plan = plan_payload.get("plan", {})
    snapshot = plan_payload.get("snapshot", {})

    if plan.get("docs_only"):
        score = 70
        checks.append({"name": "Validation plan", "status": "passed", "reason": "Patch altera apenas documentação."})
        checks.append(coverage_check)
        return _build_gate_response(workspace_id, patch_id, "docs_only", score, True, checks, "Patch altera apenas documentação, apply manual permitido com confirmação.", coverage_intent)

    plan_groups = plan.get("plan", [])
    if not plan_groups:
        checks.append({"name": "Validation plan", "status": "failed", "reason": "Nenhum teste sugerido/obrigatório para este patch."})
        return _build_gate_response(workspace_id, patch_id, "needs_validation", score, False, checks, "Nenhum plano de validação gerado.", coverage_intent)

    checks.append({"name": "Validation plan", "status": "passed", "reason": "Plano de validação foi gerado."})
    score += 20

    executions = snapshot.get("executions", {}).get("executions", [])
    if not executions:
        checks.append({"name": "Required commands", "status": "failed", "reason": "Nenhum comando do plano foi executado."})
        return _build_gate_response(workspace_id, patch_id, "needs_validation", score, False, checks, "Execute os comandos do plano de validação.", coverage_intent)

    # Collect expected commands
    expected_commands = set()
    for group in plan_groups:
        for cmd in group.get("commands", []):
            expected_commands.add(cmd.get("command"))

    executed_commands = set(e.get("command") for e in executions)
    failed_executions = [e for e in executions if e.get("status") != "succeeded"]

    # Check 3: Required commands
    if not expected_commands.issubset(executed_commands):
        checks.append({"name": "Required commands", "status": "failed", "reason": "Faltam comandos sugeridos a serem executados."})
        gate_status = "partial"
        can_apply = False
        summary = "Validação incompleta. Alguns comandos obrigatórios não rodaram."
    else:
        score += 20
        if failed_executions:
            checks.append({"name": "Required commands", "status": "failed", "reason": "Um ou mais comandos falharam."})
            gate_status = "failed"
            can_apply = False
            summary = "Validação falhou em alguns comandos."
        else:
            score += 25
            checks.append({"name": "Required commands", "status": "passed", "reason": "Todos os comandos executados passaram."})
            gate_status = "ready"
            can_apply = True
            summary = "Todos os testes executados com sucesso."

    # Check 4: Regression check
    comparison = snapshot.get("comparison", {})
    summary_cmp = comparison.get("summary", {})
    if summary_cmp.get("regressed", 0) > 0:
        score = min(score, 35) # Max 35 for regression
        checks.append({"name": "Regression check", "status": "failed", "reason": f"{summary_cmp.get('regressed')} comando(s) regrediu(ram) em relação ao snapshot anterior."})
        gate_status = "regressed"
        can_apply = False
        summary = "Regressão detectada nos testes."
    else:
        score += 15
        checks.append({"name": "Regression check", "status": "passed", "reason": "Nenhuma regressão detectada em relação snapshot anterior."})

    checks.append(coverage_check)

    if intent_class == "code_with_tests":
        score += 5
    elif intent_class == "code_without_tests" or (intent_class == "mixed" and intent_severity == "warning"):
        score -= 10
    elif intent_class == "tests_only":
        score += 3
    elif intent_class == "config_only":
        score -= 5

    if gate_status == "failed":
        score = min(score, 40)
    elif gate_status == "partial":
        score = min(score, 65)

    if score > 100:
        score = 100
    if score < 0:
        score = 0

    return _build_gate_response(workspace_id, patch_id, gate_status, score, can_apply, checks, summary, coverage_intent)

def _build_gate_response(workspace_id: str, patch_id: str, status: str, score: int, can_apply: bool, checks: list, summary: str, coverage_intent: dict = None) -> dict:
    res = {
        "ok": True,
        "workspace_id": workspace_id,
        "patch_id": patch_id,
        "status": status,
        "readiness_score": score,
        "can_apply": can_apply,
        "requires_confirmation": True,
        "checks": checks,
        "summary": summary
    }
    if coverage_intent:
        res["coverage_intent"] = {
            "classification": coverage_intent.get("classification"),
            "severity": coverage_intent.get("severity"),
            "summary": coverage_intent.get("summary")
        }
    return res

def list_review_gates(workspace_id: str, status_filter: str = None, limit: int = 50) -> dict:
    rows = []

    # We need to iterate over patches
    from .test_runner import _workspace_base
    from pathlib import Path
    import os
    import json

    # Re-implementing a simple patch listing since list_patch_proposals is in aiw-cockpit.
    patches_dir = _workspace_base(workspace_id) / "patches"
    seen = set()
    if patches_dir.exists():
        for patch_file in sorted(patches_dir.glob("*.json"), reverse=True):
            try:
                data = json.loads(patch_file.read_text(encoding="utf-8"))
                patch_id = str(data.get("patch_id") or patch_file.stem)
                if patch_id in seen: continue
                seen.add(patch_id)
                gate = review_gate_for_patch(workspace_id, patch_id)
                if gate.get("ok"):
                    if status_filter and gate.get("status") != status_filter:
                        continue
                    rows.append(gate)
                    if len(rows) >= limit: break
            except Exception:
                pass

    # Also check legacy patches
    ROOT = Path(__file__).resolve().parents[1]
    legacy_dir = ROOT / ".aiw" / "patches"
    if legacy_dir.exists() and len(rows) < limit:
        for patch_file in sorted(legacy_dir.glob("*.json"), reverse=True):
            try:
                data = json.loads(patch_file.read_text(encoding="utf-8"))
                patch_id = str(data.get("patch_id") or patch_file.stem)
                if patch_id in seen: continue
                seen.add(patch_id)
                gate = review_gate_for_patch(workspace_id, patch_id)
                if gate.get("ok"):
                    if status_filter and gate.get("status") != status_filter:
                        continue
                    rows.append(gate)
                    if len(rows) >= limit: break
            except Exception:
                pass

    return {"ok": True, "workspace_id": workspace_id, "gates": rows}

def apply_reviewed_patch(workspace_id: str, patch_id: str, confirm: bool, acknowledge_status: str) -> dict:
    if not confirm:
        return {"ok": False, "error": "confirm_required"}

    gate = review_gate_for_patch(workspace_id, patch_id)
    if not gate.get("ok"):
        return gate

    gate_status = gate.get("status")

    # Restrict to ready or docs_only
    if gate_status not in ("ready", "docs_only"):
        return {"ok": False, "error": f"apply_blocked_for_status_{gate_status}"}

    if acknowledge_status and acknowledge_status != gate_status:
        return {"ok": False, "error": "status_mismatch"}

    # We use the existing project_patch_apply tool logic
    import subprocess
    import json
    from pathlib import Path

    # We call the python tool to apply it safely
    # aiw_runtime.tools file is where project_patch_apply is defined. We can import it or run it.
    from aiw_runtime.tools import project_patch_apply

    # actually `project_patch_apply` might expect kwargs
    result = project_patch_apply(patch_id=patch_id)

    return {
        "ok": result.get("ok", False),
        "patch_id": patch_id,
        "workspace_id": workspace_id,
        "status": "applied" if result.get("ok") else "failed",
        "result": result,
        "note": "apply_manual_gate_reviewed"
    }
