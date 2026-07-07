"""OpenRouter Model Provider implementation.

Implements the ModelProvider interface for OpenRouter (https://openrouter.ai).

Usage:
- Set OPENROUTER_API_KEY env var.
- Models like "openai/gpt-4o", "anthropic/claude-3.5-sonnet", "deepseek/deepseek-chat", etc.

See docs/interfaces/model-provider.md
"""

import json
import os
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

from aiw.interfaces.model_provider import ModelProvider


class OpenRouterModelProvider(ModelProvider):
    """OpenRouter provider."""

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        # Do not raise here, only on use (for registry list etc)
        if not self.api_key:
            self.api_key = None  # will fail on generate if not set


    def name(self) -> str:
        return "openrouter"

    def list_models(self) -> List[Dict[str, Any]]:
        """List available models from OpenRouter."""
        url = f"{self.BASE_URL}/models"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                models = []
                for m in data.get("data", []):
                    models.append({
                        "id": m.get("id"),
                        "name": m.get("name"),
                        "context_window": m.get("context_length"),
                        "pricing": m.get("pricing", {}),
                        "capabilities": {
                            "tools": "tools" in (m.get("architecture", {}).get("modality", "") or "").lower() or True,
                        }
                    })
                return models
        except Exception as e:
            return [{"id": "error", "error": str(e)}]

    def generate(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """Generate completion via chat API."""
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set")
        url = f"{self.BASE_URL}/chat/completions"
        messages = [{"role": "user", "content": prompt}]
        payload = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens"),
        }
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": kwargs.get("referer", "https://aiw.local"),
                "X-Title": kwargs.get("title", "AIW"),
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=kwargs.get("timeout", 120)) as resp:
                data = json.loads(resp.read().decode())
                choice = data.get("choices", [{}])[0]
                message = choice.get("message", {})
                usage = data.get("usage", {})
                return {
                    "text": message.get("content", ""),
                    "model": data.get("model", model),
                    "usage": {
                        "prompt_tokens": usage.get("prompt_tokens"),
                        "completion_tokens": usage.get("completion_tokens"),
                        "total_tokens": usage.get("total_tokens"),
                    },
                    "raw": data,
                }
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else str(e)
            raise RuntimeError(f"OpenRouter API error {e.code}: {error_body}")
        except Exception as e:
            raise RuntimeError(f"OpenRouter request failed: {e}")

    def supports(self, capability: str) -> bool:
        caps = {
            "text": True,
            "chat": True,
            "tools": True,  # many models support
            "vision": True,  # depends on model
            "long_context": True,
        }
        return caps.get(capability.lower(), False)

    def count_tokens(self, text: str, model: str) -> int:
        # Rough estimate; real would use tiktoken or provider endpoint
        return len(text.split()) * 1  # very rough
