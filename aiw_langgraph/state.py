"""State definitions for LangGraph engineering loop."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class LoopState:
    """Container for loop state data with detailed fields for engineering loop."""
    context: Dict[str, Any] = field(default_factory=dict)
    plan: Optional[Dict[str, Any]] = None
    commands: List[Dict[str, Any]] = field(default_factory=list)  # each command execution metadata
    validations: List[Dict[str, Any]] = field(default_factory=list)  # validation results
    result: Any = None
    success: bool = False
    errors: List[str] = field(default_factory=list)
