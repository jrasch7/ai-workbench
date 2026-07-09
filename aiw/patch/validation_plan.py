"""Validation Plan for patches - aiw primary (surgical migration step).

Full logic migrated here. aiw_workspace/validation_plan.py is now thin delegate.
Prefer importing from aiw.patch.validation_plan or via aiw.patch / aiw .

No logic changes; pure move + reexports.
"""

from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path

# aiw-first after profiles migration (thin compat)
try:
    from aiw.workspace.profiles import validate_profile, validate_test_command
except Exception:
    from aiw_workspace.profiles import validate_profile, validate_test_command
# aiw-first (step 1: test_runner to aiw/patch)
try:
    from .test_runner import list_test_runs, preview_test_command, run_test_command, suggest_tests_for_patch
except Exception:
    from aiw_workspace.test_runner import list_test_runs, preview_test_command, run_test_command, suggest_tests_for_patch

KIND_FOR_COMMAND = (
    ("syntax", ("py_compile", "bash -n")),
    ("smoke", ("smoke",)),
    ("build", ("build",)),
    ("docs", ("docs", "markdown")),
)


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _workspace_base(workspace_id: str) -> Path:
    return _repo_root() / ".aiw" / "workspaces" / _safe_segment(workspace_id)


def _safe_segment(value: str) -> str:
    segment = str(value or "").strip()
    if not segment or "/" in segment or "\\" in segment or ".." in segment:
        raise ValueError("invalid_id")
    return segment


def _snapshot_root(workspace_id: str, patch_id: str) -> Path:
    return _workspace_base(workspace_id) / "validation-plans" / _safe_segment(patch_id)


