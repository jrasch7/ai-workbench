# MIGRAÇÃO CIRÚRGICA: Lógica principal movida de aiw_workspace/coverage_baseline.py para aiw/patch/coverage_baseline.py (test/cov related)
# aiw_workspace/coverage_baseline.py agora thin delegate (lazy __getattr__ pattern).
# Prefer aiw.patch.coverage_baseline or via aiw.patch/aiw .
# Surgical only: move + delegates + aiw-first imports + comments. No behavior change.

import json
import uuid
import datetime
from pathlib import Path

# aiw-first (profiles)
try:
    from aiw.workspace.profiles import resolve_workspace
except Exception:
    from aiw_workspace.profiles import resolve_workspace
# aiw-first (test_runner now also in aiw/patch/)
try:
    from .test_runner import get_test_run, _workspace_base
except Exception:
    from aiw_workspace.test_runner import get_test_run, _workspace_base


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

def _write_json(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def get_current_coverage_baseline(workspace_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "unknown_workspace"}
    base = _workspace_base(ws["id"]) / "coverage-baselines"
    current_file = base / "current.json"
    if not current_file.exists():
        return {"ok": False, "error": "no_baseline"}
    try:
        data = json.loads(current_file.read_text(encoding="utf-8"))
        return {"ok": True, "baseline": data}
    except Exception as e:
        return {"ok": False, "error": f"invalid_baseline: {e}"}

def promote_coverage_baseline(workspace_id: str, test_run_id: str, confirm: bool = False) -> dict:
    if not confirm:
        return {"ok": False, "status": "blocked", "error": "confirm_required"}
        
    run_payload = get_test_run(workspace_id, test_run_id)
    if not run_payload.get("ok"):
        return {"ok": False, "error": "test_run_not_found"}
        
    cov_summary = run_payload.get("coverage_summary")
    if not cov_summary or not cov_summary.get("summary", {}).get("has_reports"):
        return {"ok": False, "error": "no_current_coverage"}
        
    ws = resolve_workspace(workspace_id)
    base = _workspace_base(ws["id"]) / "coverage-baselines"
    base.mkdir(parents=True, exist_ok=True)
    history_base = base / "history"
    history_base.mkdir(parents=True, exist_ok=True)
    
    baseline_id = f"covbase-{uuid.uuid4().hex[:12]}"
    
    # extrair lista combinada de arquivos das reports
    files_list = []
    combined_files_data = {}
    
    for r in cov_summary.get("reports", []):
        for f, data in r.get("files_data", {}).items():
            if f not in combined_files_data:
                combined_files_data[f] = {"covered": 0, "missed": 0}
            combined_files_data[f]["covered"] += data.get("covered", 0)
            combined_files_data[f]["missed"] += data.get("missed", 0)
            
    for f, data in combined_files_data.items():
        total = data["covered"] + data["missed"]
        files_list.append({
            "file": f,
            "line_rate": (data["covered"] / total) if total > 0 else 0.0,
            "covered_lines": data["covered"],
            "missed_lines": data["missed"]
        })
        
    # We strip files_data from the final saved reports to save space, just like in coverage_report
    safe_reports = []
    for r in cov_summary.get("reports", []):
        safe_r = {k: v for k, v in r.items() if k != "files_data"}
        safe_reports.append(safe_r)
        
    baseline_data = {
        "baseline_id": baseline_id,
        "workspace_id": ws["id"],
        "created_at": _now(),
        "source_test_run_id": test_run_id,
        "source": "manual_promotion",
        "coverage_status": cov_summary.get("summary", {}).get("status", "unknown"),
        "average_line_rate": cov_summary.get("summary", {}).get("average_line_rate", 0.0),
        "reports": safe_reports,
        "files": files_list
    }
    
    _write_json(history_base / f"{baseline_id}.json", baseline_data)
    md = f"# Coverage Baseline\n\n- ID: {baseline_id}\n- Source: {test_run_id}\n- Status: {baseline_data['coverage_status']}\n- Average line-rate: {baseline_data['average_line_rate']*100:.1f}%\n"
    (history_base / f"{baseline_id}.md").write_text(md, encoding="utf-8")
    
    # Update current
    _write_json(base / "current.json", baseline_data)
    
    return {"ok": True, "baseline": baseline_data}

def list_coverage_baselines(workspace_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "unknown_workspace"}
    base = _workspace_base(ws["id"]) / "coverage-baselines" / "history"
    if not base.exists():
        return {"ok": True, "baselines": []}
    
    baselines = []
    for p in base.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            baselines.append(data)
        except:
            pass
    baselines.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"ok": True, "baselines": baselines}

