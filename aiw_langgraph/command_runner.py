"""Safe command runner for LangGraph engineering loop.

Provides a thin wrapper around subprocess.run that enforces an allowlist of
permitted commands and captures execution metadata.
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Mapping, Sequence

# Define simple allowlist – commands that are considered safe for this POC.
# Each entry is the executable name (without arguments). The runner will only
# allow the first token of the command to match an entry.
ALLOWLIST: List[str] = [
    "python",
    "bash",
    "sh",
]

# Disallowed patterns – used to block dangerous operations even if the command
# name is allowed (e.g., "python -c 'import os; os.system("rm -rf /")'").
DISALLOWED_SUBSTRINGS: List[str] = [
    "rm ",
    "sudo", 
    "git push --force",
    "curl ",
    "wget ",
    "ssh ",
    "scp ",
]

@dataclass
class CommandResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration: float

def _is_allowed(command: str) -> bool:
    # Split on whitespace to get the executable.
    parts = command.strip().split()
    if not parts:
        return False
    exe = Path(parts[0]).name
    if exe not in ALLOWLIST:
        return False
    # Check disallowed substrings.
    for bad in DISALLOWED_SUBSTRINGS:
        if bad in command:
            return False
    return True

def run_command(command: str, cwd: str | None = None) -> CommandResult:
    """Execute *command* if it passes the allowlist.

    Returns a :class:`CommandResult` with captured stdout, stderr, exit code and
    execution time.
    """
    if not _is_allowed(command):
        raise ValueError(f"Command not allowed by safety policy: {command}")
    start = time.time()
    completed = subprocess.run(
        command,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
        executable="/bin/bash",
    )
    duration = time.time() - start
    return CommandResult(
        command=command,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        duration=duration,
    )
