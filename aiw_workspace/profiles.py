import json
import re
import shlex
import subprocess
from pathlib import Path


AIW_ROOT = Path(__file__).resolve().parents[1]
WORKSPACES_CONFIG = AIW_ROOT / ".aiw" / "workspaces.json"
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")
ALLOWED_TYPES = {"python", "node", "mixed", "docs", "unknown"}
BROAD_PATHS = {Path("/"), Path("/home"), Path("/home/joao"), Path("/tmp"), Path("/mnt")}

DEFAULT_PROFILE = {
    "safe_roots": ["."],
    "source_roots": ["aiw_runtime", "aiw_context", "scripts", "docs"],
    "test_commands": [
        "python3 -m py_compile aiw_runtime/*.py",
        "python3 -m py_compile aiw_context/*.py",
        "bash -n scripts/aiw-cockpit",
    ],
    "blocked_paths": [".env", ".env.*", ".git", "node_modules", ".venv", "vendor", "__pycache__"],
}

DEFAULT_WORKSPACE = {
    "id": "aiw",
    "name": "AI Workbench",
    "path": str(AIW_ROOT),
    "type": "python",
    "profile": DEFAULT_PROFILE,
}


def normalize_workspace_id(workspace_id: str | None = None) -> str:
    value = (workspace_id or "aiw").strip()
    if not SAFE_ID_RE.match(value):
        raise ValueError("invalid_workspace_id")
    return value


def _merge_profile(profile: dict | None) -> dict:
    merged = dict(DEFAULT_PROFILE)
    if isinstance(profile, dict):
        for key in ("safe_roots", "source_roots", "test_commands", "blocked_paths"):
            if isinstance(profile.get(key), list):
                merged[key] = [str(v) for v in profile[key]]
    return merged


def _workspace_from_item(item: dict, seen: set[str]) -> dict | None:
    if not isinstance(item, dict):
        return None
    try:
        ws_id = normalize_workspace_id(str(item.get("id", "")).strip())
    except ValueError:
        return None
    if ws_id in seen:
        return None
    raw_path = str(item.get("path", "")).strip()
    if not raw_path:
        return None
    path = Path(raw_path).expanduser().resolve()
    return {
        "id": ws_id,
        "name": str(item.get("name", ws_id)),
        "path": str(path),
        "type": str(item.get("type", "external")),
        "profile": _merge_profile(item.get("profile")),
    }


def load_workspaces_config() -> dict:
    seen = {"aiw"}
    items = [dict(DEFAULT_WORKSPACE)]
    active = "aiw"
    if WORKSPACES_CONFIG.exists():
        try:
            data = json.loads(WORKSPACES_CONFIG.read_text(encoding="utf-8"))
            for item in data.get("workspaces", []):
                ws = _workspace_from_item(item, seen)
                if ws:
                    seen.add(ws["id"])
                    items.append(ws)
            requested_active = str(data.get("active", "aiw"))
            if requested_active in seen:
                active = requested_active
        except Exception:
            return {"version": 1, "active": "aiw", "workspaces": items, "config_error": "invalid_json"}
    return {"version": 1, "active": active, "workspaces": items}


def resolve_workspace(workspace_id: str | None = None) -> dict | None:
    ws_id = normalize_workspace_id(workspace_id or load_workspaces_config().get("active", "aiw"))
    for ws in load_workspaces_config()["workspaces"]:
        if ws["id"] == ws_id:
            path = Path(ws["path"]).expanduser().resolve()
            resolved = dict(ws)
            resolved["path"] = str(path)
            resolved["resolved_path"] = str(path)
            resolved["exists"] = path.is_dir()
            resolved["execution_enabled"] = path.is_dir()
            resolved["external"] = ws_id != "aiw"
            return resolved
    return None


