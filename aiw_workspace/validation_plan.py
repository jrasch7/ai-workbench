from __future__ import annotations

from .profiles import validate_profile, validate_test_command
from .test_runner import preview_test_command, run_test_command, suggest_tests_for_patch


KIND_FOR_COMMAND = (
    ("syntax", ("py_compile", "bash -n")),
    ("smoke", ("smoke",)),
    ("build", ("build",)),
    ("docs", ("docs", "markdown")),
)


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
            validation_group=item.get("validation_group", ""),
            validation_score=item.get("score"),
        )
        results.append(result)
    return {
        "ok": all(item.get("status") == "succeeded" for item in results),
        "status": "succeeded" if all(item.get("status") == "succeeded" for item in results) else "failed",
        "patch_id": patch_id,
        "results": results,
    }
