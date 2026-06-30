import json
import re
from pathlib import Path


AIW_ROOT = Path(__file__).resolve().parents[1]
WORKSPACES_CONFIG = AIW_ROOT / ".aiw" / "workspaces.json"
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")

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
