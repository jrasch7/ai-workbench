"""Model Provider interface (text / reasoning generation).

See docs/interfaces/model-provider.md for the authoritative definition.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ModelProvider(ABC):
    """Interface that all Model Providers must implement.

    This allows AIW to treat OpenRouter, OpenAI, Anthropic, Gemini,
    Ollama, local models, and future providers uniformly.
    """

    @abstractmethod
    def name(self) -> str:
        """Unique provider name (e.g. 'openrouter', 'ollama')."""
        ...

    @abstractmethod
    def list_models(self) -> List[Dict[str, Any]]:
        """Return available models with metadata (id, context_window, cost, capabilities)."""
        ...

    @abstractmethod
    def generate(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """Synchronous generation. Returns {text, usage, metadata}."""
        ...

    def stream(self, prompt: str, model: str, **kwargs):
        """Optional streaming generator."""
        raise NotImplementedError

    @abstractmethod
    def supports(self, capability: str) -> bool:
        """Check if provider supports a capability (e.g. 'tools', 'vision', 'long_context')."""
        ...

    def count_tokens(self, text: str, model: str) -> int:
        """Optional token counting."""
        raise NotImplementedError

