# MIGRAÇÃO: Lógica movida de aiw_workspace/changed_lines_coverage.py para aiw/patch/changed_lines_coverage.py
# aiw_workspace/changed_lines_coverage.py agora thin delegate.
# Usada por patch_gate para análise de cobertura em linhas alteradas de patches.

import json
from pathlib import Path

def analyze_changed_lines_coverage(workspace_id: str, patch_id: str, test_run_id: str = None) -> dict:
    # aiw-first lazy imports (avoid cycles with aiw_workspace/__init__.py eager from .delegates)
    try:
        from aiw.workspace.profiles import resolve_workspace
    except Exception:
        from aiw_workspace.profiles import resolve_workspace
    # aiw-first (step 1: test_runner migrated to aiw/patch)
    try:
        from .test_runner import get_test_run, list_test_runs
    except Exception:
        from aiw_workspace.test_runner import get_test_run, list_test_runs
    # coverage_report now local aiw/patch (step 2)
    from .coverage_report import analyze_patch_coverage
    from aiw_runtime.tools import _patches_dir
    patches_dir = _patches_dir()
    patch_file = patches_dir / f"{patch_id}.json"
    
    if not patch_file.exists():
        return {"ok": False, "error": "patch_not_found"}
        
    try:
        patch = json.loads(patch_file.read_text(encoding="utf-8"))
    except Exception as e:
        return {"ok": False, "error": f"invalid_patch_json: {e}"}

    changed_lines_data = patch.get("changed_lines", [])
    
    # Se não tem metadata no patch (versões velhas ou sem diff parseado)
    if not changed_lines_data:
        return {
            "workspace_id": workspace_id,
            "patch_id": patch_id,
            "source": "no_line_data",
            "line_level_available": False,
            "summary": {
                "changed_lines": 0,
                "covered_changed_lines": 0,
                "uncovered_changed_lines": 0,
                "changed_line_coverage": 0.0,
                "status": "no_line_data"
            },
            "files": []
        }

    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    profile = ws.get("profile", {})
    threshold = profile.get("coverage", {}).get("changed_file_threshold", profile.get("coverage", {}).get("default_threshold", 0.70))

    # Carregar o report_payload (test_run_capture ou workspace_report)
    report_payload = None
    source = "no_report"
    
    if test_run_id:
        tr = get_test_run(workspace_id, test_run_id)
        if tr.get("ok") and tr.get("run", {}).get("coverage_summary"):
            report_payload = tr["run"]["coverage_summary"]
            source = "test_run_capture"
    else:
        # Se não especificou test_run_id, tenta achar o último do patch
        runs = list_test_runs(workspace_id, limit=50).get("runs", [])
        runs_for_patch = [r for r in runs if r.get("patch_id") == patch_id and r.get("coverage_summary", {}).get("summary", {}).get("has_reports")]
        if runs_for_patch:
            report_payload = runs_for_patch[0]["coverage_summary"]
            source = "test_run_capture"
        else:
            # Fallback para o workspace_report puro
            report_payload = analyze_patch_coverage(workspace_id, patch_id, patch.get("changed_files", []))
            if report_payload.get("reports"):
                source = "workspace_report"

    if not report_payload or source == "no_report":
        return {
            "workspace_id": workspace_id,
            "patch_id": patch_id,
            "source": "no_report",
            "line_level_available": True,
            "summary": {
                "changed_lines": sum(len(c.get("added_lines", [])) for c in changed_lines_data),
                "covered_changed_lines": 0,
                "uncovered_changed_lines": 0,
                "changed_line_coverage": 0.0,
                "status": "no_report"
            },
            "files": []
        }

    # Extract all files_data
    # No caso de analyze_patch_coverage, ele devolve changed_files_coverage que já filtra
    # Mas pode não expor covered_lines list. Vamos pegar dos reports.
    all_files_data = {}
    for r in report_payload.get("reports", []):
        for fpath, fdata in r.get("files_data", {}).items():
            # Merge if multiple reports
            if fpath not in all_files_data:
                all_files_data[fpath] = {"covered_lines": set(), "missed_lines": set()}
            
            all_files_data[fpath]["covered_lines"].update(fdata.get("covered_lines", []))
            all_files_data[fpath]["missed_lines"].update(fdata.get("missed_lines", []))

    # Cruzar com changed_lines
    result_files = []
    total_added = 0
    total_covered = 0
    total_uncovered = 0
    has_any_line_data = False

    for cl in changed_lines_data:
        file_path = cl.get("file", "")
        added_lines = cl.get("added_lines", [])
        if not added_lines:
            continue
            
        total_added += len(added_lines)
        
        # Encontrar o file em all_files_data via sufixo
        matched_fd = None
        for r_file, r_data in all_files_data.items():
            if r_file.endswith(file_path) or file_path.endswith(r_file):
                matched_fd = r_data
                break
                
        if not matched_fd:
            # Arquivo não tem report
            result_files.append({
                "file": file_path,
                "changed_lines": added_lines,
                "covered_lines": [],
                "uncovered_lines": added_lines,
                "line_rate": 0.0,
                "status": "uncovered"
            })
            total_uncovered += len(added_lines)
            continue
            
        if not matched_fd["covered_lines"] and not matched_fd["missed_lines"]:
            # Arquivo achado mas sem line-level
            result_files.append({
                "file": file_path,
                "changed_lines": added_lines,
                "covered_lines": [],
                "uncovered_lines": added_lines,
                "line_rate": 0.0,
                "status": "uncovered"
            })
            total_uncovered += len(added_lines)
            continue
            
        has_any_line_data = True
            
        cov_l = []
        uncov_l = []
        for l in added_lines:
            if l in matched_fd["covered_lines"]:
                cov_l.append(l)
            else:
                uncov_l.append(l)
                
        total_covered += len(cov_l)
        total_uncovered += len(uncov_l)
        
        line_rate = len(cov_l) / len(added_lines)
        if line_rate >= threshold:
            f_status = "covered"
        elif len(cov_l) > 0:
            f_status = "partial"
        else:
            f_status = "uncovered"
            
        result_files.append({
            "file": file_path,
            "changed_lines": added_lines,
            "covered_lines": cov_l,
            "uncovered_lines": uncov_l,
            "line_rate": line_rate,
            "status": f_status
        })

    if total_added == 0:
        status = "no_line_data"
    elif not has_any_line_data and all_files_data:
        status = "no_line_data"
    else:
        line_rate = total_covered / total_added if total_added > 0 else 0.0
        if line_rate >= threshold:
            status = "covered"
        elif total_covered > 0:
            status = "partial"
        else:
            status = "uncovered"

    return {
        "workspace_id": workspace_id,
        "patch_id": patch_id,
        "source": source,
        "line_level_available": has_any_line_data,
        "summary": {
            "changed_lines": total_added,
            "covered_changed_lines": total_covered,
            "uncovered_changed_lines": total_uncovered,
            "changed_line_coverage": total_covered / total_added if total_added > 0 else 0.0,
            "status": status
        },
        "files": result_files
    }