def coverage_diff(workspace_id: str, test_run_id: str, patch_id: str = None) -> dict:
    # Obtém baseline
    baseline_payload = get_current_coverage_baseline(workspace_id)
    if not baseline_payload.get("ok"):
        return {"ok": True, "status": "no_baseline", "error": baseline_payload.get("error")}
        
    baseline = baseline_payload["baseline"]
    
    # Obtém coverage atual do test_run
    run_payload = get_test_run(workspace_id, test_run_id)
    if not run_payload.get("ok"):
        return {"ok": False, "error": "test_run_not_found"}
        
    cov_summary = run_payload.get("coverage_summary")
    if not cov_summary or not cov_summary.get("summary", {}).get("has_reports"):
        return {"ok": True, "status": "no_current_coverage", "baseline_id": baseline["baseline_id"]}
        
    # Obtém changed_files do patch (se fornecido)
    changed_files = []
    if patch_id:
        from .test_runner import load_patch_preview
        patch_payload = load_patch_preview(workspace_id, patch_id)
        if patch_payload.get("ok"):
            changed_files = patch_payload.get("patch", {}).get("changed_files", [])
            
    # Comparar line-rate average (overall)
    before_avg = baseline.get("average_line_rate", 0.0)
    after_avg = cov_summary.get("summary", {}).get("average_line_rate", 0.0)
    delta_avg = after_avg - before_avg
    
    if delta_avg < -0.01:
        overall_status = "regressed"
    elif delta_avg > 0.01:
        overall_status = "improved"
    else:
        overall_status = "unchanged"
        
    # Reconstruir arquivos do test run atual
    current_files_data = {}
    for r in cov_summary.get("reports", []):
        for f, data in r.get("files_data", {}).items():
            if f not in current_files_data:
                current_files_data[f] = {"covered": 0, "missed": 0}
            current_files_data[f]["covered"] += data.get("covered", 0)
            current_files_data[f]["missed"] += data.get("missed", 0)
            
    # Mapear baseline files
    baseline_files = {f["file"]: f for f in baseline.get("files", [])}
    
    diff_files = []
    # Usar changed_files do patch se existirem, senao todos os current_files_data
    files_to_compare = changed_files if changed_files else list(current_files_data.keys())
    
    for f in files_to_compare:
        norm_f = f.replace("\\", "/")
        # tenta exact ou suffix
        curr_rate = None
        for cf, data in current_files_data.items():
            if cf == norm_f or cf.endswith("/" + norm_f):
                total = data["covered"] + data["missed"]
                curr_rate = (data["covered"] / total) if total > 0 else 0.0
                break
                
        base_rate = None
        for bf, bdata in baseline_files.items():
            if bf == norm_f or bf.endswith("/" + norm_f):
                base_rate = bdata.get("line_rate", 0.0)
                break
                
        if curr_rate is not None or base_rate is not None:
            cr = curr_rate or 0.0
            br = base_rate or 0.0
            d = cr - br
            if d < -0.01:
                fst = "regressed"
            elif d > 0.01:
                fst = "improved"
            else:
                fst = "unchanged"
            diff_files.append({
                "file": f,
                "before": br,
                "after": cr,
                "delta": d,
                "status": fst
            })
            
    summary_text = ""
    if overall_status == "regressed":
        summary_text = f"Coverage médio caiu {-delta_avg*100:.1f} pontos percentuais em relação à baseline."
    elif overall_status == "improved":
        summary_text = f"Coverage médio melhorou {delta_avg*100:.1f} pontos percentuais em relação à baseline."
    else:
        summary_text = "Coverage médio sem alterações significativas em relação à baseline."
        
    return {
        "ok": True,
        "workspace_id": workspace_id,
        "baseline_id": baseline["baseline_id"],
        "test_run_id": test_run_id,
        "status": overall_status,
        "average_line_rate_before": before_avg,
        "average_line_rate_after": after_avg,
        "delta": delta_avg,
        "files": diff_files,
        "summary": summary_text
    }
