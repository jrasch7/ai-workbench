"""Policy layer (target structure).

This is the canonical place for capability, isolation and runtime decisions.
aiw/ preferred (light surgical migration step 4 for capabilities, analogous to runtime_gate).
"""

from .registry import (
    CapabilityRegistry,
    PolicyEngine,
    get_capability_registry,
    get_policy_engine,
    POLICY_PROFILE,  # reexport for agent/regression path (aiw preferred)
    is_trusted_ws,  # step 5 policy relax helper (aiw-first)
)

# Expose legacy style for compatibility during alignment; aiw preferred via registry/engine
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
    "POLICY_PROFILE",
    "is_trusted_ws",  # aiw-first trusted ws for cap relax (step 5)
    "evaluate_capability_policy",
    "evaluate_isolation_boundary",
    "evaluate_runtime_gate",
]

