# Model Provider Interface

**Purpose:** Abstraction for any system that can generate text/reasoning from a prompt.

This allows AIW to use OpenRouter, OpenAI, Anthropic, Gemini, Ollama, local models, etc. interchangeably.

## Interface (Python-like contract)

```python
class ModelProvider:
    def name(self) -> str:
        """Unique identifier, e.g. 'openrouter', 'ollama'."""

    def list_models(self) -> list[dict]:
        """Return available models with metadata (id, context_window, cost, capabilities)."""

    def generate(self, prompt: str, model: str, **kwargs) -> dict:
        """Synchronous generation. Returns {text, usage, metadata}."""

    def stream(self, prompt: str, model: str, **kwargs):
        """Optional streaming generator."""

    def supports(self, capability: str) -> bool:
        """e.g. 'tools', 'vision', 'long_context', 'reasoning'."""

    def count_tokens(self, text: str, model: str) -> int:
        ...
```

## Responsibilities
- Authentication and rate limiting handled inside the provider.
- Return structured usage/cost information when possible.
- Never assume a specific model family.

## Examples
- OpenRouterProvider (multi-model)
- OpenAIProvider
- AnthropicProvider
- OllamaProvider (local first-class)

## Registration
Providers register themselves with the central registry. The Model Router discovers them.
