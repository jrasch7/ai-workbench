import datetime
import json
import uuid
from pathlib import Path
from .profiles import resolve_workspace, AIW_ROOT
from .patch_gate import review_gate_for_patch
from .test_runner import get_test_run, load_patch_preview
from .validation_plan import ensure_validation_plan_snapshot

def compute_risk_summary(gate_response: dict) -> dict:
    checks = gate_response.get("checks", [])
    status = gate_response.get("status", "unknown")
    
    reasons = []
    level = "low"
    
    # Analyze checks to determine risk
    has_failed_tests = False
    has_uncovered_lines = False
    has_regression = False
    has_partial_cov = False
    no_report = False
    no_tests = False
    
    for chk in checks:
        name = chk.get("name", "")
        chk_status = chk.get("status", "")
        reason = chk.get("reason", "")
        
        if name == "Test result report":
            if chk_status == "failed":
                has_failed_tests = True
                reasons.append(f"Test result failed: {reason}")
            elif chk_status == "info" and "Sem relatório" in reason:
                no_report = True
                reasons.append("No test result report")
        elif name == "Required commands":
            if chk_status == "failed":
                has_failed_tests = True
                reasons.append(f"Validation plan executions failed: {reason}")
        elif name == "Coverage diff vs baseline":
            if chk_status == "warning":
                has_regression = True
                reasons.append(f"Coverage regression: {reason}")
            elif chk_status == "info" and "Nenhuma baseline" in reason:
                reasons.append("No coverage baseline")
        elif name == "Changed lines coverage":
            if chk_status == "warning" and "não possuem cobertura" in reason:
                has_uncovered_lines = True
                reasons.append("Changed lines are uncovered")
            elif chk_status == "warning" and "Cobertura parcial" in reason:
                has_partial_cov = True
                reasons.append("Changed lines partially covered")
            elif chk_status == "warning" and "Relatório sem mapeamento" in reason:
                no_report = True
                reasons.append("No line mapping data")
        elif name == "Coverage report":
            if chk_status == "warning":
                has_partial_cov = True
                reasons.append(f"Coverage partial/missing: {reason}")
        elif name == "Coverage intent":
            if chk_status == "warning" and "code_without_tests" in reason:
                no_tests = True
                reasons.append("Code changes without tests")
                
    if status == "needs_validation" or status == "regressed" or status == "failed":
        level = "high"
        reasons.append("Apply blocked by review gate")
    elif has_failed_tests or has_regression or has_uncovered_lines:
        level = "high"
    elif has_partial_cov or no_report or no_tests or "baseline" in " ".join(reasons):
        if level != "high":
            level = "medium"
            
    if not reasons and status in ("ready", "docs_only"):
        reasons.append("All checks passed or docs only")
        level = "low"
        
    return {"level": level, "reasons": reasons}

