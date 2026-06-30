import os
import argparse
import json
import subprocess
import time
import shutil
import uuid
import difflib
from pathlib import Path
from .policy import validate_path, validate_write_path, validate_project_patch_path, validate_shell_command, get_root, get_aiw_root


def _workspace_id() -> str:
    value = os.environ.get("AIW_WORKSPACE_ID", "aiw").strip() or "aiw"
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in value)[:80] or "aiw"


def _patches_dir() -> Path:
    return get_aiw_root() / ".aiw" / "workspaces" / _workspace_id() / "patches"


def _legacy_patches_dir() -> Path:
    return get_aiw_root() / ".aiw" / "patches"


def _patch_file_for_read(patch_id: str) -> Path:
    scoped = _patches_dir() / f"{patch_id}.json"
    if scoped.exists():
        return scoped
    return _legacy_patches_dir() / f"{patch_id}.json"


def directory_list(path: str = ".", max_depth: int = 2, limit: int = 100):
    try:
        resolved_path = validate_path(path)
        if not resolved_path.is_dir():
            return {"ok": False, "tool": "directory_list", "error": "Not a directory"}

        ignored = {".git", ".venv", "node_modules", "vendor", "__pycache__"}

        entries = []
        start_depth = len(resolved_path.parts)

        for root, dirs, files in os.walk(resolved_path):
            current_depth = len(Path(root).parts) - start_depth
            if current_depth >= max_depth:
                dirs.clear() # don't go deeper
                continue

            # Filter ignored dirs
            dirs[:] = [d for d in dirs if d not in ignored]

            for d in dirs:
                if len(entries) >= limit:
                    break
                rel = str(Path(root) / d)
                rel = rel.replace(str(resolved_path), "").lstrip(os.sep)
                entries.append({"name": rel or d, "type": "dir"})

            if len(entries) >= limit:
                break

            for f in files:
                if len(entries) >= limit:
                    break
                rel = str(Path(root) / f)
                rel = rel.replace(str(resolved_path), "").lstrip(os.sep)
                entries.append({"name": rel or f, "type": "file"})

            if len(entries) >= limit:
                break

        return {"ok": True, "tool": "directory_list", "entries": entries[:limit]}
    except Exception as e:
        return {"ok": False, "tool": "directory_list", "error": str(e)}

def file_read(path: str, max_bytes: int = 8000):
    try:
        resolved_path = validate_path(path)
        if not resolved_path.is_file():
            return {"ok": False, "tool": "file_read", "error": "Not a file or does not exist"}

        stat = resolved_path.stat()
        truncated = stat.st_size > max_bytes

        with open(resolved_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_bytes)

        return {
            "ok": True,
            "tool": "file_read",
            "content": content,
            "truncated": truncated
        }
    except Exception as e:
        return {"ok": False, "tool": "file_read", "error": str(e)}

