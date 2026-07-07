"""Capability & Policy Registry (target structure).

This is becoming the source of truth.
Currently bridges to legacy for compatibility during migration.
"""

from typing import Any, Dict, List, Optional

# Own the data now (aligned)
from .capabilities import _capabilities_db

def legacy_get_capability(name: str):
    for cap in _capabilities_db():
        if cap["name"] == name:
            return cap
    return None

def legacy_validate(cap):
    return cap is not None and "name" in cap  # basic for now, real validation in legacy if needed

# Lazy to avoid cycles with legacy
def _get_legacy_policy():
    from aiw_workspace.capability_policy import evaluate_capability_policy as fn
    return fn

def _get_legacy_isolation():
    from aiw_workspace.isolation_boundary import evaluate_isolation_boundary as fn
    return fn

def _get_legacy_runtime():
    from aiw_workspace.runtime_gate import evaluate_runtime_gate as fn
    return fn
from aiw_workspace.capability_policy import evaluate_capability_policy as legacy_evaluate_policy
from aiw_workspace.isolation_boundary import evaluate_isolation_boundary as legacy_evaluate_isolation
from aiw_workspace.runtime_gate import evaluate_runtime_gate as legacy_evaluate_runtime


class CapabilityRegistry:
    """Unified registry for capabilities."""

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        for cap in _capabilities_db():
            if cap["name"] == name:
                return cap
        return None

    def validate(self, cap: Dict[str, Any]) -> bool:
        return cap is not None and "name" in cap

    def list_all(self) -> List[Dict[str, Any]]:
        return _capabilities_db()


class PolicyEngine:
    """Central policy evaluation."""

    def evaluate_capability(
        self, workspace_id: str, capability_name: str, **kwargs
    ) -> Dict[str, Any]:
        return _get_legacy_policy()(workspace_id, capability_name, **kwargs)

    def evaluate_isolation(self, **kwargs) -> Dict[str, Any]:
        return _get_legacy_isolation()(**kwargs)

    def evaluate_runtime(self, **kwargs) -> Dict[str, Any]:
        return _get_legacy_runtime()(**kwargs)


_registry: Optional[CapabilityRegistry] = None
_policy_engine: Optional[PolicyEngine] = None


def get_capability_registry() -> CapabilityRegistry:
    global _registry
    if _registry is None:
        _registry = CapabilityRegistry()
    return _registry


def get_policy_engine() -> PolicyEngine:
    global _policy_engine
    if _policy_engine is None:
        _policy_engine = PolicyEngine()
    return _policy_engine
