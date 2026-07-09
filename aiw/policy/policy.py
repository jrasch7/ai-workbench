"""Capability Policy bridge.

Light surgical (step 4): bridge kept for compat; prefer aiw.policy.registry.get_policy_engine().evaluate_capability
or from aiw.policy import evaluate_capability_policy (which delegates to engine).
aiw/ is canonical for cap data/eval (see registry + capabilities.py). Similar to runtime_gate migration.
"""

# Legacy direct kept for thin compat during migration (callers should prefer aiw equivalents)
from aiw_workspace.capability_policy import evaluate_capability_policy
