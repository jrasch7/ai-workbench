"""Model Providers (target structure).

Real providers:
- litellm (adapter to existing gateway)
- openrouter (direct, start here)

See docs/interfaces/model-provider.md and guides/adding-model-provider.md
"""

from .registry import ModelProviderRegistry, get_model_provider_registry
from .openrouter import OpenRouterModelProvider
from .litellm_adapter import LiteLLMModelProvider

__all__ = [
    "ModelProviderRegistry",
    "get_model_provider_registry",
    "OpenRouterModelProvider",
    "LiteLLMModelProvider",
]