def execution_policy(workspace_id: str | None = None) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "unknown_workspace"}
    profile = ws.get("profile") or DEFAULT_PROFILE
    return {
        "ok": True,
        "workspace_id": ws["id"],
        "workspace_name": ws["name"],
        "execution_enabled": bool(ws.get("execution_enabled")),
        "root": ws["resolved_path"],
        "safe_roots": profile.get("safe_roots", ["."]),
        "source_roots": profile.get("source_roots", []),
        "test_commands": profile.get("test_commands", []),
        "allowed_shell_commands": ["pwd", "ls", "find", "cat", "sed", "grep", "head", "tail", "git", "bash", "python3"],
        "blocked_paths": profile.get("blocked_paths", DEFAULT_PROFILE["blocked_paths"]),
        "auto_apply": False,
        "auto_commit": False,
        "push_enabled": False,
    }


def _git_value(path: Path, args: list[str]) -> str:
    try:
        proc = subprocess.run(["git", *args], cwd=path, capture_output=True, text=True, timeout=3)
        if proc.returncode == 0:
            return proc.stdout.strip()
    except Exception:
        pass
    return ""


def detect_stack(path: Path) -> dict:
    found = {
        "README": (path / "README.md").is_file() or (path / "README").is_file(),
        "package.json": (path / "package.json").is_file(),
        "pyproject.toml": (path / "pyproject.toml").is_file(),
        "requirements.txt": (path / "requirements.txt").is_file(),
        "pnpm-lock.yaml": (path / "pnpm-lock.yaml").is_file(),
        "package-lock.json": (path / "package-lock.json").is_file(),
        "yarn.lock": (path / "yarn.lock").is_file(),
        "setup.py": (path / "setup.py").is_file(),
        "Dockerfile": (path / "Dockerfile").is_file(),
        "docker-compose.yml": (path / "docker-compose.yml").is_file(),
    }
    md_count = 0
    try:
        blocked_dirs = {".git", ".venv", "node_modules", "vendor", "__pycache__", ".aiw"}
        stack = [path]
        while stack and md_count < 500:
            current = stack.pop()
            for child in current.iterdir():
                if child.name in blocked_dirs or child.name.startswith(".env"):
                    continue
                if child.is_dir():
                    stack.append(child)
                elif child.suffix == ".md":
                    md_count += 1
                    if md_count >= 500:
                        break
    except Exception:
        md_count = 0
    stacks = []
    if found["package.json"] or found["pnpm-lock.yaml"] or found["package-lock.json"] or found["yarn.lock"]:
        stacks.append("node")
    if found["pyproject.toml"] or found["requirements.txt"] or found["setup.py"]:
        stacks.append("python")
    if found["Dockerfile"] or found["docker-compose.yml"]:
        stacks.append("docker")
    if md_count >= 5:
        stacks.append("docs")
    if not stacks:
        stacks.append("unknown")
    primary = "mixed" if len([s for s in stacks if s in ("node", "python")]) > 1 else stacks[0]
    return {"primary": primary, "stacks": stacks, "found": found, "markdown_count": md_count}


