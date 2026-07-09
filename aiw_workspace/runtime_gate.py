# MIGRAÇÃO CIRÚRGICA (Cockpit/agent path): runtime_gate agora tem lógica em aiw/policy/runtime_gate.py
# aiw_workspace/runtime_gate.py = thin delegate (ponte de compat).
# Mantém reexports de RUNTIME_PROFILE, RUNTIME_PROFILES, FIXED_*, KNOWN_*, evaluate_runtime_gate, assert_runtime_allowed.
# Usado internamente por aiw_workspace/isolation_boundary.py, execution_provider.py, capability_policy.py (relativo)
# e por aiw/policy (agora prefere aiw/). Não quebra callers legados.
# Termos PT: Porta de Runtime (Runtime Gate), usada pelo Loop Iterativo do Agente via PolicyEngine.

from aiw.policy.runtime_gate import (
    RUNTIME_PROFILE,
    RUNTIME_PROFILES,
    FIXED_CODEACT_OPERATIONS,
    KNOWN_RUNTIME_OPERATIONS,
    evaluate_runtime_gate,
    assert_runtime_allowed,
)

__all__ = [
    "RUNTIME_PROFILE",
    "RUNTIME_PROFILES",
    "FIXED_CODEACT_OPERATIONS",
    "KNOWN_RUNTIME_OPERATIONS",
    "evaluate_runtime_gate",
    "assert_runtime_allowed",
]

# (corpo de lógica removido na migração cirúrgica para aiw/policy/runtime_gate.py)
# Thin delegate acima reexporta os símbolos de aiw.policy para manter compat 100%.
# Nenhuma lógica duplicada aqui.
