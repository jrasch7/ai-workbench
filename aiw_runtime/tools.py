import os
import argparse
import json
import subprocess
from pathlib import Path
from .policy import validate_path, validate_shell_command

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", choices=["directory_list", "file_read", "shell_exec"])
    parser.add_argument("--path", type=str)
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--max-bytes", type=int, default=8000)
    parser.add_argument("--command", type=str)
    parser.add_argument("--timeout", type=int, default=20)
    
    args = parser.parse_args()
    
    if args.tool == "directory_list":
        print(json.dumps(directory_list(args.path or ".", args.max_depth, args.limit), indent=2))
    elif args.tool == "file_read":
        print(json.dumps(file_read(args.path, args.max_bytes), indent=2))
    elif args.tool == "shell_exec":
        print(json.dumps(shell_exec(args.command, args.timeout), indent=2))
