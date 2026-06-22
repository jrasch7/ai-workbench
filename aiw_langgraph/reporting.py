"""Reporting utilities for LangGraph engineering loop."""

from __future__ import annotations

import datetime
import json
import os
from dataclasses import asdict, is_dataclass
from typing import Any


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
    """Write a markdown report for a LangGraph execution state."""
    os.makedirs(report_dir, exist_ok=True)

    timestamp = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
    safe_timestamp = timestamp.replace("+00:00", "Z").replace(":", "-")
    report_path = os.path.join(report_dir, f"report_{safe_timestamp}.md")

    payload = _state_to_dict(state)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# LangGraph Engineering Loop Report\n\n")
        f.write(f"**Timestamp**: {timestamp}\n\n")
        f.write("## State Dump\n\n")
        f.write("```json\n")
        f.write(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
        f.write("\n```\n")

    return report_path