def _snapshot_dir(workspace_id: str, patch_id: str, snapshot_id: str) -> Path:
    return _snapshot_root(workspace_id, patch_id) / _safe_segment(snapshot_id)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _read_json(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def _plan_fingerprint(plan_payload: dict) -> str:
    normalized = {
        "changed_files": plan_payload.get("changed_files", []),
        "docs_only": bool(plan_payload.get("docs_only")),
        "plan": plan_payload.get("plan", []),
    }
    raw = json.dumps(normalized, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _new_snapshot_id(plan_payload: dict) -> str:
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    short_hash = _plan_fingerprint(plan_payload)[:8]
    return f"vp-{stamp}-{short_hash}"


def _command_kind(command: str) -> str:
    lower = command.lower()
    for kind, needles in KIND_FOR_COMMAND:
        if any(needle in lower for needle in needles):
            return kind
    return "targeted"


def _source_root_bonus(command: str, changed_files: list[str]) -> int:
    for file_path in changed_files:
        first = file_path.split("/", 1)[0]
        if first and first in command:
            return 15
    return 0


def _score_command(command: str, suggestion: dict | None, group: dict, changed_files: list[str]) -> int:
    score = 0
    if suggestion and suggestion.get("source") == "test_mapping":
        score += 80
    if command in group.get("commands", []):
        score += 20
    score += _source_root_bonus(command, changed_files)
    if group.get("kind") == "syntax" or _command_kind(command) == "syntax":
        score += 10
    if group.get("kind") == "smoke" or "smoke" in command.lower():
        score += 5
    return min(score, 100)


def _reason_for_command(command: str, suggestion: dict | None, group: dict, changed_files: list[str]) -> str:
    if suggestion and suggestion.get("reason"):
        return str(suggestion["reason"])
    if group.get("kind") == "smoke":
        return "Grupo smoke cobre regressao ampla apos patch."
    if _command_kind(command) == "syntax":
        return "Comando de sintaxe relevante para arquivos alterados."
    return "Comando pertence ao grupo de validacao sugerido."


def validation_plan_for_patch(workspace_id: str, patch_id: str) -> dict:
    suggestions_payload = suggest_tests_for_patch(workspace_id, patch_id)
    if not suggestions_payload.get("ok"):
        return suggestions_payload
    profile = validate_profile(workspace_id)
    if not profile.get("ok"):
        return {"ok": False, "error": "invalid_profile", "profile": profile}

    changed_files = suggestions_payload.get("changed_files", [])
    suggestions = suggestions_payload.get("suggestions", [])
    docs_only = bool(suggestions_payload.get("no_technical_test_required")) and all(item.get("command") is None for item in suggestions)
    suggestion_by_command = {item.get("command"): item for item in suggestions if item.get("command")}
    allowed_commands = [str(cmd) for cmd in profile.get("test_commands", [])]
    command_groups = []

    if docs_only:
        return {
            "ok": True,
            "workspace_id": suggestions_payload.get("workspace_id", workspace_id),
            "workspace_name": suggestions_payload.get("workspace_name", workspace_id),
            "patch_id": patch_id,
            "changed_files": changed_files,
            "plan": [],
            "docs_only": True,
            "summary": "Patch altera apenas documentacao. Nenhum teste tecnico obrigatorio foi definido no profile.",
        }

    for group in profile.get("validation_groups", []):
        if not group.get("ok"):
            continue
        group_commands = []
        for command in group.get("commands", []):
            if command not in allowed_commands:
                continue
            validation = validate_test_command(command)
            if not validation.get("ok"):
                continue
            suggestion = suggestion_by_command.get(command)
            score = _score_command(command, suggestion, group, changed_files)
            if score <= 0:
                continue
            group_commands.append({
                "command": command,
                "score": score,
                "source": suggestion.get("source", "validation_group") if suggestion else "validation_group",
                "mapping_name": suggestion.get("mapping_name", "") if suggestion else "",
                "matched_files": suggestion.get("matched_files", changed_files) if suggestion else changed_files,
                "allowed": True,
                "reason": _reason_for_command(command, suggestion, group, changed_files),
            })
        if group_commands:
            group_commands.sort(key=lambda item: item["score"], reverse=True)
            command_groups.append({
                "group": group.get("name", ""),
                "kind": group.get("kind", "targeted"),
                "priority": group.get("priority", 100),
                "reason": group_commands[0]["reason"],
                "commands": group_commands,
            })

    if not command_groups:
        fallback_commands = []
        for suggestion in suggestions:
            command = suggestion.get("command")
            if not command:
                continue
            score = min(100, 80 if suggestion.get("source") == "test_mapping" else 60)
            fallback_commands.append({
                "command": command,
                "score": score,
                "source": suggestion.get("source", "heuristic"),
                "mapping_name": suggestion.get("mapping_name", ""),
                "matched_files": suggestion.get("matched_files", changed_files),
                "allowed": bool(suggestion.get("allowed")),
                "reason": suggestion.get("reason", "Comando sugerido pelo patch."),
            })
        if fallback_commands:
            command_groups.append({
                "group": "Targeted",
                "kind": "targeted",
                "priority": 20,
                "reason": "Fallback para sugestoes diretas do patch.",
                "commands": fallback_commands,
            })

    command_groups.sort(key=lambda group: (group["priority"], -max(cmd["score"] for cmd in group["commands"])))
    return {
        "ok": True,
        "workspace_id": suggestions_payload.get("workspace_id", workspace_id),
        "workspace_name": suggestions_payload.get("workspace_name", workspace_id),
        "patch_id": patch_id,
        "changed_files": changed_files,
        "plan": command_groups,
        "docs_only": False,
        "summary": f"{len(command_groups)} grupo(s) de validacao sugerido(s).",
    }


def _execution_status_by_command(snapshot: dict) -> dict:
    rows = {}
    executions = snapshot.get("executions", {}).get("executions", []) if snapshot.get("executions") else []
    for item in executions:
        command = str(item.get("command", ""))
        if command:
            rows[command] = item
    return rows


def _status_change(previous: str | None, current: str | None) -> str:
    if previous is None and current is not None:
        return "new"
    if previous is not None and current is None:
        return "removed"
    if previous == current:
        return "unchanged"
    if previous in {"failed", "timed_out", "blocked"} and current == "succeeded":
        return "improved"
    if previous == "succeeded" and current in {"failed", "timed_out", "blocked"}:
        return "regressed"
    return "changed"


def _compare_snapshots(previous: dict | None, current: dict) -> dict:
    previous_rows = _execution_status_by_command(previous or {})
    current_rows = _execution_status_by_command(current)
    commands = sorted(set(previous_rows) | set(current_rows))
    changes = []
    summary = {"improved": 0, "regressed": 0, "unchanged": 0, "new": 0, "removed": 0, "changed": 0}
    for command in commands:
        before = previous_rows.get(command)
        after = current_rows.get(command)
        status_change = _status_change(
            before.get("status") if before else None,
            after.get("status") if after else None,
        )
        if status_change in summary:
            summary[status_change] += 1
        previous_duration = before.get("duration_seconds") if before else None
        current_duration = after.get("duration_seconds") if after else None
        duration_delta = None
        if isinstance(previous_duration, (int, float)) and isinstance(current_duration, (int, float)):
            duration_delta = round(current_duration - previous_duration, 3)
        changes.append({
            "command": command,
            "previous_status": before.get("status") if before else None,
            "current_status": after.get("status") if after else None,
            "previous_exit_code": before.get("exit_code") if before else None,
            "current_exit_code": after.get("exit_code") if after else None,
            "status_change": status_change,
            "duration_delta_seconds": duration_delta,
        })
    return {
        "patch_id": current.get("patch_id"),
        "current_snapshot_id": current.get("snapshot_id"),
        "previous_snapshot_id": previous.get("snapshot_id") if previous else None,
        "changes": changes,
        "summary": summary,
    }


def _snapshot_summary(plan_payload: dict, executions_payload: dict, comparison_payload: dict) -> str:
    executions = executions_payload.get("executions", [])
    statuses = {}
    for item in executions:
        status = str(item.get("status", "unknown"))
        statuses[status] = statuses.get(status, 0) + 1
    comparison = comparison_payload.get("summary", {})
    return (
        "# Validation Plan Snapshot\n\n"
        f"- Snapshot: `{plan_payload.get('snapshot_id')}`\n"
        f"- Workspace: `{plan_payload.get('workspace_id')}`\n"
        f"- Patch: `{plan_payload.get('patch_id')}`\n"
        f"- Created at: {plan_payload.get('created_at')}\n"
        f"- Changed files: {len(plan_payload.get('changed_files', []))}\n"
        f"- Groups: {len(plan_payload.get('plan', []))}\n"
        f"- Executions: {len(executions)}\n"
        f"- Statuses: {json.dumps(statuses, sort_keys=True)}\n"
        f"- Comparison: improved={comparison.get('improved', 0)}, "
        f"regressed={comparison.get('regressed', 0)}, unchanged={comparison.get('unchanged', 0)}, "
        f"new={comparison.get('new', 0)}, removed={comparison.get('removed', 0)}\n"
    )


def _load_snapshot(workspace_id: str, patch_id: str, snapshot_id: str) -> dict:
    root = _snapshot_dir(workspace_id, patch_id, snapshot_id)
    plan = _read_json(root / "plan.json", {})
    executions = _read_json(root / "executions.json", {"executions": []})
    comparison = _read_json(root / "comparison.json", {"changes": [], "summary": {}})
    return {
        "ok": bool(plan),
        "snapshot_id": snapshot_id,
        "workspace_id": workspace_id,
        "patch_id": patch_id,
        "plan": plan,
        "executions": executions,
        "comparison": comparison,
        "summary_path": str(root / "summary.md"),
        "artifact_dir": str(root),
    }


def _snapshot_rows(workspace_id: str, patch_id: str) -> list[dict]:
    root = _snapshot_root(workspace_id, patch_id)
    rows = []
    if not root.is_dir():
        return rows
    for path in sorted([p for p in root.iterdir() if p.is_dir()], reverse=True):
        snapshot = _load_snapshot(workspace_id, patch_id, path.name)
        if not snapshot.get("ok"):
            continue
        plan = snapshot.get("plan", {})
        executions = snapshot.get("executions", {}).get("executions", [])
        comparison = snapshot.get("comparison", {})
        statuses = {}
        for execution in executions:
            status = str(execution.get("status", "unknown"))
            statuses[status] = statuses.get(status, 0) + 1
        rows.append({
            "snapshot_id": path.name,
            "workspace_id": workspace_id,
            "patch_id": patch_id,
            "created_at": plan.get("created_at"),
            "changed_files": plan.get("changed_files", []),
            "group_count": len(plan.get("plan", [])),
            "execution_count": len(executions),
            "status_summary": statuses,
            "comparison_summary": comparison.get("summary", {}),
        })
    return rows


def _write_snapshot_files(workspace_id: str, patch_id: str, plan_payload: dict, previous_snapshot: dict | None = None) -> dict:
    snapshot_id = plan_payload["snapshot_id"]
    root = _snapshot_dir(workspace_id, patch_id, snapshot_id)
    executions = {
        "snapshot_id": snapshot_id,
        "patch_id": patch_id,
        "executions": [],
    }
    current = {"snapshot_id": snapshot_id, "patch_id": patch_id, "executions": executions}
    comparison = _compare_snapshots(previous_snapshot, current)
    _write_json(root / "plan.json", plan_payload)
    _write_json(root / "executions.json", executions)
    _write_json(root / "comparison.json", comparison)
    (root / "summary.md").write_text(_snapshot_summary(plan_payload, executions, comparison), encoding="utf-8")
    return _load_snapshot(workspace_id, patch_id, snapshot_id)


def ensure_validation_plan_snapshot(workspace_id: str, patch_id: str, force_new: bool = False) -> dict:
    try:
        safe_workspace_id = _safe_segment(workspace_id)
        safe_patch_id = _safe_segment(patch_id)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    plan = validation_plan_for_patch(safe_workspace_id, safe_patch_id)
    if not plan.get("ok"):
        return plan
    fingerprint = _plan_fingerprint(plan)
    rows = _snapshot_rows(safe_workspace_id, safe_patch_id)
    if not force_new:
        for row in rows:
            snapshot = _load_snapshot(safe_workspace_id, safe_patch_id, row["snapshot_id"])
            snapshot_plan = snapshot.get("plan", {})
            executions = snapshot.get("executions", {}).get("executions", [])
            if snapshot_plan.get("fingerprint") == fingerprint and not executions:
                return {"ok": True, "snapshot": snapshot, "plan": snapshot_plan, "reused": True}
    previous_snapshot = _load_snapshot(safe_workspace_id, safe_patch_id, rows[0]["snapshot_id"]) if rows else None
    snapshot_id = _new_snapshot_id(plan)
    root = _snapshot_root(safe_workspace_id, safe_patch_id)
    suffix = 1
    while (root / snapshot_id).exists():
        suffix += 1
        snapshot_id = f"{_new_snapshot_id(plan)}-{suffix}"
    plan_payload = {
        "snapshot_id": snapshot_id,
        "workspace_id": plan.get("workspace_id", safe_workspace_id),
        "workspace_name": plan.get("workspace_name", safe_workspace_id),
        "patch_id": safe_patch_id,
        "created_at": _now(),
        "fingerprint": fingerprint,
        "changed_files": plan.get("changed_files", []),
        "plan": plan.get("plan", []),
        "docs_only": bool(plan.get("docs_only")),
        "summary": plan.get("summary", ""),
    }
    snapshot = _write_snapshot_files(safe_workspace_id, safe_patch_id, plan_payload, previous_snapshot)
    return {"ok": True, "snapshot": snapshot, "plan": plan_payload, "reused": False}


def list_validation_plan_snapshots(workspace_id: str, patch_id: str) -> dict:
    try:
        rows = _snapshot_rows(_safe_segment(workspace_id), _safe_segment(patch_id))
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": True, "workspace_id": workspace_id, "patch_id": patch_id, "snapshots": rows}


def get_validation_plan_snapshot(workspace_id: str, patch_id: str, snapshot_id: str) -> dict:
    try:
        snapshot = _load_snapshot(_safe_segment(workspace_id), _safe_segment(patch_id), _safe_segment(snapshot_id))
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    if not snapshot.get("ok"):
        return {"ok": False, "error": "snapshot_not_found"}
    return snapshot


def compare_validation_plan_snapshots(workspace_id: str, patch_id: str, snapshot_id: str | None = None) -> dict:
    try:
        safe_workspace_id = _safe_segment(workspace_id)
        safe_patch_id = _safe_segment(patch_id)
        safe_snapshot_id = _safe_segment(snapshot_id) if snapshot_id else None
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    rows = _snapshot_rows(safe_workspace_id, safe_patch_id)
    if not rows:
        return {"ok": True, "workspace_id": workspace_id, "patch_id": patch_id, "comparison": None, "snapshots": []}
    current_id = safe_snapshot_id or rows[0]["snapshot_id"]
    current = _load_snapshot(safe_workspace_id, safe_patch_id, current_id)
    if not current.get("ok"):
        return {"ok": False, "error": "snapshot_not_found"}
    current_index = next((idx for idx, row in enumerate(rows) if row["snapshot_id"] == current_id), None)
    previous = None
    if current_index is not None and current_index + 1 < len(rows):
        previous = _load_snapshot(safe_workspace_id, safe_patch_id, rows[current_index + 1]["snapshot_id"])
    comparison = _compare_snapshots(previous, current)
    return {"ok": True, "workspace_id": workspace_id, "patch_id": patch_id, "comparison": comparison, "snapshots": rows}


def _record_execution(workspace_id: str, patch_id: str, snapshot_id: str, command_item: dict, result: dict) -> None:
    root = _snapshot_dir(workspace_id, patch_id, snapshot_id)
    executions = _read_json(root / "executions.json", {"snapshot_id": snapshot_id, "patch_id": patch_id, "executions": []})
    run_result = result.get("result", {})
    executions.setdefault("executions", []).append({
        "command": command_item.get("command"),
        "test_run_id": result.get("test_run_id"),
        "status": result.get("status"),
        "exit_code": run_result.get("exit_code"),
        "duration_seconds": run_result.get("duration_seconds"),
        "started_at": run_result.get("started_at"),
        "finished_at": run_result.get("finished_at"),
        "validation_group": command_item.get("validation_group", ""),
        "score": command_item.get("score"),
        "mapping_name": command_item.get("mapping_name", ""),
        "matched_files": command_item.get("matched_files", []),
    })
    _write_json(root / "executions.json", executions)
    rows = _snapshot_rows(workspace_id, patch_id)
    current_index = next((idx for idx, row in enumerate(rows) if row["snapshot_id"] == snapshot_id), None)
    previous = None
    if current_index is not None and current_index + 1 < len(rows):
        previous = _load_snapshot(workspace_id, patch_id, rows[current_index + 1]["snapshot_id"])
    current = _load_snapshot(workspace_id, patch_id, snapshot_id)
    comparison = _compare_snapshots(previous, current)
    _write_json(root / "comparison.json", comparison)
    plan_payload = _read_json(root / "plan.json", {})
    (root / "summary.md").write_text(_snapshot_summary(plan_payload, executions, comparison), encoding="utf-8")


def validation_reliability(workspace_id: str) -> dict:
    runs = list_test_runs(workspace_id, limit=200)
    if not runs.get("ok"):
        return runs
    areas = {}
    for row in reversed(runs.get("runs", [])):
        if row.get("trigger") != "validation_plan":
            continue
        mapping_name = str(row.get("mapping_name") or "").strip()
        validation_group = str(row.get("validation_group") or "").strip()
        matched_files = [str(item) for item in row.get("matched_files", []) if str(item)]
        source_root = matched_files[0].split("/", 1)[0] if matched_files else ""
        name = mapping_name or validation_group or source_root or "Validation plan"
        key = (name, validation_group, source_root)
        area = areas.setdefault(key, {
            "name": name,
            "mapping_name": mapping_name,
            "validation_group": validation_group,
            "source_root": source_root,
            "runs": 0,
            "succeeded": 0,
            "failed": 0,
            "last_status": "",
        })
        area["runs"] += 1
        if row.get("status") == "succeeded":
            area["succeeded"] += 1
        else:
            area["failed"] += 1
        area["last_status"] = row.get("status", "unknown")
    result = []
    for area in areas.values():
        area["success_rate"] = round(area["succeeded"] / area["runs"], 2) if area["runs"] else 0
        result.append(area)
    result.sort(key=lambda item: (-item["runs"], item["name"]))
    return {"ok": True, "workspace_id": workspace_id, "areas": result}


def _plan_command(workspace_id: str, patch_id: str, command: str) -> tuple[dict | None, str | None]:
    plan = validation_plan_for_patch(workspace_id, patch_id)
    if not plan.get("ok"):
        return None, plan.get("error", "validation_plan_unavailable")
    if not command:
        return None, "command_required"
    for group in plan.get("plan", []):
        for item in group.get("commands", []):
            if item.get("command") == command:
                payload = dict(item)
                payload["validation_group"] = group.get("group", "")
                payload["validation_kind"] = group.get("kind", "")
                return payload, None
    return None, "command_not_in_validation_plan"


def preview_validation_plan_command(workspace_id: str, patch_id: str, command: str) -> dict:
    _, error = _plan_command(workspace_id, patch_id, command)
    if error:
        return {"ok": False, "allowed": False, "error": error}
    return preview_test_command(workspace_id, command=command)


def run_validation_plan_commands(workspace_id: str, patch_id: str, commands: list[str], confirm: bool = False) -> dict:
    if not confirm:
        return {"ok": False, "status": "blocked", "error": "confirm_required"}
    if not commands:
        return {"ok": False, "status": "blocked", "error": "commands_required"}
    snapshot_payload = ensure_validation_plan_snapshot(workspace_id, patch_id, force_new=True)
    if not snapshot_payload.get("ok"):
        return {"ok": False, "status": "blocked", "error": snapshot_payload.get("error", "snapshot_unavailable")}
    snapshot_id = snapshot_payload.get("plan", {}).get("snapshot_id")
    results = []
    for command in commands:
        item, error = _plan_command(workspace_id, patch_id, command)
        if error:
            return {"ok": False, "status": "blocked", "error": error, "command": command}
        result = run_test_command(
            workspace_id,
            command=command,
            confirm=True,
            trigger="validation_plan",
            patch_id=patch_id,
            validation_snapshot_id=snapshot_id,
            validation_group=item.get("validation_group", ""),
            validation_score=item.get("score"),
            mapping_name=item.get("mapping_name", ""),
            matched_files=item.get("matched_files", []),
        )
        _record_execution(workspace_id, patch_id, snapshot_id, item, result)
        results.append(result)
    return {
        "ok": all(item.get("status") == "succeeded" for item in results),
        "status": "succeeded" if all(item.get("status") == "succeeded" for item in results) else "failed",
        "patch_id": patch_id,
        "validation_snapshot_id": snapshot_id,
        "snapshot": get_validation_plan_snapshot(workspace_id, patch_id, snapshot_id),
        "results": results,
    }
