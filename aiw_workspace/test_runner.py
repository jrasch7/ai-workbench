import datetime
import json
import os
import shlex
import subprocess
import time
import glob
import fnmatch
from pathlib import Path

from .profiles import load_workspaces_config, resolve_workspace, validate_profile, validate_test_command
from .coverage_report import load_coverage_reports


MAX_LOG_CHARS = 120_000
SUMMARY_CHARS = 4_000
DEFAULT_TIMEOUT = 120
MAX_TIMEOUT = 300
SENSITIVE_PARTS = (".env", "token", "secret", "password", "credential", "private_key", "client_secret", "api_key")


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _workspace_base(workspace_id: str) -> Path:
    return Path(__file__).resolve().parents[1] / ".aiw" / "workspaces" / workspace_id


def _mask(text: str) -> str:
    value = text or ""
    lowered = value.lower()
    if any(part in lowered for part in SENSITIVE_PARTS):
        value = value.replace(".env", "[masked-env]")
        for part in SENSITIVE_PARTS[1:]:
            value = value.replace(part, "[masked]")
            value = value.replace(part.upper(), "[masked]")
    if len(value) > MAX_LOG_CHARS:
        return value[:MAX_LOG_CHARS] + "\n[truncated]\n"
    return value


def _minimal_env() -> dict:
    env = {}
    for key in ("PATH", "HOME", "LANG", "LC_ALL", "TERM"):
        if os.environ.get(key):
            env[key] = os.environ[key]
    return env


def _resolve_inside(root: Path, candidate: Path) -> Path:
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        raise ValueError("path_escape_blocked")
    if any(part in {".git", ".venv", "node_modules", "vendor", "__pycache__"} for part in resolved.relative_to(root).parts):
        raise ValueError("blocked_path")
    return resolved


def _expand_arg(root: Path, arg: str) -> list[str]:
    if not any(ch in arg for ch in ("*", "?", "[")):
        if arg.startswith("/") or ".." in Path(arg).parts:
            raise ValueError("unsafe_relative_path")
        return [arg]
    if arg.startswith("/") or ".." in Path(arg).parts:
        raise ValueError("unsafe_glob")
    matches = []
    for match in glob.glob(str(root / arg)):
        resolved = _resolve_inside(root, Path(match))
        matches.append(str(resolved.relative_to(root)))
    return sorted(matches) if matches else [arg]


def _prepare_argv(root: Path, command: str) -> list[str]:
    parts = shlex.split(command)
    argv = []
    for part in parts:
        argv.extend(_expand_arg(root, part))
    return argv


def _command_from_profile(workspace_id: str, command_index: int | None = None, command: str | None = None) -> tuple[dict | None, str | None]:
    profile = validate_profile(workspace_id)
    if not profile.get("ok"):
        return None, "invalid_profile"
    commands = [str(cmd) for cmd in profile.get("test_commands", [])]
    selected = None
    if command_index is not None:
        if command_index < 0 or command_index >= len(commands):
            return None, "command_index_out_of_range"
        selected = commands[command_index]
    elif command is not None:
        if command not in commands:
            return None, "command_not_in_profile"
        selected = command
    else:
        return None, "command_required"
    return {"profile": profile, "command": selected, "command_index": commands.index(selected)}, None


def preview_test_command(workspace_id: str, command_index: int | None = None, command: str | None = None, timeout: int = DEFAULT_TIMEOUT) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws or not ws.get("exists"):
        return {"ok": False, "allowed": False, "error": "unknown_or_missing_workspace"}
    selected, error = _command_from_profile(workspace_id, command_index, command)
    if error:
        return {"ok": False, "allowed": False, "error": error}
    command_text = selected["command"]
    validation = validate_test_command(command_text)
    root = Path(ws["resolved_path"]).resolve()
    timeout = max(1, min(int(timeout or DEFAULT_TIMEOUT), MAX_TIMEOUT))
    argv = []
    argv_error = ""
    if validation.get("ok"):
        try:
            argv = _prepare_argv(root, command_text)
        except Exception as exc:
            argv_error = str(exc)
            validation = {"command": command_text, "ok": False, "reason": argv_error}
    return {
        "ok": validation.get("ok", False),
        "allowed": validation.get("ok", False),
        "reason": validation.get("reason", ""),
        "command": command_text,
        "command_index": selected["command_index"],
        "argv": argv,
        "workspace_id": ws["id"],
        "workspace_name": ws["name"],
        "cwd": str(root),
        "timeout": timeout,
        "auto_commit": False,
        "auto_apply": False,
        "push_enabled": False,
    }


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _new_test_run_id(workspace_id: str) -> str:
    base = "test-" + datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    runs_root = _workspace_base(workspace_id) / "test-runs"
    candidate = base
    suffix = 1
    while (runs_root / candidate).exists():
        suffix += 1
        candidate = f"{base}-{suffix}"
    return candidate