def validate_workspace_path(raw_path: str) -> dict:
    risks = []
    path_text = str(raw_path or "").strip()
    if not path_text:
        return {"ok": False, "error": "path_required", "risks": ["path vazio"]}
    path = Path(path_text).expanduser()
    if not path.is_absolute():
        return {"ok": False, "error": "path_must_be_absolute", "path": path_text, "risks": ["path nao absoluto"]}
    resolved = path.resolve()
    exists = resolved.exists()
    is_dir = resolved.is_dir()
    if resolved in BROAD_PATHS:
        risks.append("path amplo demais")
    if ".git" in resolved.parts:
        risks.append("path dentro de .git")
    if not exists:
        risks.append("path inexistente")
    if exists and not is_dir:
        risks.append("path nao e diretorio")

    blocking = [r for r in risks if r in ("path amplo demais", "path dentro de .git", "path inexistente", "path nao e diretorio")]
    if blocking:
        return {
            "ok": False,
            "path": str(resolved),
            "exists": exists,
            "is_dir": is_dir,
            "git_repo": False,
            "branch": "",
            "head": "",
            "stack": {"primary": "unknown", "stacks": ["unknown"], "found": {}, "markdown_count": 0},
            "found_files": {".env": False},
            "risks": risks,
        }

    git_repo = (resolved / ".git").exists() if is_dir else False
    if not git_repo:
        risks.append("workspace sem git")
    readme = ((resolved / "README.md").is_file() or (resolved / "README").is_file()) if is_dir else False
    if not readme:
        risks.append("workspace sem README")

    stack = detect_stack(resolved) if is_dir else {"primary": "unknown", "stacks": ["unknown"], "found": {}, "markdown_count": 0}
    found = stack.get("found", {})
    found[".env"] = (resolved / ".env").exists() if is_dir else False
    return {
        "ok": not blocking,
        "path": str(resolved),
        "exists": exists,
        "is_dir": is_dir,
        "git_repo": git_repo,
        "branch": _git_value(resolved, ["branch", "--show-current"]) if git_repo else "",
        "head": _git_value(resolved, ["rev-parse", "--short", "HEAD"]) if git_repo else "",
        "stack": stack,
        "found_files": found,
        "risks": risks,
    }


def profile_for_stack(stack_type: str) -> dict:
    stack_type = stack_type if stack_type in ALLOWED_TYPES else "unknown"
    source_roots = ["."]
    test_commands = []
    if stack_type in ("python", "mixed"):
        test_commands.extend(["python3 -m py_compile *.py", "python3 -m compileall ."])
    if stack_type in ("node", "mixed"):
        test_commands.extend(["npm test", "npm run lint", "npm run build"])
    if stack_type == "docs":
        source_roots = ["docs", "."]
    return {
        "safe_roots": ["."],
        "source_roots": source_roots,
        "test_commands": test_commands,
        "blocked_paths": list(DEFAULT_PROFILE["blocked_paths"]),
    }


def validate_test_command(command: str) -> dict:
    blocked = ("rm", "mv", "cp", "curl", "wget", "ssh", "scp", "docker", "sudo", "chmod", "chown")
    try:
        parts = shlex.split(command)
    except Exception:
        return {"command": command, "ok": False, "reason": "invalid_shell_syntax"}
    if not parts:
        return {"command": command, "ok": False, "reason": "empty_command"}
    lower = command.lower()
    for op in (";", "&&", "||", "|", ">", "<", "`", "$("):
        if op in command:
            return {"command": command, "ok": False, "reason": "blocked_operator"}
    if any(f" {b} " in f" {lower} " or lower.startswith(f"{b} ") for b in blocked):
        return {"command": command, "ok": False, "reason": "blocked_command"}
    if "git push" in lower or "git add ." in lower or "git reset" in lower or "git clean" in lower:
        return {"command": command, "ok": False, "reason": "blocked_git_mutation"}
    ok = False
    if parts[:2] == ["python3", "-m"] and len(parts) >= 3 and parts[2] in ("py_compile", "compileall"):
        ok = True
    elif parts[:2] == ["bash", "-n"] and len(parts) >= 3:
        ok = True
    elif parts == ["npm", "test"] or parts == ["npm", "run", "test"] or parts == ["npm", "run", "lint"] or parts == ["npm", "run", "build"]:
        ok = True
    elif parts == ["pnpm", "test"] or parts == ["pnpm", "lint"] or parts == ["pnpm", "build"]:
        ok = True
    elif parts == ["pnpm", "run", "test"] or parts == ["pnpm", "run", "lint"] or parts == ["pnpm", "run", "build"]:
        ok = True
    elif parts == ["yarn", "test"] or parts == ["yarn", "lint"] or parts == ["yarn", "build"]:
        ok = True
    return {"command": command, "ok": ok, "reason": "" if ok else "not_in_allowlist"}