def create_evidence_bundle(workspace_id: str, patch_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    patch = load_patch_preview(ws["id"], patch_id)
    if not patch.get("ok"):
        return {"ok": False, "error": f"Patch error: {patch.get('error')}"}
        
    gate_response = review_gate_for_patch(ws["id"], patch_id)
    if not gate_response.get("ok"):
        return {"ok": False, "error": f"Gate error: {gate_response.get('error')}"}
        
    bundle_id = f"evb-{uuid.uuid4().hex[:8]}"
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "evidence-bundles" / patch_id / bundle_id
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract pieces from gate_response
    checks = gate_response.get("checks", [])
    
    # We can fetch snapshot
    snapshot_id = None
    executions = []
    comparison = {}
    plan_payload = ensure_validation_plan_snapshot(ws["id"], patch_id)
    if plan_payload.get("ok"):
        snapshot = plan_payload.get("snapshot", {})
        snapshot_id = snapshot.get("id")
        executions = snapshot.get("executions", {}).get("executions", [])
        comparison = snapshot.get("comparison", {})
        
    # Test results payload
    tr_report = {}
    cl_report = {}
    diff_report = {}
    cov_report = {}
    intent = {}
    
    for chk in checks:
        if chk.get("name") == "Test result report":
            tr_report = chk.get("tr_payload", {})
        elif chk.get("name") == "Changed lines coverage":
            cl_report = chk.get("cl_payload", {})
        elif chk.get("name") == "Coverage diff vs baseline":
            diff_report = chk.get("diff_payload", {})
        elif chk.get("name") == "Coverage report":
            cov_report = chk.get("coverage_payload", {})
        elif chk.get("name") == "Coverage intent":
            intent = chk.get("intent_payload", {})
            
    risk_summary = compute_risk_summary(gate_response)
    
    bundle_data = {
        "bundle_id": bundle_id,
        "workspace_id": ws["id"],
        "patch_id": patch_id,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "patch": {
            "changed_files": patch.get("patch", {}).get("changed_files", []),
            "changed_lines_available": True
        },
        "review_gate": {
            "status": gate_response.get("status"),
            "readiness_score": gate_response.get("readiness_score", 0),
            "can_apply": gate_response.get("can_apply", False),
            "checks": gate_response.get("checks", [])
        },
        "validation": {
            "latest_snapshot_id": snapshot_id,
            "executions": executions,
            "comparison": comparison
        },
        "coverage": {
            "intent": intent,
            "report": cov_report,
            "baseline_diff": diff_report,
            "changed_lines": cl_report
        },
        "test_results": tr_report.get("summary", {}),
        "risk_summary": risk_summary
    }
    
    (base_dir / "bundle.json").write_text(json.dumps(bundle_data, indent=2), encoding="utf-8")
    
    decision_data = {
        "decision": "pending",
        "decided_at": None,
        "reason": None,
        "operator": "local_user",
        "source": "cockpit"
    }
    (base_dir / "decision.json").write_text(json.dumps(decision_data, indent=2), encoding="utf-8")
    
    # Generate summary.md
    md_lines = [
        f"# Patch Evidence Bundle",
        f"",
        f"- Workspace: `{ws['id']}`",
        f"- Patch: `{patch_id}`",
        f"- Status: **{bundle_data['review_gate']['status']}**",
        f"- Score: {bundle_data['review_gate']['readiness_score']}",
        f"- Risk: **{risk_summary['level']}**",
        f"- Changed files: {len(bundle_data['patch']['changed_files'])}",
        f"- Validation: {len(executions)} executions, snapshot: {snapshot_id or 'none'}",
        f"- Coverage: {cov_report.get('summary', {}).get('status', 'unknown')}",
        f"- Changed lines coverage: {cl_report.get('summary', {}).get('status', 'unknown')}",
        f"- Test results: {tr_report.get('summary', {}).get('status', 'unknown')}",
        f"- Decision: pending",
    ]
    (base_dir / "summary.md").write_text("\n".join(md_lines), encoding="utf-8")
    
    return {"ok": True, "bundle": bundle_data, "decision": decision_data}

def list_evidence_bundles(workspace_id: str, patch_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "evidence-bundles" / patch_id
    if not base_dir.is_dir():
        return {"ok": True, "bundles": []}
        
    bundles = []
    for p in sorted(base_dir.iterdir(), key=lambda d: d.name, reverse=True):
        if p.is_dir() and (p / "bundle.json").exists():
            try:
                data = json.loads((p / "bundle.json").read_text(encoding="utf-8"))
                dec = {}
                if (p / "decision.json").exists():
                    dec = json.loads((p / "decision.json").read_text(encoding="utf-8"))
                data["decision_record"] = dec
                bundles.append(data)
            except Exception:
                continue
                
    return {"ok": True, "bundles": bundles}

def read_evidence_bundle(workspace_id: str, patch_id: str, bundle_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "evidence-bundles" / patch_id / bundle_id
    if not base_dir.is_dir() or not (base_dir / "bundle.json").exists():
        return {"ok": False, "error": "bundle_not_found"}
        
    try:
        data = json.loads((base_dir / "bundle.json").read_text(encoding="utf-8"))
        dec = {}
        if (base_dir / "decision.json").exists():
            dec = json.loads((base_dir / "decision.json").read_text(encoding="utf-8"))
        data["decision_record"] = dec
        try:
            data["summary_md"] = (base_dir / "summary.md").read_text(encoding="utf-8")
        except:
            data["summary_md"] = ""
        return {"ok": True, "bundle": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def record_patch_decision(workspace_id: str, patch_id: str, bundle_id: str, decision: str, reason: str = None) -> dict:
    allowed_decisions = {"approved", "rejected", "needs_work", "applied", "rolled_back", "pending"}
    if decision not in allowed_decisions:
        return {"ok": False, "error": "invalid_decision"}
        
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "evidence-bundles" / patch_id / bundle_id
    if not base_dir.is_dir() or not (base_dir / "decision.json").exists():
        return {"ok": False, "error": "bundle_not_found"}
        
    try:
        dec = json.loads((base_dir / "decision.json").read_text(encoding="utf-8"))
        dec["decision"] = decision
        dec["decided_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        dec["reason"] = reason
        (base_dir / "decision.json").write_text(json.dumps(dec, indent=2), encoding="utf-8")
        
        # update summary.md decision line
        summary_path = base_dir / "summary.md"
        if summary_path.exists():
            lines = summary_path.read_text(encoding="utf-8").splitlines()
            for i, line in enumerate(lines):
                if line.startswith("- Decision:"):
                    lines[i] = f"- Decision: **{decision}**"
            summary_path.write_text("\n".join(lines), encoding="utf-8")
            
        return {"ok": True, "decision": dec}
    except Exception as e:
        return {"ok": False, "error": str(e)}
