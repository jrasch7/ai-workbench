"""Model Router - aligned implementation.

Makes intelligent (or profile-driven) selection of model/provider.
Replaces the previous mock heuristic.
"""

from typing import Any, Dict, Optional, List
from aiw.providers.model.registry import get_model_provider_registry


class ModelRouter:
    """Chooses provider + model based on task, profile and constraints.

    This is now the real routing layer.
    """

    def route(
        self,
        task: str,
        profile: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None,
        mode: str = "auto",
    ) -> Dict[str, Any]:
        constraints = constraints or {}
        profile = profile or {}

        if mode != "auto":
            provider = constraints.get("provider") or profile.get("default_provider", "litellm")
            model = constraints.get("model") or profile.get("default_model", "dev-coder")
            rationale = "Explicit selection"
        else:
            # Real routing logic based on profile + task analysis
            task_lower = task.lower()
            allowed = profile.get("allowed_model_providers", ["litellm"])
            default_model = profile.get("default_model", "dev-coder")

            # Prefer from registered model providers
            model_reg = get_model_provider_registry()
            avail = model_reg.list() or ["litellm"]

            if any(kw in task_lower for kw in ["security", "pentest", "vulnerab", "review"]):
                provider = [p for p in allowed if p in avail][0] if any(p in avail for p in allowed) else "litellm"
                model = profile.get("security_model", default_model)
                rationale = "Security/review task -> stronger reasoning model"
            elif any(kw in task_lower for kw in ["test", "unittest", "generate test"]):
                provider = [p for p in allowed if p in avail][0] if any(p in avail for p in allowed) else "litellm"
                model = profile.get("fast_model", default_model)
                rationale = "Test generation -> fast/cheap model"
            elif any(kw in task_lower for kw in ["refactor", "architect", "design", "large"]):
                provider = [p for p in allowed if p in avail][0] if any(p in avail for p in allowed) else "litellm"
                model = profile.get("strong_model", default_model)
                rationale = "Complex refactoring/architecture -> high capability model"
            else:
                provider = [p for p in allowed if p in avail][0] if any(p in avail for p in allowed) else "litellm"
                model = default_model
                rationale = "Default for task type"

        params = {
            "temperature": profile.get("temperature", constraints.get("temperature", 0.2)),
        }

        return {
            "provider": provider,
            "model": model,
            "params": params,
            "rationale": rationale,
            "mode": mode,
            "profile_used": profile.get("name") if profile else None,
        }

    def list_options(self, task: str, constraints: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        reg = get_model_provider_registry()
        models: List[Dict[str, Any]] = []
        for name in reg.list():
            p = reg.get(name)
            if p:
                models.extend(p.list_models())
        return models or [{"id": "dev-coder", "provider": "litellm"}]


_router: Optional[ModelRouter] = None


def get_model_router() -> ModelRouter:
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router

