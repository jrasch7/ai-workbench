"""Stub for Model Provider using LiteLLM (existing gateway).

This is a placeholder to align with the new structure.
Real implementation will wrap the current model-ask / LiteLLM usage.
"""

from aiw.interfaces.model_provider import ModelProvider
from typing import Any, Dict, List


class LiteLLMModelProvider(ModelProvider):
    """Placeholder adapter for current LiteLLM usage."""

    def name(self) -> str:
        return "litellm"

    def list_models(self) -> List[Dict[str, Any]]:
        # TODO: integrate with existing model aliases
        return [{"id": "dev-coder", "provider": "litellm"}]

    def generate(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        # In real impl, call the existing LLM gateway
        raise NotImplementedError("LiteLLM adapter not yet wired. See scripts/model-ask")

    def supports(self, capability: str) -> bool:
        return capability in ("text", "basic")
