import datetime
from .test_runner import load_patch_preview, list_test_runs
from .validation_plan import (
    ensure_validation_plan_snapshot,
    compare_validation_plan_snapshots,
    validation_plan_for_patch
)
from .test_coverage_intent import analyze_test_coverage_intent
from .coverage_report import analyze_patch_coverage
from .coverage_baseline import coverage_diff
from .changed_lines_coverage import analyze_changed_lines_coverage

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

    # Check 6: Real Coverage Report
    changed_files = patch.get("changed_files", [])

    # Busca captures do run deste patch
    runs_payload = list_test_runs(workspace_id, limit=50)
    runs_for_patch = [r for r in runs_payload.get("runs", []) if r.get("patch_id") == patch_id]

    captured_report = None
    captured_test_result = None
    for r in runs_for_patch:
        if r.get("coverage_summary") and r["coverage_summary"].get("summary", {}).get("has_reports"):
            captured_report = r["coverage_summary"]
        if r.get("test_results") and r["test_results"].get("summary", {}).get("has_reports"):
            captured_test_result = r["test_results"]
            
        if captured_report and captured_test_result:
            break

    if captured_report:
        coverage_report = captured_report
        coverage_report["source"] = "test_run_capture"
        # We need changed_files_coverage to be compatible with UI
        coverage_report["changed_files_coverage"] = []
    else:
        coverage_report = analyze_patch_coverage(workspace_id, patch_id, changed_files)
        coverage_report["source"] = "workspace_report" if coverage_report.get("reports") else "no_report"

    cov_status = coverage_report.get("summary", {}).get("status", "unknown")

    if cov_status == "covered":
        cov_chk_status = "passed"
        cov_reason = "Arquivos alterados possuem cobertura de testes suficiente."
        score += 5
    elif cov_status == "partial":
        cov_chk_status = "warning"
        cov_reason = "Arquivos alterados possuem cobertura parcial ou abaixo do esperado."
        score -= 5
    elif cov_status == "missing":
        cov_chk_status = "warning"
        cov_reason = "Relatório de cobertura existe, mas arquivos alterados não foram cobertos."
        score -= 10
    elif cov_status == "no_report":
        cov_chk_status = "info"
        cov_reason = "Nenhum relatório de cobertura configurado ou existente."
    else:
        cov_chk_status = "info"
        cov_reason = "Status de cobertura desconhecido ou erro ao processar relatório."

    real_coverage_check = {"name": "Coverage report", "status": cov_chk_status, "reason": cov_reason}

    # Check 7: Coverage Diff
    diff_report = {}
    diff_status = "no_current_coverage"
    diff_chk_status = "info"
    diff_reason = "Sem coverage atual para comparar."

    if captured_report:
        diff_payload = coverage_diff(workspace_id, captured_report.get("test_run_id"), patch_id)
        diff_report = diff_payload
        diff_status = diff_payload.get("status", "unknown")

        if diff_status == "improved":
            diff_chk_status = "passed"
            diff_reason = diff_payload.get("summary", "Coverage melhorou.")
            score += 5
        elif diff_status == "unchanged":
            diff_chk_status = "passed"
            diff_reason = diff_payload.get("summary", "Coverage estável.")
            score += 2
        elif diff_status == "regressed":
            diff_chk_status = "warning"
            diff_reason = diff_payload.get("summary", "Coverage regrediu vs baseline.")
            score -= 10
        elif diff_status == "no_baseline":
            diff_chk_status = "info"
            diff_reason = "Nenhuma baseline configurada."
    else:
        diff_reason = "Sem coverage atual (test-run capture) para comparar contra baseline."

    diff_check = {"name": "Coverage diff vs baseline", "status": diff_chk_status, "reason": diff_reason, "diff_payload": diff_report}

    # Check 8: Changed lines coverage
    cl_report = {}
    cl_status = "unknown"
    cl_chk_status = "info"
    cl_reason = "Análise de linhas alteradas não executada."

    cap_run_id = captured_report.get("test_run_id") if captured_report else None
    cl_payload = analyze_changed_lines_coverage(workspace_id, patch_id, cap_run_id)
    if cl_payload.get("ok", True) and "summary" in cl_payload:
        cl_report = cl_payload
        cl_status = cl_payload["summary"].get("status", "unknown")

        if cl_status == "covered":
            cl_chk_status = "passed"
            cl_reason = f"Linhas alteradas estão cobertas ({cl_payload['summary'].get('changed_line_coverage', 0)*100:.1f}%)."
            score += 8
        elif cl_status == "partial":
            cl_chk_status = "warning"
            cl_reason = f"Cobertura parcial nas linhas alteradas ({cl_payload['summary'].get('changed_line_coverage', 0)*100:.1f}%)."
            score -= 8
        elif cl_status == "uncovered":
            cl_chk_status = "warning"
            cl_reason = "Linhas alteradas não possuem cobertura."
            score -= 15
        elif cl_status == "no_line_data":
            cl_chk_status = "warning"
            cl_reason = "Relatório sem mapeamento de linhas ou patch sem metadata de diff."
            score -= 3
        elif cl_status == "no_report":
            cl_chk_status = "info"
            cl_reason = "Sem relatório de coverage."

    cl_check = {"name": "Changed lines coverage", "status": cl_chk_status, "reason": cl_reason, "cl_payload": cl_report}

    # Check 9: Test result report
    tr_report = {}
    tr_status = "unknown"
    tr_chk_status = "info"
    tr_reason = "Análise de resultados de testes não executada."
    
    if captured_test_result:
        tr_report = captured_test_result
        tr_report["source"] = "test_run_capture"
    else:
        from aiw_workspace.test_result_report import analyze_test_results
        tr_report = analyze_test_results(workspace_id)
        tr_report["source"] = "workspace_report" if tr_report.get("summary", {}).get("has_reports") else "no_report"
        
    tr_summ = tr_report.get("summary", {})
    tr_status = tr_summ.get("status", "unknown")
    
    if tr_status == "passed":
        tr_chk_status = "passed"
        tr_reason = f"Todos os {tr_summ.get('tests', 0)} testes passaram."
        score += 5
    elif tr_status == "failed":
        tr_chk_status = "failed"
        tr_reason = f"{tr_summ.get('failed', 0)} falharam de {tr_summ.get('tests', 0)}."
        score -= 15
    elif tr_status == "error":
        tr_chk_status = "failed"
        tr_reason = f"{tr_summ.get('errors', 0)} com erros de {tr_summ.get('tests', 0)}."
        score -= 20
    elif tr_status == "no_report":
        tr_chk_status = "info"
        tr_reason = "Sem relatório de resultado de testes configurado ou existente."
    else:
        tr_chk_status = "warning"
        tr_reason = "Status do resultado de testes desconhecido."
        score -= 3
        
    tr_check = {"name": "Test result report", "status": tr_chk_status, "reason": tr_reason, "tr_payload": tr_report}

    if plan.get("docs_only"):
        score = 70
        checks.append({"name": "Validation plan", "status": "passed", "reason": "Patch altera apenas documentação."})
        checks.append(coverage_check)
        checks.append(real_coverage_check)
        checks.append(diff_check)
        checks.append(cl_check)
        checks.append(tr_check)
        return _build_gate_response(workspace_id, patch_id, "docs_only", score, True, checks, "Patch altera apenas documentação, apply manual permitido com confirmação.", coverage_intent, coverage_report)

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
    checks.append(real_coverage_check)
    checks.append(diff_check)
    checks.append(cl_check)
    checks.append(tr_check)

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

    return _build_gate_response(workspace_id, patch_id, gate_status, score, can_apply, checks, summary, coverage_intent, coverage_report)

