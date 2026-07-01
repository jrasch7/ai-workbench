import xml.etree.ElementTree as ET
from pathlib import Path
from aiw_workspace.profiles import resolve_workspace

def parse_cobertura_xml(path: Path) -> dict:
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        files_data = {}
        total_covered = 0
        total_missed = 0
        total_lines = 0

        for package in root.findall(".//package"):
            for cls in package.findall(".//class"):
                filename = cls.attrib.get("filename", "")
                if not filename:
                    continue
                lines = cls.find("lines")
                if lines is None:
                    continue
                covered = 0
                missed = 0
                for line in lines.findall("line"):
                    hits = int(line.attrib.get("hits", "0"))
                    if hits > 0:
                        covered += 1
                    else:
                        missed += 1
                total_covered += covered
                total_missed += missed
                total_lines += covered + missed
                files_data[filename.replace("\\", "/")] = {
                    "covered": covered,
                    "missed": missed,
                    "line_rate": (covered / (covered + missed)) if (covered + missed) > 0 else 0.0
                }

        return {
            "ok": True,
            "files": len(files_data),
            "covered_lines": total_covered,
            "missed_lines": total_missed,
            "files_data": files_data
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

def parse_lcov(path: Path) -> dict:
    try:
        content = path.read_text(encoding="utf-8")
        files_data = {}
        total_covered = 0
        total_missed = 0
        current_file = None
        current_covered = 0
        current_missed = 0

        for line in content.splitlines():
            line = line.strip()
            if line.startswith("SF:"):
                current_file = line[3:].strip().replace("\\", "/")
                current_covered = 0
                current_missed = 0
            elif line.startswith("DA:"):
                parts = line[3:].split(",")
                if len(parts) >= 2:
                    hits = int(parts[1])
                    if hits > 0:
                        current_covered += 1
                    else:
                        current_missed += 1
            elif line == "end_of_record" and current_file:
                files_data[current_file] = {
                    "covered": current_covered,
                    "missed": current_missed,
                    "line_rate": (current_covered / (current_covered + current_missed)) if (current_covered + current_missed) > 0 else 0.0
                }
                total_covered += current_covered
                total_missed += current_missed
                current_file = None

        return {
            "ok": True,
            "files": len(files_data),
            "covered_lines": total_covered,
            "missed_lines": total_missed,
            "files_data": files_data
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

def load_coverage_reports(workspace_id: str) -> list[dict]:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return []

    profile = ws.get("profile", {})
    reports_config = profile.get("coverage_reports", [])
    root = Path(ws["resolved_path"])

    loaded_reports = []

    for report in reports_config:
        r_path = report.get("path", "")
        fmt = report.get("format", "unknown")
        name = report.get("name", "")
        threshold = report.get("threshold", profile.get("coverage", {}).get("default_threshold", 0.70))

        if not r_path or ".." in Path(r_path).parts or r_path.startswith("/") or ".env" in r_path:
            continue

        full_path = root / r_path
        if not full_path.is_file():
            loaded_reports.append({
                "name": name,
                "format": fmt,
                "path": r_path,
                "exists": False
            })
            continue

        parsed = None
        if fmt == "cobertura_xml":
            parsed = parse_cobertura_xml(full_path)
        elif fmt == "lcov":
            parsed = parse_lcov(full_path)

        if parsed and parsed.get("ok"):
            loaded_reports.append({
                "name": name,
                "format": fmt,
                "path": r_path,
                "exists": True,
                "files": parsed.get("files", 0),
                "covered_lines": parsed.get("covered_lines", 0),
                "missed_lines": parsed.get("missed_lines", 0),
                "line_rate": (parsed.get("covered_lines", 0) / (parsed.get("covered_lines", 0) + parsed.get("missed_lines", 0))) if (parsed.get("covered_lines", 0) + parsed.get("missed_lines", 0)) > 0 else 0.0,
                "threshold": threshold,
                "status": "covered" if ((parsed.get("covered_lines", 0) / (parsed.get("covered_lines", 0) + parsed.get("missed_lines", 0))) if (parsed.get("covered_lines", 0) + parsed.get("missed_lines", 0)) > 0 else 0.0) >= threshold else "partial",
                "files_data": parsed.get("files_data", {})
            })
        else:
            loaded_reports.append({
                "name": name,
                "format": fmt,
                "path": r_path,
                "exists": True,
                "error": parsed.get("error", "unknown format or parse failed") if parsed else "unknown format"
            })

    return loaded_reports

def analyze_patch_coverage(workspace_id: str, patch_id: str, changed_files: list[str]) -> dict:
    reports = load_coverage_reports(workspace_id)

    # Strip files_data from reports to avoid huge JSONs in the output array, but keep it for calculations
    safe_reports = []
    combined_files_data = {}

    has_valid_report = False
    for r in reports:
        safe_r = {k: v for k, v in r.items() if k != "files_data"}
        safe_reports.append(safe_r)

        if r.get("exists") and "files_data" in r:
            has_valid_report = True
            for file, data in r["files_data"].items():
                if file not in combined_files_data:
                    combined_files_data[file] = {"covered": 0, "missed": 0}
                combined_files_data[file]["covered"] += data["covered"]
                combined_files_data[file]["missed"] += data["missed"]

    if not reports:
        status = "no_report"
    elif not has_valid_report:
        status = "unknown"
    else:
        status = "no_report" # Will overwrite

    changed_files_coverage = []
    found_count = 0
    missing_count = 0
    total_rate = 0.0

    # Analyze changed files against combined coverage
    for f in changed_files:
        normalized_f = f.replace("\\", "/")

        found = False
        cov = 0
        mis = 0
        rate = 0.0

        # Exact match or suffix match
        for rf, data in combined_files_data.items():
            if rf == normalized_f or rf.endswith("/" + normalized_f):
                found = True
                cov = data["covered"]
                mis = data["missed"]
                total = cov + mis
                rate = (cov / total) if total > 0 else 0.0
                break

        changed_files_coverage.append({
            "file": f,
            "found_in_report": found,
            "covered_lines": cov,
            "missed_lines": mis,
            "line_rate": rate
        })

        if found:
            found_count += 1
            total_rate += rate
        else:
            missing_count += 1

    avg_rate = (total_rate / found_count) if found_count > 0 else 0.0

    if has_valid_report:
        if found_count == 0 and changed_files:
            status = "missing"
        elif missing_count > 0:
            status = "partial"
        elif avg_rate >= 0.70:
            status = "covered"
        else:
            status = "partial"

    if not changed_files and has_valid_report:
        status = "covered"

    return {
        "workspace_id": workspace_id,
        "patch_id": patch_id,
        "reports": safe_reports,
        "changed_files": changed_files,
        "changed_files_coverage": changed_files_coverage,
        "summary": {
            "has_reports": bool(reports),
            "changed_files_found": found_count,
            "changed_files_missing": missing_count,
            "average_changed_file_line_rate": avg_rate,
            "status": status
        }
    }

def capture_test_run_coverage(workspace_id: str, test_run_id: str) -> dict:
    from .profiles import resolve_workspace
    import datetime
    import json

    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace not found"}

    root = Path(ws["resolved_path"])
    run_dir = root / ".aiw" / "workspaces" / workspace_id / "test-runs" / test_run_id
    if not run_dir.is_dir():
        return {"ok": False, "error": "test run not found"}

    reports = load_coverage_reports(workspace_id)

    safe_reports = []
    total_cov = 0
    total_mis = 0
    has_reports = False
    status_counts = {"covered": 0, "partial": 0}

    for r in reports:
        safe_r = {k: v for k, v in r.items() if k != "files_data"}
        safe_reports.append(safe_r)
        if r.get("exists") and "files_data" in r:
            has_reports = True
            total_cov += r.get("covered_lines", 0)
            total_mis += r.get("missed_lines", 0)
            if safe_r.get("status") == "covered":
                status_counts["covered"] += 1
            elif safe_r.get("status") == "partial":
                status_counts["partial"] += 1

    total_lines = total_cov + total_mis
    avg_rate = (total_cov / total_lines) if total_lines > 0 else 0.0

    if not has_reports:
        overall_status = "no_report"
    elif status_counts["partial"] > 0:
        overall_status = "partial"
    else:
        overall_status = "covered"

    summary = {
        "captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "workspace_id": workspace_id,
        "test_run_id": test_run_id,
        "reports": safe_reports,
        "summary": {
            "has_reports": has_reports,
            "average_line_rate": avg_rate,
            "status": overall_status
        }
    }

    run_dir.joinpath("coverage-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md = f"# Coverage Summary\n\n- Status: {overall_status}\n- Average line-rate: {avg_rate*100:.1f}%\n- Reports: {len([r for r in safe_reports if r.get('exists')])}\n"
    run_dir.joinpath("coverage-summary.md").write_text(md, encoding="utf-8")

    meta_path = run_dir / "metadata.json"
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            meta["coverage_captured"] = has_reports
            meta["coverage_status"] = overall_status
            if has_reports:
                meta["coverage_average_line_rate"] = avg_rate
            meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        except Exception:
            pass

    return {"ok": True, "coverage": summary}

