import os
import argparse
import json
import subprocess
import time
import shutil
from pathlib import Path
from .policy import validate_path, validate_write_path, validate_shell_command, get_root

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
    backup_path = root / ".aiw" / "backups" / timestamp / rel
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(resolved_path, backup_path)
    return str(backup_path.relative_to(root))

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", choices=["directory_list", "file_read", "shell_exec", "file_write", "file_patch"])
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
