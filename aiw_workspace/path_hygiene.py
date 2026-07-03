from pathlib import Path

from .profiles import AIW_ROOT


def safe_display_path(path, repo_root: Path | None = None) -> str:
    if path is None:
        return None
    text = str(path)
    if not text:
        return text

    try:
        candidate = Path(text).expanduser()
    except Exception:
        return text

    root = (repo_root or AIW_ROOT).resolve()
    if candidate.is_absolute():
        try:
            rel = candidate.resolve().relative_to(root)
            return rel.as_posix()
        except Exception:
            return candidate.name or "[external-path]"

    normalized = text.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def sanitize_artifact_paths_for_display(value, repo_root: Path | None = None):
    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            if _looks_like_path_key(key):
                sanitized[key] = safe_display_path(item, repo_root=repo_root)
            else:
                sanitized[key] = sanitize_artifact_paths_for_display(item, repo_root=repo_root)
        return sanitized
    if isinstance(value, list):
        return [sanitize_artifact_paths_for_display(item, repo_root=repo_root) for item in value]
    return value


def _looks_like_path_key(key) -> bool:
    name = str(key).lower()
    return name in {"artifact", "run_dir"} or name.endswith("_path") or name.endswith("_dir") or name.endswith("_json") or name.endswith("_md")
