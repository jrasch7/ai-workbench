"""State definitions for LangGraph engineering loop."""

from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class LoopState:
    """Simple container for loop state data."""
    context: Dict[str, Any]
    plan: Dict[str, Any] | None = None
    result: Any = None
    success: bool = False
