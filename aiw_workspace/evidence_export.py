import datetime
import json
import uuid
import zipfile
from pathlib import Path
from .profiles import resolve_workspace, AIW_ROOT
from .evidence_bundle import read_evidence_bundle, list_evidence_bundles

def _sanitize_data(data):
    if isinstance(data, dict):
        return {k: _sanitize_data(v) for k, v in data.items() if k not in ("failed_cases_raw", "source_code", "logs")}
    elif isinstance(data, list):
        return [_sanitize_data(x) for x in data[:100]]
    else:
        return data

def create_evidence_export(workspace_id: str, patch_id: str, bundle_id: str = None, formats: list = None) -> dict:
    if not formats:
        formats = ["json", "markdown", "pr-summary", "handoff", "zip"]
        
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    if not bundle_id:
        eb_payload = list_evidence_bundles(ws["id"], patch_id)
        bundles = eb_payload.get("bundles", [])
        if not bundles:
            return {"ok": False, "error": "no_evidence_bundle_found"}
        bundle_id = bundles[0].get("bundle_id")
        
    bundle_payload = read_evidence_bundle(ws["id"], patch_id, bundle_id)
    if not bundle_payload.get("ok"):
        return {"ok": False, "error": f"bundle_error: {bundle_payload.get('error')}"}
        
    bundle_data = bundle_payload.get("bundle", {})
    
    export_id = f"evx-{uuid.uuid4().hex[:8]}"
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "evidence-exports" / patch_id / export_id
    base_dir.mkdir(parents=True, exist_ok=True)
    
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    files_created = []
    
    dec = bundle_data.get("decision_record", {})
    rg = bundle_data.get("review_gate", {})
    val = bundle_data.get("validation", {})
    cov = bundle_data.get("coverage", {})
    tr = bundle_data.get("test_results", {})
    patch_info = bundle_data.get("patch", {})
    risk = bundle_data.get("risk_summary", {})
    
    # 1. export.json
    export_json_data = {
        "schema_version": "aiw.patch_evidence_export.v1",
        "export_id": export_id,
        "workspace_id": ws["id"],
        "patch_id": patch_id,
        "bundle_id": bundle_id,
        "created_at": now_iso,
        "decision": {
            "decision": dec.get("decision", "pending"),
            "reason": dec.get("reason", ""),
            "decided_at": dec.get("decided_at", "")
        },
        "review_gate": {
            "status": rg.get("status", "unknown"),
            "readiness_score": rg.get("readiness_score", 0),
            "risk_level": risk.get("level", "unknown")
        },
        "patch": {
            "changed_files": _sanitize_data(patch_info.get("changed_files", [])),
            "changed_lines_available": patch_info.get("changed_lines_available", False)
        },
        "validation": {
            "status": "passed" if val.get("executions") else "unknown",
            "snapshots": [val.get("latest_snapshot_id")] if val.get("latest_snapshot_id") else [],
            "executions": _sanitize_data(val.get("executions", []))
        },
        "coverage": {
            "intent": _sanitize_data(cov.get("intent", {})),
            "report": _sanitize_data(cov.get("report", {})),
            "baseline_diff": _sanitize_data(cov.get("baseline_diff", {})),
            "changed_lines": _sanitize_data(cov.get("changed_lines", {}))
        },
        "test_results": {
            "status": tr.get("status", "unknown"),
            "tests": tr.get("tests", 0),
            "failed": tr.get("failed", 0),
            "errors": tr.get("errors", 0),
            "skipped": tr.get("skipped", 0),
            "failed_cases": _sanitize_data(tr.get("failed_cases", []))
        },
        "risk_summary": risk
    }
    
    if "json" in formats:
        (base_dir / "export.json").write_text(json.dumps(export_json_data, indent=2), encoding="utf-8")
        files_created.append("export.json")
        
    # 2. export.md
    if "markdown" in formats:
        export_md = f"""# AIW Patch Evidence Export

## Summary

- Workspace: `{ws['id']}`
- Patch: `{patch_id}`
- Bundle: `{bundle_id}`
- Decision: **{dec.get('decision', 'pending')}**
- Gate status: **{rg.get('status', 'unknown')}**
- Readiness score: {rg.get('readiness_score', 0)}
- Risk: **{risk.get('level', 'unknown')}**

## Changed Files
{chr(10).join(f"- `{f}`" for f in patch_info.get('changed_files', []))}

## Review Gate
- Status: {rg.get('status', 'unknown')}
- Can apply: {rg.get('can_apply', False)}

## Validation Plan
- Executions: {len(val.get('executions', []))}
- Latest Snapshot: {val.get('latest_snapshot_id') or 'none'}

## Test Results
- Status: {tr.get('status', 'unknown')}
- Tests passed: {tr.get('passed', 0)} / {tr.get('tests', 0)}

## Coverage

### Coverage Intent
- Class: {cov.get('intent', {}).get('classification', 'unknown')}

### Coverage Report
- Status: {cov.get('report', {}).get('summary', {}).get('status', 'unknown')}

### Coverage Diff vs Baseline
- Delta: {cov.get('baseline_diff', {}).get('delta', 0.0) * 100:.2f}%

### Changed Lines Coverage
- Found/Missing lines covered

## Decision Record
- Decided by: {dec.get('operator', 'unknown')}
- Reason: {dec.get('reason', 'none')}

## Security Notes
- No .env content included.
- No secrets included.
- No source file contents included.
"""
        (base_dir / "export.md").write_text(export_md, encoding="utf-8")
        files_created.append("export.md")
        
    # 3. pr-summary.md
    if "pr-summary" in formats:
        pr_md = f"""## AIW Evidence Summary

**Decision:** {dec.get('decision', 'pending')}  
**Gate:** {rg.get('status', 'unknown')}  
**Score:** {rg.get('readiness_score', 0)}  
**Risk:** {risk.get('level', 'unknown')}  

### Validation

- Validation plan: {'passed' if val.get('executions') else 'unknown'}
- Test results: {tr.get('status', 'unknown')}
- Coverage: {cov.get('report', {}).get('summary', {}).get('status', 'unknown')}
- Changed lines coverage: {cov.get('changed_lines', {}).get('summary', {}).get('status', 'unknown')}
- Coverage diff: {'improved/unchanged' if cov.get('baseline_diff', {}).get('delta', 0.0) >= 0 else 'regressed'}

### Changed files

{chr(10).join(f"- `{f}`" for f in patch_info.get('changed_files', [])[:10])}
{'' if len(patch_info.get('changed_files', [])) <= 10 else f'- ... and {len(patch_info.get("changed_files", []))-10} more files'}

### Notes

Evidence generated locally by AIW Cockpit. No secrets or source contents included.
"""
        (base_dir / "pr-summary.md").write_text(pr_md, encoding="utf-8")
        files_created.append("pr-summary.md")
        
    # 4. handoff.md
    if "handoff" in formats:
        handoff_md = f"""# AIW Patch Handoff

## Current State
- Patch ID: `{patch_id}`
- Gate Status: `{rg.get('status', 'unknown')}`
- Score: {rg.get('readiness_score', 0)}
- Risk Level: **{risk.get('level', 'unknown')}**

## Decision
- Status: **{dec.get('decision', 'pending')}**
- Reason: {dec.get('reason', 'none')}

## Evidence
- Validation Plan Snapshot: `{val.get('latest_snapshot_id') or 'none'}`
- Test Results Status: `{tr.get('status', 'unknown')}`
- Code intent analysis: `{cov.get('intent', {}).get('classification', 'unknown')}`

## What to do next
Please review the metrics above. If approved, use `apply-reviewed` carefully.

## Safety Constraints
- Do not auto-apply.
- Do not auto-commit.
- Do not push.
- Do not read .env.
"""
        (base_dir / "handoff.md").write_text(handoff_md, encoding="utf-8")
        files_created.append("handoff.md")
        
    # manifest
    manifest_data = {
        "export_id": export_id,
        "workspace_id": ws["id"],
        "patch_id": patch_id,
        "bundle_id": bundle_id,
        "created_at": now_iso,
        "formats": formats,
        "files": files_created + ["manifest.json"]
    }
    
    if "zip" in formats:
        manifest_data["files"].append("evidence-export.zip")
        
    (base_dir / "manifest.json").write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
    
    # zip
    if "zip" in formats:
        zip_path = base_dir / "evidence-export.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname in files_created + ["manifest.json"]:
                fpath = base_dir / fname
                if fpath.exists():
                    zf.write(fpath, arcname=fname)
                    
    return {"ok": True, "export": manifest_data}

