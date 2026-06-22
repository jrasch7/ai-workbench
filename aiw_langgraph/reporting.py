"""Reporting utilities for LangGraph engineering loop.

Generates a markdown report summarizing execution details, including
branch information, timestamps, commands, validations, success flag, errors,
and suggested next steps.
"""

from __future__ import annotations

import datetime
import json
import os
import subprocess
from dataclasses import asdict, is_dataclass
from typing import Any, List, Mapping

# Helper to safely obtain git info; if unavailable, return None.
def _git_info() -> Mapping[str, str | None]:
    def _run_git(arg: str) -> str | None:
        try:
            result = subprocess.run(
                ["git", arg], cwd=os.getcwd(), capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except Exception:
            return None
    branch = _run_git("rev-parse --abbrev-ref HEAD")
    head = _run_git("rev-parse HEAD")
    return {"branch": branch, "head": head}


def _state_to_dict(state: Any) -> dict[str, Any]:
    """Convert supported LangGraph state objects to a serializable dictionary."""
    if isinstance(state, dict):
        return state
    if is_dataclass(state):
        return asdict(state)
    if hasattr(state, "__dict__"):
        return dict(state.__dict__)
    return {"repr": repr(state)}


def write_report(state: Any, report_dir: str = "reports/langgraph-smoke") -> str:
    """Write a comprehensive markdown report for a LangGraph execution state.

    The report includes:
        * Timestamp (UTC)
        * Git branch and HEAD
        * Executed commands with exit codes, stdout, stderr, duration
        * Validation results
        * Overall success flag
        * Errors (if any)
        * Suggested next steps
    """
    os.makedirs(report_dir, exist_ok=True)
    timestamp = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
    safe_timestamp = timestamp.replace("+00:00", "Z").replace(":", "-")
    report_path = os.path.join(report_dir, f"report_{safe_timestamp}.md")

    git_info = _git_info()
    payload = _state_to_dict(state)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# LangGraph Engineering Loop Report\n\n")
        f.write(f"**Timestamp**: {timestamp}\n\n")
        f.write(f"**Branch**: {git_info.get('branch') or 'N/A'}\n\n")
        f.write(f"**HEAD**: {git_info.get('head') or 'N/A'}\n\n")
        f.write("## Executed Commands\n\n")
        commands: List[Mapping[str, Any]] = payload.get("commands", [])
        if commands:
            for cmd in commands:
                f.write(f"- **Command**: `{cmd.get('command')}`\n")
                f.write(f"  - Exit code: {cmd.get('exit_code')}\n")
                f.write(f"  - Duration: {cmd.get('duration'):.2f}s\n")
                stdout = cmd.get('stdout', '').strip()
                stderr = cmd.get('stderr', '').strip()
                if stdout:
                    f.write(f"  - Stdout: `{stdout}`\n")
                if stderr:
                    f.write(f"  - Stderr: `{stderr}`\n")
                f.write("\n")
        else:
            f.write("_No commands recorded_\n\n")

        f.write("## Validations\n\n")
        validations: List[Mapping[str, Any]] = payload.get("validations", [])
        if validations:
            for v in validations:
                f.write(f"- **{v.get('name', 'validation')}**: {'PASS' if v.get('passed') else 'FAIL'} – {v.get('details', '')}\n")
        else:
            f.write("_No validations recorded_\n\n")

        f.write(f"## Overall Success: {'✅ YES' if payload.get('success') else '❌ NO'}\n\n")
        errors = payload.get("errors", [])
        if errors:
            f.write("## Errors\n\n")
            for e in errors:
                f.write(f"- {e}\n")
            f.write("\n")

        f.write("## Suggested Next Steps\n\n")
        if payload.get('success'):
            f.write("- Review the report, then proceed to commit and push the changes.\n")
        else:
            f.write("- Fix the reported errors, then re‑run the smoke test.\n")

        f.write("\n---\n\n")
        f.write("### State Dump (JSON)\n\n")
        f.write("```json\n")
        f.write(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
        f.write("\n```\n")

    return report_path
