import xml.etree.ElementTree as ET
from pathlib import Path
from aiw_workspace.profiles import resolve_workspace

def parse_junit_xml(path: Path, report_name: str) -> dict:
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        
        tests = 0
        failed = 0
        errors = 0
        skipped = 0
        failed_cases = []
        
        # O JUnit XML pode ter a tag root como <testsuites> ou diretamente <testsuite>
        if root.tag == "testsuites":
            testsuites = root.findall(".//testsuite")
        elif root.tag == "testsuite":
            testsuites = [root]
        else:
            testsuites = root.findall(".//testsuite")
            if not testsuites:
                # Fallback, tenta buscar em tudo
                testsuites = [root]
                
        for ts in testsuites:
            tests += int(ts.attrib.get("tests", "0"))
            failed += int(ts.attrib.get("failures", "0"))
            errors += int(ts.attrib.get("errors", "0"))
            skipped += int(ts.attrib.get("skipped", "0"))
            
        # Percorrer os testcases para buscar os failed/errors
        for tc in root.findall(".//testcase"):
            for f in tc.findall("failure"):
                msg = f.attrib.get("message", "") or f.text or ""
                if len(msg) > 500:
                    msg = msg[:500] + " ... [truncated]"
                failed_cases.append({
                    "classname": tc.attrib.get("classname", ""),
                    "name": tc.attrib.get("name", ""),
                    "type": f.attrib.get("type", "failure"),
                    "message": msg.strip(),
                    "report": report_name
                })
            for err in tc.findall("error"):
                msg = err.attrib.get("message", "") or err.text or ""
                if len(msg) > 500:
                    msg = msg[:500] + " ... [truncated]"
                failed_cases.append({
                    "classname": tc.attrib.get("classname", ""),
                    "name": tc.attrib.get("name", ""),
                    "type": err.attrib.get("type", "error"),
                    "message": msg.strip(),
                    "report": report_name
                })
                
        return {
            "ok": True,
            "tests": tests,
            "failed": failed,
            "errors": errors,
            "skipped": skipped,
            "failed_cases": failed_cases
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

def analyze_test_results(workspace_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}

    profile = ws.get("profile", {})
    reports_config = profile.get("test_result_reports", [])
    root = Path(ws["resolved_path"])
    
    total_tests = 0
    total_failed = 0
    total_errors = 0
    total_skipped = 0
    all_failed_cases = []
    has_reports = False
    
    for report in reports_config:
        r_path = report.get("path", "")
        fmt = report.get("format", "unknown")
        name = report.get("name", "")
        
        if not r_path or ".." in Path(r_path).parts or r_path.startswith("/") or ".env" in r_path:
            continue
            
        full_path = root / r_path
        if not full_path.is_file():
            continue
            
        parsed = None
        if fmt == "junit_xml":
            parsed = parse_junit_xml(full_path, name)
            
        if parsed and parsed.get("ok"):
            has_reports = True
            total_tests += parsed.get("tests", 0)
            total_failed += parsed.get("failed", 0)
            total_errors += parsed.get("errors", 0)
            total_skipped += parsed.get("skipped", 0)
            all_failed_cases.extend(parsed.get("failed_cases", []))

    if not has_reports:
        return {
            "workspace_id": workspace_id,
            "summary": {
                "has_reports": False,
                "tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "status": "no_report"
            },
            "failed_cases": []
        }

    status = "passed"
    if total_errors > 0:
        status = "error"
    elif total_failed > 0:
        status = "failed"
        
    return {
        "workspace_id": workspace_id,
        "summary": {
            "has_reports": True,
            "tests": total_tests,
            "passed": total_tests - total_failed - total_errors - total_skipped,
            "failed": total_failed,
            "errors": total_errors,
            "skipped": total_skipped,
            "status": status
        },
        "failed_cases": all_failed_cases
    }

def capture_test_result_report(workspace_id: str, test_run_id: str) -> dict:
    from .profiles import resolve_workspace
    import json
    import datetime
    
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace not found"}
        
    root = Path(ws["resolved_path"])
    run_dir = root / ".aiw" / "workspaces" / workspace_id / "test-runs" / test_run_id
    if not run_dir.is_dir():
        return {"ok": False, "error": "test run not found"}
        
    meta_path = run_dir / "metadata.json"
    if meta_path.exists():
        try:
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            metadata = {}
    else:
        metadata = {}

    tr_res = analyze_test_results(workspace_id)
    if not tr_res.get("summary", {}).get("has_reports"):
        metadata["test_results_captured"] = False
        metadata["test_results_status"] = "no_report"
        meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        return {"ok": True, "captured": False}
        
    summary = tr_res["summary"]
    tr_res["captured_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    
    (run_dir / "test-results-summary.json").write_text(json.dumps(tr_res, indent=2), encoding="utf-8")
    
    metadata["test_results_captured"] = True
    metadata["test_results_status"] = summary.get("status")
    metadata["test_results_total"] = summary.get("tests", 0)
    metadata["test_results_failed"] = summary.get("failed", 0)
    metadata["test_results_errors"] = summary.get("errors", 0)
    metadata["test_results_skipped"] = summary.get("skipped", 0)
    
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    
    md_lines = [
        f"# Test Results",
        f"",
        f"- Status: {metadata['test_results_status']}",
        f"- Total tests: {metadata['test_results_total']}",
        f"- Failed: {metadata['test_results_failed']}",
        f"- Errors: {metadata['test_results_errors']}",
        f"- Skipped: {metadata['test_results_skipped']}",
        f""
    ]
    if tr_res.get("failed_cases"):
        md_lines.append("## Failed Cases")
        for fc in tr_res["failed_cases"]:
            md_lines.append(f"- **{fc.get('classname')}.{fc.get('name')}** ({fc.get('type')}): {fc.get('message')}")
            
    (run_dir / "test-results-summary.md").write_text("\n".join(md_lines), encoding="utf-8")
    
    return {"ok": True, "captured": True, "payload": tr_res}