def _build_gate_response(workspace_id: str, patch_id: str, status: str, score: int, can_apply: bool, checks: list, summary: str, coverage_intent: dict = None, coverage_report: dict = None) -> dict:
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
    if coverage_report:
        res["coverage_report"] = coverage_report
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

    from aiw_workspace.evidence_bundle import create_evidence_bundle, record_patch_decision
    bundle_res = create_evidence_bundle(workspace_id, patch_id)
    bundle_id = bundle_res.get("bundle", {}).get("bundle_id") if bundle_res.get("ok") else None

    # We use the existing project_patch_apply tool logic
    import subprocess
    import json
    from pathlib import Path

    # We call the python tool to apply it safely
    # aiw_runtime.tools file is where project_patch_apply is defined. We can import it or run it.
    from aiw_runtime.tools import project_patch_apply

    # actually `project_patch_apply` might expect kwargs
    result = project_patch_apply(patch_id=patch_id)
    
    if result.get("ok") and bundle_id:
        record_patch_decision(workspace_id, patch_id, bundle_id, "applied", reason="Applied via review gate")
        from aiw_workspace.patch_review_flow import update_patch_lifecycle
        import datetime
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        update_patch_lifecycle(workspace_id, patch_id, {
            "status": "applied",
            "applied_at": now_iso
        })

    return {
        "ok": result.get("ok", False),
        "patch_id": patch_id,
        "workspace_id": workspace_id,
        "status": "applied" if result.get("ok") else "failed",
        "result": result,
        "bundle_id": bundle_id,
        "note": "apply_manual_gate_reviewed"
    }

def rollback_reviewed_patch(workspace_id: str, patch_id: str, confirm: bool, reason: str = "") -> dict:
    if not confirm:
        return {"ok": False, "error": "confirm_required"}
        
    from aiw_runtime.tools import project_patch_rollback
    from aiw_workspace.patch_review_flow import get_patch_lifecycle, update_patch_lifecycle
    from aiw_workspace.evidence_bundle import record_patch_decision, list_evidence_bundles
    
    life = get_patch_lifecycle(workspace_id, patch_id)
    if not life or life.get("status") != "applied":
        return {"ok": False, "error": "patch_not_applied"}
        
    result = project_patch_rollback(patch_id=patch_id)
    if result.get("ok"):
        import datetime
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        update_patch_lifecycle(workspace_id, patch_id, {
            "status": "rolled_back",
            "rolled_back_at": now_iso
        })
        
        ev_bundles = list_evidence_bundles(workspace_id, patch_id=patch_id)
        if ev_bundles.get("ok") and ev_bundles.get("bundles"):
            bundle_id = ev_bundles["bundles"][0].get("bundle_id")
            if bundle_id:
                record_patch_decision(workspace_id, patch_id, bundle_id, "rolled_back", reason=reason or "Manual rollback")
                
    return {
        "ok": result.get("ok", False),
        "patch_id": patch_id,
        "workspace_id": workspace_id,
        "status": "rolled_back" if result.get("ok") else "failed",
        "result": result
    }