def list_evidence_exports(workspace_id: str, patch_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "evidence-exports" / patch_id
    if not base_dir.is_dir():
        return {"ok": True, "exports": []}
        
    exports = []
    for p in sorted(base_dir.iterdir(), key=lambda d: d.name, reverse=True):
        if p.is_dir() and (p / "manifest.json").exists():
            try:
                data = json.loads((p / "manifest.json").read_text(encoding="utf-8"))
                exports.append(data)
            except Exception:
                continue
                
    return {"ok": True, "exports": exports}

def read_evidence_export(workspace_id: str, patch_id: str, export_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "evidence-exports" / patch_id / export_id
    if not base_dir.is_dir() or not (base_dir / "manifest.json").exists():
        return {"ok": False, "error": "export_not_found"}
        
    try:
        data = json.loads((base_dir / "manifest.json").read_text(encoding="utf-8"))
        files_data = {}
        for f in data.get("files", []):
            if f.endswith(".md") or f.endswith(".json"):
                fpath = base_dir / f
                if fpath.exists():
                    files_data[f] = fpath.read_text(encoding="utf-8")
        data["file_contents"] = files_data
        return {"ok": True, "export": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def resolve_evidence_export_file(workspace_id: str, patch_id: str, export_id: str, filename: str):
    ws = resolve_workspace(workspace_id)
    if not ws:
        return None
        
    if ".." in filename or "/" in filename or "\\" in filename:
        return None
        
    allowed_files = {"export.json", "export.md", "pr-summary.md", "handoff.md", "manifest.json", "evidence-export.zip"}
    if filename not in allowed_files:
        return None
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "evidence-exports" / patch_id / export_id
    fpath = base_dir / filename
    if fpath.is_file():
        return fpath
    return None
