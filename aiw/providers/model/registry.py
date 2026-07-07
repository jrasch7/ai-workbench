"""Model Provider Registry (stub for alignment)."""

from typing import Dict, Optional, Type
from aiw.interfaces.model_provider import ModelProvider


class ModelProviderRegistry:
    """Registry for Model Providers."""

    def __init__(self):
        self._providers: Dict[str, Type[ModelProvider]] = {}
        # Register available providers
        from .litellm_adapter import LiteLLMModelProvider
        self.register("litellm", LiteLLMModelProvider)
        from .openrouter import OpenRouterModelProvider
        self.register("openrouter", OpenRouterModelProvider)

    def register(self, name: str, provider_class: Type[ModelProvider]):
        self._providers[name] = provider_class

    def get(self, name: str) -> Optional[ModelProvider]:
        cls = self._providers.get(name)
        if cls:
            return cls()
        return None

    def list(self):
        return list(self._providers.keys())


_registry: Optional[ModelProviderRegistry] = None


def get_model_provider_registry() -> ModelProviderRegistry:
    global _registry
    if _registry is None:
        _registry = ModelProviderRegistry()
    return _registry