def validate_profile(workspace_id: str | None = None) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "unknown_workspace"}
    root = Path(ws["resolved_path"])
    profile = ws.get("profile") or {}
    warnings = []
    source_roots = profile.get("source_roots", [])
    source_checks = []
    for src in source_roots:
        p = (root / src).resolve()
        exists = p.exists()
        source_checks.append({"path": src, "exists": exists})
        if not exists:
            warnings.append(f"source_root ausente: {src}")
    command_checks = [validate_test_command(str(cmd)) for cmd in profile.get("test_commands", [])]
    if not profile:
        warnings.append("profile ausente")
    if not source_roots:
        warnings.append("source_roots vazio")
    if any(not c["ok"] for c in command_checks):
        warnings.append("test_commands contem comando fora da allowlist")
    status = "valid" if not warnings else ("incomplete" if profile else "needs_attention")
    return {
        "ok": True,
        "workspace_id": ws["id"],
        "workspace_name": ws["name"],
        "profile_exists": bool(profile),
        "status": status,
        "safe_roots": profile.get("safe_roots", []),
        "source_roots": source_roots,
        "blocked_paths": profile.get("blocked_paths", []),
        "test_commands": profile.get("test_commands", []),
        "source_root_checks": source_checks,
        "test_command_checks": command_checks,
        "warnings": warnings,
        "stack": detect_stack(root) if root.is_dir() else {"primary": "unknown", "stacks": ["unknown"]},
    }


def _local_workspaces() -> list[dict]:
    if not WORKSPACES_CONFIG.exists():
        return []
    try:
        data = json.loads(WORKSPACES_CONFIG.read_text(encoding="utf-8"))
        return [w for w in data.get("workspaces", []) if isinstance(w, dict) and w.get("id") != "aiw"]
    except Exception:
        return []


def _write_local_config(active: str, workspaces: list[dict]) -> None:
    WORKSPACES_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": 1, "active": active or "aiw", "workspaces": workspaces}
    WORKSPACES_CONFIG.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def add_workspace(workspace_id: str, name: str, path: str, workspace_type: str = "unknown") -> dict:
    try:
        ws_id = normalize_workspace_id(workspace_id)
    except ValueError:
        return {"ok": False, "error": "invalid_workspace_id"}
    if ws_id == "aiw" or resolve_workspace(ws_id):
        return {"ok": False, "error": "duplicate_workspace_id"}
    validation = validate_workspace_path(path)
    if not validation.get("ok"):
        return {"ok": False, "error": "invalid_workspace_path", "validation": validation}
    resolved_path = validation["path"]
    for existing in load_workspaces_config()["workspaces"]:
        if Path(existing["path"]).expanduser().resolve() == Path(resolved_path):
            return {"ok": False, "error": "duplicate_workspace_path", "existing_id": existing["id"]}
    detected = validation["stack"]["primary"]
    ws_type = workspace_type if workspace_type in ALLOWED_TYPES else detected
    if ws_type == "unknown":
        ws_type = detected
    item = {
        "id": ws_id,
        "name": str(name or ws_id),
        "path": resolved_path,
        "type": ws_type,
        "profile": profile_for_stack(ws_type),
    }
    items = _local_workspaces()
    items.append(item)
    active = load_workspaces_config().get("active", "aiw")
    _write_local_config(active, items)
    return {"ok": True, "workspace": item, "validation": validation}


def remove_workspace(workspace_id: str) -> dict:
    try:
        ws_id = normalize_workspace_id(workspace_id)
    except ValueError:
        return {"ok": False, "error": "invalid_workspace_id"}
    if ws_id == "aiw":
        return {"ok": False, "error": "cannot_remove_default_workspace"}
    items = _local_workspaces()
    kept = [w for w in items if w.get("id") != ws_id]
    if len(kept) == len(items):
        return {"ok": False, "error": "unknown_workspace"}
    active = load_workspaces_config().get("active", "aiw")
    if active == ws_id:
        active = "aiw"
    _write_local_config(active, kept)
    return {"ok": True, "removed": ws_id, "artifacts_removed": False}
