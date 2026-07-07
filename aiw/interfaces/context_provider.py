"""Context Provider interface (knowledge sources).

See docs/interfaces/context-provider.md for the authoritative definition.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ContextProvider(ABC):
    """Interface for sources of context/knowledge (RAG, Git, Docs, Jira, etc.)."""

    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def retrieve(self, query: str, workspace_id: str, **kwargs) -> List[Dict[str, Any]]:
        """Return relevant chunks with source, score, content."""
        ...

    @abstractmethod
    def describe(self) -> Dict[str, Any]:
        """Describe capabilities and supported sources."""
        ...

    def index(self, workspace_id: str, **kwargs) -> Dict[str, Any]:
        """Optional: (re)build index for this source."""
        raise NotImplementedError