def run_test_command(
    workspace_id: str,
    command_index: int | None = None,
    command: str | None = None,
    confirm: bool = False,
    timeout: int = DEFAULT_TIMEOUT,
    rerun_of: str | None = None,
    trigger: str | None = None,
    patch_id: str | None = None,
    validation_group: str | None = None,
    validation_score: int | None = None,
    validation_snapshot_id: str | None = None,
    mapping_name: str | None = None,
    matched_files: list[str] | None = None,
) -> dict:
    if not confirm:
        return {"ok": False, "status": "blocked", "error": "confirm_required"}
    preview = preview_test_command(workspace_id, command_index, command, timeout)
    if not preview.get("allowed"):
        return {"ok": False, "status": "blocked", "preview": preview, "error": preview.get("error") or preview.get("reason")}

    test_run_id = _new_test_run_id(preview["workspace_id"])
    run_dir = _workspace_base(preview["workspace_id"]) / "test-runs" / test_run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    started = _now()
    start_time = time.monotonic()
    status = "failed"
    exit_code = None
    stdout = ""
    stderr = ""
    try:
        proc = subprocess.run(
            preview["argv"],
            cwd=preview["cwd"],
            shell=False,
            capture_output=True,
            text=True,
            timeout=preview["timeout"],
            env=_minimal_env(),
        )
        exit_code = proc.returncode
        stdout = _mask(proc.stdout)
        stderr = _mask(proc.stderr)
        status = "succeeded" if proc.returncode == 0 else "failed"
    except subprocess.TimeoutExpired as exc:
        stdout = _mask(exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", "replace"))
        stderr = _mask(exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode("utf-8", "replace"))
        status = "timed_out"
    except Exception as exc:
        stderr = _mask(str(exc))
        status = "blocked"

    duration = round(time.monotonic() - start_time, 3)
    finished = _now()
    metadata = {
        "test_run_id": test_run_id,
        "workspace_id": preview["workspace_id"],
        "workspace_name": preview["workspace_name"],
        "workspace_root": preview["cwd"],
        "started_at": started,
        "finished_at": finished,
        "status": status,
        "command": preview["command"],
        "exit_code": exit_code,
        "duration_seconds": duration,
    }
    if rerun_of:
        metadata["rerun_of"] = rerun_of
        metadata["parent_test_run_id"] = rerun_of
    if trigger:
        metadata["trigger"] = trigger
    if patch_id:
        metadata["patch_id"] = patch_id
    if validation_group:
        metadata["validation_group"] = validation_group
    if validation_score is not None:
        metadata["score"] = validation_score
    if validation_snapshot_id:
        metadata["validation_snapshot_id"] = validation_snapshot_id
    if mapping_name:
        metadata["mapping_name"] = mapping_name
    if matched_files:
        metadata["matched_files"] = [str(item) for item in matched_files]
    result = {"ok": status == "succeeded", **metadata}
    _write_json(run_dir / "metadata.json", metadata)
    _write_json(run_dir / "command.json", preview)
    (run_dir / "stdout.log").write_text(stdout, encoding="utf-8")
    (run_dir / "stderr.log").write_text(stderr, encoding="utf-8")
    _write_json(run_dir / "result.json", result)
    (run_dir / "summary.md").write_text(
        f"# Profile Test Run\n\n"
        f"- Workspace: {preview['workspace_name']} (`{preview['workspace_id']}`)\n"
        f"- Command: `{preview['command']}`\n"
        f"- Status: {status}\n"
        f"- Exit code: {exit_code}\n"
        f"- Duration: {duration}s\n",
        encoding="utf-8",
    )

    from .coverage_report import capture_test_run_coverage
    capture_test_run_coverage(preview["workspace_id"], test_run_id)

    return {"ok": status == "succeeded", "status": status, "test_run_id": test_run_id, "result": result, "run_dir": str(run_dir)}


def _run_row_from_dir(workspace_id: str, run_dir: Path) -> dict:
    meta_path = run_dir / "metadata.json"
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        meta = {"test_run_id": run_dir.name, "status": "invalid"}
    meta.setdefault("test_run_id", run_dir.name)
    meta.setdefault("workspace_id", workspace_id)
    meta["artifact_dir"] = str(run_dir)
    meta["artifact_files"] = {
        name: str(run_dir / name)
        for name in ("metadata.json", "command.json", "stdout.log", "stderr.log", "result.json", "summary.md")
        if (run_dir / name).exists()
    }
    return meta


def list_test_runs(workspace_id: str, limit: int = 30, status: str | None = None, q: str | None = None) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "unknown_workspace"}
    root = _workspace_base(ws["id"]) / "test-runs"
    rows = []
    if root.is_dir():
        q_lower = (q or "").lower()
        allowed_statuses = {"succeeded", "failed", "timed_out", "blocked"}
        status_filter = status if status in allowed_statuses else ""
        for run_dir in sorted([p for p in root.iterdir() if p.is_dir()], reverse=True):
            row = _run_row_from_dir(ws["id"], run_dir)
            if status_filter and row.get("status") != status_filter:
                continue
            if q_lower:
                haystack = " ".join(str(row.get(k, "")) for k in ("test_run_id", "command", "status", "workspace_name", "trigger", "patch_id")).lower()
                if q_lower not in haystack:
                    continue
            rows.append(row)
            if len(rows) >= limit:
                break
    return {"ok": True, "workspace_id": ws["id"], "runs": rows}


