"""Context Provider Registry (stub)."""

from typing import Dict, Optional, Type
from aiw.interfaces.context_provider import ContextProvider


class ContextProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, Type[ContextProvider]] = {}
        from .local_rag import LocalRAGContextProvider
        self.register("local_rag", LocalRAGContextProvider)

    def register(self, name: str, provider_class: Type[ContextProvider]):
        self._providers[name] = provider_class

    def get(self, name: str) -> Optional[ContextProvider]:
        cls = self._providers.get(name)
        if cls:
            return cls()
        return None

    def list(self):
        return list(self._providers.keys())


_registry: Optional[ContextProviderRegistry] = None


def get_context_provider_registry() -> ContextProviderRegistry:
    global _registry
    if _registry is None:
        _registry = ContextProviderRegistry()
    return _registry
