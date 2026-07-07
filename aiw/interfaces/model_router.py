"""Model Router interface stub (see docs/interfaces/model-router.md)."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List


class ModelRouter(ABC):
    @abstractmethod
    def route(self, task: str, profile: Optional[Dict[str, Any]] = None, constraints: Optional[Dict[str, Any]] = None, mode: str = "auto") -> Dict[str, Any]:
        ...

    def list_options(self, task: str, constraints: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return []