def list_all_test_runs(
    workspace_id: str | None = None,
    limit: int = 50,
    status: str | None = None,
    q: str | None = None,
    trigger: str | None = None,
    patch_id: str | None = None,
) -> dict:
    try:
        limit = max(1, min(int(limit or 50), 200))
    except Exception:
        limit = 50
    workspace_ids = []
    if workspace_id:
        workspace_ids = [workspace_id]
    else:
        workspace_ids = [ws["id"] for ws in load_workspaces_config().get("workspaces", [])]
    rows = []
    errors = []
    for ws_id in workspace_ids:
        payload = list_test_runs(ws_id, limit=limit, status=status, q=q)
        if payload.get("ok"):
            for row in payload.get("runs", []):
                if trigger and row.get("trigger") != trigger:
                    continue
                if patch_id and row.get("patch_id") != patch_id:
                    continue
                rows.append(row)
        else:
            errors.append({"workspace_id": ws_id, "error": payload.get("error", "unknown")})
    rows.sort(key=lambda row: str(row.get("started_at") or row.get("test_run_id") or ""), reverse=True)
    return {"ok": True, "runs": rows[:limit], "count": min(len(rows), limit), "errors": errors}


def get_test_run(workspace_id: str, test_run_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "unknown_workspace"}
    if not test_run_id.startswith("test-") or "/" in test_run_id or ".." in test_run_id:
        return {"ok": False, "error": "invalid_test_run_id"}
    run_dir = _workspace_base(ws["id"]) / "test-runs" / test_run_id
    if not run_dir.is_dir():
        return {"ok": False, "error": "test_run_not_found"}
    def read_json_file(name):
        try:
            return json.loads((run_dir / name).read_text(encoding="utf-8"))
        except Exception:
            return {}
    def read_text_file(name):
        try:
            return (run_dir / name).read_text(encoding="utf-8", errors="replace")[:SUMMARY_CHARS]
        except Exception:
            return ""
    return {
        "ok": True,
        "workspace_id": ws["id"],
        "test_run_id": test_run_id,
        "metadata": read_json_file("metadata.json"),
        "command": read_json_file("command.json"),
        "result": read_json_file("result.json"),
        "coverage_summary": read_json_file("coverage-summary.json"),
        "stdout": _mask(read_text_file("stdout.log")),
        "stderr": _mask(read_text_file("stderr.log")),
        "summary": read_text_file("summary.md"),
        "artifacts": {
            name: str(run_dir / name)
            for name in ("metadata.json", "command.json", "stdout.log", "stderr.log", "result.json", "summary.md", "coverage-summary.json", "coverage-summary.md")
            if (run_dir / name).exists()
        },
    }


