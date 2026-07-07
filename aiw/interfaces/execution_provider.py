"""Execution Provider interface.

See docs/interfaces/execution-provider.md for the authoritative definition.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ExecutionProvider(ABC):
    """Interface for all execution mechanisms (CodeAct, Docker, Devcontainer, etc.).

    Execution Providers are completely separate from Model Providers.
    They must respect Policy and Isolation decisions.
    """

    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def describe(self) -> Dict[str, Any]:
        """Return capabilities, supported operations, risk level, required runtime."""
        ...

    @abstractmethod
    def validate(self, action: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ...

    @abstractmethod
    def supports_runtime(self, runtime: str) -> bool:
        ...

    @abstractmethod
    def dry_run(self, workspace_id: str, action: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        ...

    @abstractmethod
    def execute(
        self, workspace_id: str, action: Dict[str, Any], confirm: bool = False, **kwargs
    ) -> Dict[str, Any]:
        ...

    def supports_operation(self, operation: str | None) -> bool:
        """Optional: check if this provider supports a specific operation."""
        return True