def shell_exec(command: str, timeout: int = 20):
    try:
        if timeout > 30:
            timeout = 30

        parts = validate_shell_command(command)

        result = subprocess.run(
            parts,
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(validate_path("."))
        )

        return {
            "ok": True,
            "tool": "shell_exec",
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired as e:
        return {"ok": False, "tool": "shell_exec", "error": "Timeout expired", "stdout": e.stdout.decode('utf-8', 'replace') if e.stdout else ""}
    except Exception as e:
        return {"ok": False, "tool": "shell_exec", "error": str(e)}

def _create_backup(resolved_path: Path) -> str:
    if not resolved_path.exists():
        return None
    root = get_root()
    rel = resolved_path.relative_to(root)
    timestamp = time.strftime("%Y%m%dT%H%M%SZ")
    backup_path = get_aiw_root() / ".aiw" / "backups" / _workspace_id() / timestamp / rel
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(resolved_path, backup_path)
    return str(backup_path.relative_to(get_aiw_root()))

def file_write(path: str, content: str, overwrite: bool = False):
    try:
        resolved_path = validate_write_path(path)

        exists = resolved_path.exists()
        if exists and not overwrite:
            return {"ok": False, "tool": "file_write", "error": "Arquivo já existe. Defina overwrite=true se desejar sobrescrever."}

        backup_path = _create_backup(resolved_path) if exists else None

        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_path.write_text(content, encoding="utf-8")

        return {
            "ok": True,
            "tool": "file_write",
            "path": str(resolved_path.relative_to(get_root())),
            "bytes_written": len(content.encode("utf-8")),
            "created": not exists,
            "overwritten": exists,
            "backup_path": backup_path
        }
    except Exception as e:
        return {"ok": False, "tool": "file_write", "error": str(e)}

def file_patch(path: str, old_text: str, new_text: str, expected_replacements: int = 1):
    try:
        resolved_path = validate_write_path(path)

        if not resolved_path.exists():
            return {"ok": False, "tool": "file_patch", "error": "Arquivo não existe."}

        content = resolved_path.read_text(encoding="utf-8")
        occurrences = content.count(old_text)

        if occurrences != expected_replacements:
            return {
                "ok": False,
                "tool": "file_patch",
                "error": f"Encontradas {occurrences} ocorrências de old_text, mas esperado {expected_replacements}. Substituição abortada."
            }

        backup_path = _create_backup(resolved_path)
        new_content = content.replace(old_text, new_text)
        resolved_path.write_text(new_content, encoding="utf-8")

        return {
            "ok": True,
            "tool": "file_patch",
            "path": str(resolved_path.relative_to(get_root())),
            "replacements": occurrences,
            "backup_path": backup_path,
            "bytes_written": len(new_content.encode("utf-8"))
        }
    except Exception as e:
        return {"ok": False, "tool": "file_patch", "error": str(e)}

def project_patch_preview(path: str, old_text: str, new_text: str, expected_replacements: int = 1, reason: str = ""):
    try:
        resolved_path = validate_project_patch_path(path)

        if not resolved_path.exists():
            return {"ok": False, "tool": "project_patch_preview", "error": "Arquivo não existe."}

        content = resolved_path.read_text(encoding="utf-8")
        occurrences = content.count(old_text)

        if occurrences != expected_replacements:
            return {
                "ok": False,
                "tool": "project_patch_preview",
                "error": f"Encontradas {occurrences} ocorrências de old_text, mas esperado {expected_replacements}. Substituição abortada."
            }

        new_content = content.replace(old_text, new_text)

        # Generate unified diff
        diff_lines = list(difflib.unified_diff(
            content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=path,
            tofile=path,
            n=3
        ))
        diff_text = "".join(diff_lines)

        patch_id = time.strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:8]
        patches_dir = _patches_dir()
        patches_dir.mkdir(parents=True, exist_ok=True)

        patch_data = {
            "patch_id": patch_id,
            "path": str(resolved_path.relative_to(get_root())),
            "old_text": old_text,
            "new_text": new_text,
            "reason": reason,
            "diff": diff_text,
            "replacements": occurrences,
            "status": "preview",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "workspace_id": _workspace_id(),
            "artifact_scope": "scoped"
        }

        patch_file = patches_dir / f"{patch_id}.json"
        patch_file.write_text(json.dumps(patch_data, indent=2, ensure_ascii=False), encoding="utf-8")

        return {
            "ok": True,
            "tool": "project_patch_preview",
            "patch_id": patch_id,
            "path": patch_data["path"],
            "replacements": occurrences,
            "diff": diff_text,
            "status": "preview"
        }
    except Exception as e:
        return {"ok": False, "tool": "project_patch_preview", "error": str(e)}