def rerun_test_run(workspace_id: str, test_run_id: str, confirm: bool = False, timeout: int = DEFAULT_TIMEOUT) -> dict:
    if not confirm:
        return {"ok": False, "status": "blocked", "error": "confirm_required"}
    original = get_test_run(workspace_id, test_run_id)
    if not original.get("ok"):
        return {"ok": False, "status": "blocked", "error": original.get("error", "test_run_not_found")}
    command_payload = original.get("command") or {}
    command = str(command_payload.get("command") or original.get("metadata", {}).get("command") or "")
    if not command:
        return {"ok": False, "status": "blocked", "error": "original_command_missing"}
    selected, error = _command_from_profile(workspace_id, command=command)
    if error:
        return {"ok": False, "status": "blocked", "error": error}
    validation = validate_test_command(command)
    if not validation.get("ok"):
        return {"ok": False, "status": "blocked", "error": validation.get("reason", "command_blocked"), "command": command}
    return run_test_command(
        workspace_id,
        command_index=selected["command_index"],
        confirm=True,
        timeout=timeout,
        rerun_of=test_run_id,
    )


def _safe_patch_id(patch_id: str) -> str:
    value = str(patch_id or "").strip()
    if not value or "/" in value or "\\" in value or ".." in value:
        raise ValueError("invalid_patch_id")
    return value


def _patch_file(workspace_id: str, patch_id: str) -> Path:
    safe_patch_id = _safe_patch_id(patch_id)
    scoped = _workspace_base(workspace_id) / "patches" / f"{safe_patch_id}.json"
    if scoped.is_file():
        return scoped
    legacy = Path(__file__).resolve().parents[1] / ".aiw" / "patches" / f"{safe_patch_id}.json"
    return legacy


def load_patch_preview(workspace_id: str, patch_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "unknown_workspace"}
    try:
        patch_path = _patch_file(ws["id"], patch_id)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    if not patch_path.is_file():
        return {"ok": False, "error": "patch_not_found"}
    try:
        data = json.loads(patch_path.read_text(encoding="utf-8"))
    except Exception:
        return {"ok": False, "error": "invalid_patch_json"}
    if not isinstance(data, dict):
        return {"ok": False, "error": "invalid_patch_payload"}
    data.setdefault("patch_id", patch_path.stem)
    data.setdefault("workspace_id", ws["id"])
    data.setdefault("artifact_scope", "scoped" if ".aiw/workspaces/" in str(patch_path) else "legacy")
    if not data.get("changed_files"):
        path = str(data.get("path", "")).strip()
        data["changed_files"] = [path] if path else []
    return {"ok": True, "workspace_id": ws["id"], "patch": data}


def _command_reason(command: str, changed_files: list[str]) -> tuple[str, str] | None:
    lower_command = command.lower()
    files = [str(f) for f in changed_files]
    lower_files = [f.lower() for f in files]
    has_python = any(f.endswith(".py") for f in lower_files)
    has_shell = any(f.startswith("scripts/") or f.endswith(".sh") for f in lower_files)
    has_node = any(
        f == "package.json"
        or f.startswith("src/")
        or f.startswith("frontend/")
        or f.endswith((".ts", ".tsx", ".js", ".jsx"))
        for f in lower_files
    )
    docs_only = bool(lower_files) and all(f.endswith(".md") for f in lower_files)
    if has_python and "python3 -m" in lower_command and ("py_compile" in lower_command or "compileall" in lower_command):
        return "Patch altera arquivos Python cobertos por comando Python do profile.", "high"
    if has_shell and lower_command.startswith("bash -n"):
        return "Patch altera scripts ou shell files cobertos por sintaxe bash do profile.", "high"
    if has_node and lower_command in {"npm run lint", "npm test", "npm run build", "pnpm lint", "pnpm test", "pnpm build"}:
        return "Patch altera area Node/frontend coberta por comando do profile.", "medium"
    if docs_only and ("docs" in lower_command or "markdown" in lower_command):
        return "Patch altera apenas documentacao e existe comando de docs no profile.", "low"
    return None


def _mapping_matches(mapping: dict, changed_files: list[str]) -> list[str]:
    matches = []
    patterns = [str(p) for p in mapping.get("patterns", [])]
    for file_path in changed_files:
        normalized = str(file_path).replace("\\", "/")
        if any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns):
            matches.append(normalized)
    return sorted(set(matches))


