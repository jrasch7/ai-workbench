"""Agent Profile interface stub (see docs/interfaces/agent-profile.md)."""

from typing import Any, Dict, Optional


class AgentProfile:
    """Simple dataclass-like for profiles during alignment."""

    def __init__(self, name: str, **kwargs: Any):
        self.name = name
        self.__dict__.update(kwargs)

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__