def project_patch_apply(patch_id: str):
    try:
        if _workspace_id() != "aiw":
            return {"ok": False, "tool": "project_patch_apply", "error": "Auto-apply bloqueado para workspace externo."}
        patch_file = _patch_file_for_read(patch_id)
        if not patch_file.exists():
            return {"ok": False, "tool": "project_patch_apply", "error": "Patch não encontrado."}

        patch_data = json.loads(patch_file.read_text(encoding="utf-8"))
        if patch_data.get("status") != "preview":
            return {"ok": False, "tool": "project_patch_apply", "error": f"Patch status inválido: {patch_data.get('status')}"}

        path_str = patch_data["path"]
        resolved_path = validate_project_patch_path(path_str)

        content = resolved_path.read_text(encoding="utf-8")
        old_text = patch_data["old_text"]
        new_text = patch_data["new_text"]

        occurrences = content.count(old_text)
        if occurrences != patch_data["replacements"]:
            return {"ok": False, "tool": "project_patch_apply", "error": "Conteúdo original mudou. Rollback virtual de patch abortado."}

        backup_path = _create_backup(resolved_path)
        new_content = content.replace(old_text, new_text)
        resolved_path.write_text(new_content, encoding="utf-8")

        patch_data["status"] = "applied"
        patch_data["backup_path"] = backup_path
        patch_data["applied_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        patch_file.write_text(json.dumps(patch_data, indent=2, ensure_ascii=False), encoding="utf-8")

        return {
            "ok": True,
            "tool": "project_patch_apply",
            "patch_id": patch_id,
            "path": path_str,
            "backup_path": backup_path,
            "status": "applied"
        }
    except Exception as e:
        return {"ok": False, "tool": "project_patch_apply", "error": str(e)}

def project_patch_rollback(patch_id: str):
    try:
        patch_file = _patch_file_for_read(patch_id)
        if not patch_file.exists():
            return {"ok": False, "tool": "project_patch_rollback", "error": "Patch não encontrado."}

        patch_data = json.loads(patch_file.read_text(encoding="utf-8"))
        if patch_data.get("status") != "applied":
            return {"ok": False, "tool": "project_patch_rollback", "error": f"Patch não está aplicado. Status atual: {patch_data.get('status')}"}

        path_str = patch_data["path"]
        resolved_path = validate_project_patch_path(path_str)

        backup_str = patch_data.get("backup_path")
        if not backup_str:
            return {"ok": False, "tool": "project_patch_rollback", "error": "Nenhum backup encontrado para este patch."}

        backup_path = get_aiw_root() / backup_str
        if not backup_path.exists():
            return {"ok": False, "tool": "project_patch_rollback", "error": "Arquivo de backup não encontrado fisicamente."}

        shutil.copy2(backup_path, resolved_path)

        patch_data["status"] = "rolled_back"
        patch_data["rolled_back_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        patch_file.write_text(json.dumps(patch_data, indent=2, ensure_ascii=False), encoding="utf-8")

        return {
            "ok": True,
            "tool": "project_patch_rollback",
            "patch_id": patch_id,
            "path": path_str,
            "status": "rolled_back"
        }
    except Exception as e:
        return {"ok": False, "tool": "project_patch_rollback", "error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", choices=[
        "directory_list", "file_read", "shell_exec", "file_write", "file_patch",
        "project_patch_preview", "project_patch_apply", "project_patch_rollback"
    ])
    parser.add_argument("--path", type=str)
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--max-bytes", type=int, default=8000)
    parser.add_argument("--command", type=str)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--content", type=str)

    # Handle boolean flag appropriately
    parser.add_argument("--overwrite", type=str, default="false")

    parser.add_argument("--old-text", type=str)
    parser.add_argument("--new-text", type=str)
    parser.add_argument("--expected-replacements", type=int, default=1)
    parser.add_argument("--reason", type=str, default="")
    parser.add_argument("--patch-id", type=str)

    args = parser.parse_args()

    if args.tool == "directory_list":
        print(json.dumps(directory_list(args.path or ".", args.max_depth, args.limit), indent=2))
    elif args.tool == "file_read":
        print(json.dumps(file_read(args.path, args.max_bytes), indent=2))
    elif args.tool == "shell_exec":
        print(json.dumps(shell_exec(args.command, args.timeout), indent=2))
    elif args.tool == "file_write":
        overwrite_bool = args.overwrite.lower() in ("true", "1", "yes")
        print(json.dumps(file_write(args.path, args.content, overwrite_bool), indent=2))
    elif args.tool == "file_patch":
        print(json.dumps(file_patch(args.path, args.old_text, args.new_text, args.expected_replacements), indent=2))
    elif args.tool == "project_patch_preview":
        print(json.dumps(project_patch_preview(args.path, args.old_text, args.new_text, args.expected_replacements, args.reason), indent=2))
    elif args.tool == "project_patch_apply":
        print(json.dumps(project_patch_apply(args.patch_id), indent=2))
    elif args.tool == "project_patch_rollback":
        print(json.dumps(project_patch_rollback(args.patch_id), indent=2))