def _mapping_suggestions(profile: dict, changed_files: list[str]) -> tuple[list[dict], bool]:
    suggestions = []
    used_mapping = False
    command_checks = {str(c.get("command", "")): c for c in profile.get("test_command_checks", [])}
    seen = set()
    for mapping in profile.get("test_mappings", []):
        if not mapping.get("ok"):
            continue
        matched_files = _mapping_matches(mapping, changed_files)
        if not matched_files:
            continue
        used_mapping = True
        commands = [str(c) for c in mapping.get("commands", [])]
        if not commands:
            suggestions.append({
                "command": None,
                "reason": f"Patch altera arquivos cobertos pelo mapping {mapping.get('name')}; nenhum teste tecnico obrigatorio definido no profile.",
                "confidence": "medium",
                "allowed": True,
                "source": "test_mapping",
                "mapping_name": mapping.get("name", ""),
                "matched_files": matched_files,
                "allowlist_reason": "",
            })
            continue
        for command in commands:
            key = ("test_mapping", mapping.get("name", ""), command)
            if key in seen:
                continue
            seen.add(key)
            validation = validate_test_command(command)
            check = command_checks.get(command, {})
            suggestions.append({
                "command": command,
                "reason": f"Arquivo alterado bateu com mapping {mapping.get('name')}.",
                "confidence": "high",
                "allowed": bool(validation.get("ok")) and bool(check.get("ok")),
                "source": "test_mapping",
                "mapping_name": mapping.get("name", ""),
                "matched_files": matched_files,
                "allowlist_reason": validation.get("reason", ""),
            })
    return suggestions, used_mapping


def suggest_tests_for_patch(workspace_id: str, patch_id: str) -> dict:
    patch_payload = load_patch_preview(workspace_id, patch_id)
    if not patch_payload.get("ok"):
        return patch_payload
    profile = validate_profile(workspace_id)
    if not profile.get("ok"):
        return {"ok": False, "error": "invalid_profile", "profile": profile}
    patch = patch_payload["patch"]
    changed_files = [str(p) for p in patch.get("changed_files", []) if str(p)]
    suggestions, used_mapping = _mapping_suggestions(profile, changed_files)
    if not used_mapping:
        for check in profile.get("test_command_checks", []):
            command = str(check.get("command", ""))
            reason = _command_reason(command, changed_files)
            if not reason:
                continue
            validation = validate_test_command(command)
            suggestions.append({
                "command": command,
                "reason": reason[0],
                "confidence": reason[1],
                "allowed": bool(validation.get("ok")) and bool(check.get("ok")),
                "allowlist_reason": validation.get("reason", ""),
                "source": "heuristic",
                "mapping_name": "",
                "matched_files": changed_files,
            })
    return {
        "ok": True,
        "workspace_id": profile["workspace_id"],
        "workspace_name": profile["workspace_name"],
        "patch_id": patch["patch_id"],
        "changed_files": changed_files,
        "suggestions": suggestions,
        "used_test_mappings": used_mapping,
        "no_technical_test_required": any(item.get("command") is None for item in suggestions) or (bool(changed_files) and all(p.lower().endswith(".md") for p in changed_files) and not suggestions),
    }


def _suggested_command(workspace_id: str, patch_id: str, command: str) -> tuple[dict | None, str | None]:
    suggestions = suggest_tests_for_patch(workspace_id, patch_id)
    if not suggestions.get("ok"):
        return None, suggestions.get("error", "suggestions_unavailable")
    if not command:
        return None, "command_required"
    for item in suggestions.get("suggestions", []):
        if item.get("command") and item.get("command") == command:
            if not item.get("allowed"):
                return None, "suggested_command_blocked"
            return item, None
    return None, "command_not_in_patch_suggestions"


def preview_patch_suggested_test(workspace_id: str, patch_id: str, command: str) -> dict:
    _, error = _suggested_command(workspace_id, patch_id, command)
    if error:
        return {"ok": False, "allowed": False, "error": error}
    return preview_test_command(workspace_id, command=command)


def run_patch_suggested_test(workspace_id: str, patch_id: str, command: str, confirm: bool = False, timeout: int = DEFAULT_TIMEOUT) -> dict:
    if not confirm:
        return {"ok": False, "status": "blocked", "error": "confirm_required"}
    _, error = _suggested_command(workspace_id, patch_id, command)
    if error:
        return {"ok": False, "status": "blocked", "error": error}
    return run_test_command(
        workspace_id,
        command=command,
        confirm=True,
        timeout=timeout,
        trigger="patch_suggestion",
        patch_id=patch_id,
    )


def tests_payload(workspace_id: str) -> dict:
    profile = validate_profile(workspace_id)
    if not profile.get("ok"):
        return profile
    runs = list_test_runs(workspace_id, limit=1)
    return {
        "ok": True,
        "workspace_id": profile["workspace_id"],
        "workspace_name": profile["workspace_name"],
        "stack": profile.get("stack", {}),
        "warnings": profile.get("warnings", []),
        "commands": profile.get("test_command_checks", []),
        "last_result": runs.get("runs", [None])[0] if runs.get("runs") else None,
    }
