"""Policy layer (target structure).

This is the canonical place for capability, isolation and runtime decisions.
"""

from .registry import (
    CapabilityRegistry,
    PolicyEngine,
    get_capability_registry,
    get_policy_engine,
)

# Expose legacy style for compatibility during alignment
def evaluate_capability_policy(*a, **k):
    return get_policy_engine().evaluate_capability(*a, **k)

def evaluate_isolation_boundary(*a, **k):
    return get_policy_engine().evaluate_isolation(*a, **k)

def evaluate_runtime_gate(*a, **k):
    return get_policy_engine().evaluate_runtime(*a, **k)

__all__ = [
    "CapabilityRegistry",
    "PolicyEngine",
    "get_capability_registry",
    "get_policy_engine",
    "evaluate_capability_policy",
    "evaluate_isolation_boundary",
    "evaluate_runtime_gate",
]

