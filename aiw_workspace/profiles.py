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
    "source_roots": ["aiw_runtime", "aiw_context", "aiw_workspace", "scripts", "docs"],
    "test_commands": [
        "python3 -m py_compile aiw_runtime/*.py",
        "python3 -m py_compile aiw_context/*.py",
        "python3 -m py_compile aiw_workspace/*.py",
        "bash -n scripts/aiw-cockpit",
        "bash -n scripts/aiw-runner-agent",
        "bash -n scripts/aiw-tool-smoke",
        "./scripts/aiw-tool-smoke",
    ],
    "validation_groups": [
        {
            "name": "Syntax",
            "kind": "syntax",
            "priority": 10,
            "commands": [
                "python3 -m py_compile aiw_runtime/*.py",
                "python3 -m py_compile aiw_context/*.py",
                "python3 -m py_compile aiw_workspace/*.py",
                "bash -n scripts/aiw-cockpit",
                "bash -n scripts/aiw-runner-agent",
                "bash -n scripts/aiw-tool-smoke",
            ],
        },
        {
            "name": "Tool Runtime Smoke",
            "kind": "smoke",
            "priority": 30,
            "commands": ["./scripts/aiw-tool-smoke"],
        },
    ],
    "test_mappings": [
        {
            "name": "Runtime Python",
            "patterns": ["aiw_runtime/**/*.py", "aiw_runtime/*.py"],
            "commands": ["python3 -m py_compile aiw_runtime/*.py"],
        },
        {
            "name": "Context Python",
            "patterns": ["aiw_context/**/*.py", "aiw_context/*.py"],
            "commands": ["python3 -m py_compile aiw_context/*.py"],
        },
        {
            "name": "Workspace Python",
            "patterns": ["aiw_workspace/**/*.py", "aiw_workspace/*.py"],
            "commands": ["python3 -m py_compile aiw_workspace/*.py"],
        },
        {
            "name": "Cockpit Script",
            "patterns": ["scripts/aiw-cockpit"],
            "commands": ["bash -n scripts/aiw-cockpit"],
        },
        {
            "name": "Runner Script",
            "patterns": ["scripts/aiw-runner-agent"],
            "commands": ["bash -n scripts/aiw-runner-agent"],
        },
        {
            "name": "Tool Smoke Script",
            "patterns": ["scripts/aiw-tool-smoke"],
            "commands": ["bash -n scripts/aiw-tool-smoke"],
        },
        {
            "name": "Documentation",
            "patterns": ["docs/**/*.md", "docs/*.md", "README.md"],
            "commands": [],
        },
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
        if isinstance(profile.get("test_mappings"), list):
            mappings = []
            for item in profile["test_mappings"]:
                if not isinstance(item, dict):
                    continue
                mappings.append({
                    "name": str(item.get("name", "")),
                    "patterns": [str(v) for v in item.get("patterns", [])] if isinstance(item.get("patterns"), list) else [],
                    "commands": [str(v) for v in item.get("commands", [])] if isinstance(item.get("commands"), list) else [],
                })
            merged["test_mappings"] = mappings
        elif "test_mappings" not in profile:
            merged["test_mappings"] = []
        if isinstance(profile.get("validation_groups"), list):
            groups = []
            for item in profile["validation_groups"]:
                if not isinstance(item, dict):
                    continue
                groups.append({
                    "name": str(item.get("name", "")),
                    "kind": str(item.get("kind", "")),
                    "priority": item.get("priority", 100),
                    "commands": [str(v) for v in item.get("commands", [])] if isinstance(item.get("commands"), list) else [],
                })
            merged["validation_groups"] = groups
        elif "validation_groups" not in profile:
            merged["validation_groups"] = []

        if isinstance(profile.get("coverage_reports"), list):
            reports = []
            for item in profile["coverage_reports"]:
                if not isinstance(item, dict):
                    continue
                parsed_item = {
                    "name": str(item.get("name", "")),
                    "format": str(item.get("format", "unknown")),
                    "path": str(item.get("path", "")),
                }
                if "threshold" in item:
                    try:
                        parsed_item["threshold"] = float(item["threshold"])
                    except Exception:
                        parsed_item["threshold"] = item["threshold"]
                reports.append(parsed_item)
            merged["coverage_reports"] = reports
        elif "coverage_reports" not in profile:
            merged["coverage_reports"] = []

        if isinstance(profile.get("coverage"), dict):
            merged["coverage"] = profile["coverage"]
        elif "coverage" not in profile:
            merged["coverage"] = {}

        if isinstance(profile.get("test_result_reports"), list):
            tr_reports = []
            for item in profile["test_result_reports"]:
                if not isinstance(item, dict):
                    continue
                tr_reports.append({
                    "name": str(item.get("name", "")),
                    "format": str(item.get("format", "unknown")),
                    "path": str(item.get("path", "")),
                })
            merged["test_result_reports"] = tr_reports
        elif "test_result_reports" not in profile:
            merged["test_result_reports"] = []
            
        if isinstance(profile.get("llm_execution"), dict):
            llm_config = profile["llm_execution"]
            merged["llm_execution"] = {
                "enabled": bool(llm_config.get("enabled", False)),
                "allowed_models": [str(x) for x in llm_config.get("allowed_models", []) if isinstance(x, str)],
                "default_model": str(llm_config.get("default_model", "")),
                "timeout_seconds": max(30, min(1800, int(llm_config.get("timeout_seconds", 300)))),
                "max_stdout_chars": max(1000, min(100000, int(llm_config.get("max_stdout_chars", 12000)))),
                "max_stderr_chars": max(1000, min(100000, int(llm_config.get("max_stderr_chars", 12000)))),
            }
        elif "llm_execution" not in profile:
            merged["llm_execution"] = {
                "enabled": False,
                "allowed_models": [],
                "default_model": "",
                "timeout_seconds": 300,
                "max_stdout_chars": 12000,
                "max_stderr_chars": 12000
            }

        if isinstance(profile.get("external_workers"), dict):
            ext_config = profile["external_workers"]
            workers = []
            for w in ext_config.get("workers", []):
                if isinstance(w, dict):
                    workers.append({
                        "name": str(w.get("name", "")),
                        "target": str(w.get("target", "")),
                        "mode": str(w.get("mode", "disabled")),
                        "enabled": bool(w.get("enabled", False)),
                        "requires_confirm": bool(w.get("requires_confirm", True)),
                        "allowed_actions": [str(x) for x in w.get("allowed_actions", []) if isinstance(x, str)],
                        "blocked_actions": [str(x) for x in w.get("blocked_actions", []) if isinstance(x, str)],
                    })
            merged["external_workers"] = {
                "enabled": bool(ext_config.get("enabled", False)),
                "allow_background": bool(ext_config.get("allow_background", False)),
                "allow_ui_execution": bool(ext_config.get("allow_ui_execution", False)),
                "workers": workers
            }
        elif "external_workers" not in profile:
            merged["external_workers"] = {
                "enabled": False,
                "allow_background": False,
                "allow_ui_execution": False,
                "workers": []
            }

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
        "test_mappings": [],
        "validation_groups": [],
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
    elif parts == ["./scripts/aiw-tool-smoke"]:
        ok = True
    return {"command": command, "ok": ok, "reason": "" if ok else "not_in_allowlist"}


def _normalize_rel_pattern(pattern: str) -> tuple[str, str]:
    value = str(pattern or "").strip().replace("\\", "/")
    if not value:
        return "", "empty_pattern"
    if value.startswith("/") or ".." in Path(value).parts:
        return value, "unsafe_pattern"
    return value, ""


def _blocked_pattern(pattern: str, blocked_paths: list[str]) -> bool:
    parts = Path(pattern).parts
    for blocked in blocked_paths:
        blocked = str(blocked).replace("\\", "/").strip()
        if not blocked:
            continue
        if blocked.startswith(".env") and (pattern.startswith(".env") or any(part.startswith(".env") for part in parts)):
            return True
        if blocked in parts or pattern == blocked or pattern.startswith(blocked.rstrip("/") + "/"):
            return True
    return False


def validate_test_mappings(root: Path, profile: dict) -> tuple[list[dict], list[str], list[str], list[str]]:
    warnings = []
    errors = []
    commands = [str(cmd) for cmd in profile.get("test_commands", [])]
    blocked_paths = [str(p) for p in profile.get("blocked_paths", DEFAULT_PROFILE["blocked_paths"])]
    mappings = []

    for raw_mapping in profile.get("test_mappings", []) or []:
        if not isinstance(raw_mapping, dict):
            errors.append("mapping invalido: esperado objeto")
            continue
        name = str(raw_mapping.get("name") or "unnamed")
        raw_patterns = raw_mapping.get("patterns", [])
        raw_commands = raw_mapping.get("commands", [])
        patterns = [str(p) for p in raw_patterns] if isinstance(raw_patterns, list) else []
        mapping_commands = [str(c) for c in raw_commands] if isinstance(raw_commands, list) else []
        pattern_checks = []
        command_checks = []
        matched_files = []
        mapping_errors = []
        mapping_warnings = []

        if not patterns:
            mapping_errors.append("patterns vazio")

        for pattern in patterns:
            normalized, error = _normalize_rel_pattern(pattern)
            blocked = bool(normalized and _blocked_pattern(normalized, blocked_paths))
            if blocked:
                error = "blocked_pattern"
            matches = []
            if normalized and not error and root.is_dir():
                try:
                    matches = sorted(
                        str(path.relative_to(root)).replace("\\", "/")
                        for path in root.glob(normalized)
                        if path.is_file() and not _blocked_pattern(str(path.relative_to(root)).replace("\\", "/"), blocked_paths)
                    )[:25]
                except Exception:
                    matches = []
            if error:
                mapping_errors.append(f"{normalized or pattern}: {error}")
            matched_files.extend(matches)
            pattern_checks.append({"pattern": normalized or pattern, "ok": not error, "error": error, "matched_files": matches})

        for command in mapping_commands:
            in_profile = command in commands
            validation = validate_test_command(command)
            if not in_profile:
                mapping_errors.append(f"command_not_in_profile: {command}")
            if not validation.get("ok"):
                mapping_errors.append(f"command_blocked: {command}: {validation.get('reason')}")
            command_checks.append({
                "command": command,
                "in_profile": in_profile,
                "ok": in_profile and bool(validation.get("ok")),
                "reason": validation.get("reason", ""),
            })

        if not matched_files:
            mapping_warnings.append("mapping sem arquivos correspondentes")

        ok = not mapping_errors
        mappings.append({
            "name": name,
            "patterns": [check["pattern"] for check in pattern_checks],
            "commands": mapping_commands,
            "ok": ok,
            "status": "valid" if ok else "invalid",
            "pattern_checks": pattern_checks,
            "command_checks": command_checks,
            "matched_files": sorted(set(matched_files)),
            "warnings": mapping_warnings,
            "errors": mapping_errors,
        })
        warnings.extend([f"{name}: {w}" for w in mapping_warnings])
        errors.extend([f"{name}: {e}" for e in mapping_errors])

    source_roots_without_mapping = []
    for source_root in profile.get("source_roots", []):
        source_root = str(source_root).strip().replace("\\", "/").rstrip("/")
        if not source_root:
            continue
        mapped = any(
            pattern == source_root or pattern.startswith(source_root + "/") or pattern.startswith(source_root + "**")
            for mapping in mappings
            for pattern in mapping.get("patterns", [])
        )
        if not mapped:
            source_roots_without_mapping.append(source_root)
            warnings.append(f"source_root sem mapping: {source_root}")

    return mappings, warnings, errors, source_roots_without_mapping


def validate_validation_groups(profile: dict) -> tuple[list[dict], list[str], list[str]]:
    allowed_kinds = {"syntax", "targeted", "smoke", "build", "docs", "full"}
    warnings = []
    errors = []
    commands = [str(cmd) for cmd in profile.get("test_commands", [])]
    groups = []

    for raw_group in profile.get("validation_groups", []) or []:
        if not isinstance(raw_group, dict):
            errors.append("validation_group invalido: esperado objeto")
            continue
        name = str(raw_group.get("name") or "unnamed")
        kind = str(raw_group.get("kind") or "targeted")
        raw_priority = raw_group.get("priority", 100)
        group_commands = [str(c) for c in raw_group.get("commands", [])] if isinstance(raw_group.get("commands"), list) else []
        group_errors = []
        group_warnings = []

        try:
            priority = int(raw_priority)
        except Exception:
            priority = 100
            group_errors.append("priority_invalida")
        if kind not in allowed_kinds:
            group_errors.append(f"kind_desconhecido: {kind}")
        if not group_commands:
            group_warnings.append("grupo sem comandos")

        command_checks = []
        for command in group_commands:
            in_profile = command in commands
            validation = validate_test_command(command)
            if not in_profile:
                group_errors.append(f"command_not_in_profile: {command}")
            if not validation.get("ok"):
                group_errors.append(f"command_blocked: {command}: {validation.get('reason')}")
            command_checks.append({
                "command": command,
                "in_profile": in_profile,
                "ok": in_profile and bool(validation.get("ok")),
                "reason": validation.get("reason", ""),
            })

        ok = not group_errors
        groups.append({
            "name": name,
            "kind": kind,
            "priority": priority,
            "commands": group_commands,
            "ok": ok,
            "status": "valid" if ok else "invalid",
            "command_checks": command_checks,
            "warnings": group_warnings,
            "errors": group_errors,
        })
        warnings.extend([f"{name}: {w}" for w in group_warnings])
        errors.extend([f"{name}: {e}" for e in group_errors])

    groups.sort(key=lambda group: (group.get("priority", 100), group.get("name", "")))
    return groups, warnings, errors


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
    test_mappings, mapping_warnings, mapping_errors, source_roots_without_mapping = validate_test_mappings(root, profile)
    warnings.extend(mapping_warnings)
    if mapping_errors:
        warnings.append("test_mappings contem entradas invalidas")
    validation_groups, group_warnings, group_errors = validate_validation_groups(profile)
    warnings.extend(group_warnings)
    if group_errors:
        warnings.append("validation_groups contem entradas invalidas")

    coverage_reports = profile.get("coverage_reports", [])
    coverage_checks = []
    
    test_result_reports = profile.get("test_result_reports", [])
    test_result_checks = []

    global_cov = profile.get("coverage", {})
    if not isinstance(global_cov, dict):
        warnings.append("coverage configuracao invalida")
    else:
        for key in ["default_threshold", "changed_file_threshold"]:
            if key in global_cov:
                try:
                    val = float(global_cov[key])
                    if not (0.0 <= val <= 1.0):
                        warnings.append(f"coverage.{key} fora do range 0-1: {val}")
                except Exception:
                    warnings.append(f"coverage.{key} invalido: esperado float 0-1")

    for report in coverage_reports:
        r_path = report.get("path", "")
        name = report.get("name", "")
        threshold = report.get("threshold")
        if threshold is not None:
            try:
                val = float(threshold)
                if not (0.0 <= val <= 1.0):
                    warnings.append(f"coverage_report '{name}' threshold fora do range 0-1: {val}")
            except Exception:
                warnings.append(f"coverage_report '{name}' threshold invalido: {threshold}")
        normalized, error = _normalize_rel_pattern(r_path)
        blocked = bool(normalized and _blocked_pattern(normalized, profile.get("blocked_paths", [])))
        if blocked:
            error = "blocked_pattern"
        exists = False
        if normalized and not error and root.is_dir():
            p = (root / normalized).resolve()
            try:
                if str(p).startswith(str(root)):
                    exists = p.is_file()
                else:
                    error = "unsafe_pattern"
            except Exception:
                error = "unsafe_pattern"
        if error:
            warnings.append(f"coverage_report '{name}' path invalido: {error}")
        elif not exists:
            warnings.append(f"coverage_report '{name}' arquivo ausente: {normalized}")
        coverage_checks.append({
            "name": name,
            "path": normalized or r_path,
            "format": report.get("format", "unknown"),
            "threshold": threshold,
            "ok": not error,
            "error": error,
            "exists": exists
        })

    for report in test_result_reports:
        r_path = report.get("path", "")
        name = report.get("name", "")
        normalized, error = _normalize_rel_pattern(r_path)
        blocked = bool(normalized and _blocked_pattern(normalized, profile.get("blocked_paths", [])))
        if blocked:
            error = "blocked_pattern"
        exists = False
        if normalized and not error and root.is_dir():
            p = (root / normalized).resolve()
            try:
                if str(p).startswith(str(root)):
                    exists = p.is_file()
                else:
                    error = "unsafe_pattern"
            except Exception:
                error = "unsafe_pattern"
        if error:
            warnings.append(f"test_result_report '{name}' path invalido: {error}")
        elif not exists:
            warnings.append(f"test_result_report '{name}' arquivo ausente: {normalized}")
        test_result_checks.append({
            "name": name,
            "path": normalized or r_path,
            "format": report.get("format", "unknown"),
            "ok": not error,
            "error": error,
            "exists": exists
        })

    status = "valid" if not warnings and not mapping_errors and not group_errors else ("incomplete" if profile else "needs_attention")
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
        "test_mappings": test_mappings,
        "test_mapping_count": len(test_mappings),
        "valid_test_mapping_count": len([m for m in test_mappings if m.get("ok")]),
        "test_mapping_errors": mapping_errors,
        "source_roots_without_mapping": source_roots_without_mapping,
        "validation_groups": validation_groups,
        "validation_group_count": len(validation_groups),
        "valid_validation_group_count": len([g for g in validation_groups if g.get("ok")]),
        "validation_group_errors": group_errors,
        "source_root_checks": source_checks,
        "test_command_checks": command_checks,
        "coverage": profile.get("coverage", {}),
        "coverage_reports": coverage_reports,
        "coverage_report_checks": coverage_checks,
        "test_result_reports": test_result_reports,
        "test_result_report_checks": test_result_checks,
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
