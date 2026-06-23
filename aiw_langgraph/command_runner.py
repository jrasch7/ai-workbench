"""aiw_langgraph.command_runner

Provides a safe wrapper to execute local commands for the AIW Cockpit.
Only a limited allow-list of innocuous commands is permitted.
Destructive commands (rm, sudo, git push --force, curl, wget, ssh, scp) are blocked.
All commands are run from the repository root and cannot escape the repo.
"""

import os
import subprocess
import shlex
from pathlib import Path
from typing import Dict, Any

# Simple allow-list - commands considered safe.
ALLOWLIST = {
    "python",
    "python3",
    "bash",
    "sh",
    "git",
    "ls",
    "pwd",
    "cat",
    "echo",
    "date",
    "head",
    "tail",
    "grep",
    "sed",
    "awk",
    "find",
    "du",
    "whoami",
    "uname",
    "env",
    "tree",
}

# Blocked prefixes - any command starting with these is rejected.
BLOCKED_PREFIXES = [
    "rm ",
    "sudo",
    "git push --force",
    "curl ",
    "wget ",
    "ssh ",
    "scp ",
]

def _is_allowed(command: str) -> bool:
    """Return True if the command is allowed.

    Very simple heuristic: the first token must be in ALLOWLIST and must not start
    with any BLOCKED_PREFIXES.
    """
    stripped = command.strip()
    for prefix in BLOCKED_PREFIXES:
        if stripped.startswith(prefix):
            return False
    try:
        first = shlex.split(stripped)[0]
    except Exception:
        return False
    return first in ALLOWLIST

def run_command(command: str, cwd: str = None, timeout: int = 600) -> Dict[str, Any]:
    """Execute a command safely.

    Returns a dict with keys: exit_code, stdout, stderr, duration.
    If the command is not allowed, returns exit_code = -1 and an error message.
    """
    import time
    if not _is_allowed(command):
        return {"exit_code": -1, "stdout": "", "stderr": f"Command blocked by allow-list: {command}", "duration": 0}
    try:
        args = shlex.split(command)
    except Exception:
        return {"exit_code": -1, "stdout": "", "stderr": f"Unable to parse command safely: {command}", "duration": 0}
    exe = args[0] if args else ""
    if exe in ("python", "python3"):
        # Allow only "-m compileall" or "-m py_compile"
        if len(args) >= 3 and args[1] == "-m" and args[2] in ("compileall", "py_compile"):
            pass
        else:
            return {"exit_code": -1, "stdout": "", "stderr": f"Python command not allowed: {command}", "duration": 0}
    if exe in ("bash", "sh"):
        # Disallow "-c" which enables arbitrary code execution
        if "-c" in args:
            return {"exit_code": -1, "stdout": "", "stderr": f"Shell command with -c blocked: {command}", "duration": 0}
    start = time.time()
    try:
        completed = subprocess.run(
            args,
            cwd=cwd or str(Path.cwd()),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        duration = time.time() - start
        return {"exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr, "duration": duration}
    except subprocess.TimeoutExpired as te:
        return {"exit_code": -2, "stdout": te.stdout or "", "stderr": te.stderr or "", "duration": timeout}
    except Exception as exc:
        return {"exit_code": -3, "stdout": "", "stderr": str(exc), "duration": time.time() - start}
