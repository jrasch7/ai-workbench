# MIGRAÇÃO CIRÚRGICA: Lógica movida para aiw/workspace/external_worker_policy.py
# Este arquivo agora é thin delegate reexportando de aiw/ (aiw-first).
# Mantém compatibilidade total para callers legados.
# Prefer: from aiw.workspace.external_worker_policy import ... ou from aiw import ...

from aiw.workspace.external_worker_policy import (
    load_external_worker_policy,
    validate_external_worker_policy,
    can_worker_execute,
)

__all__ = [
    "load_external_worker_policy",
    "validate_external_worker_policy",
    "can_worker_execute",
]

# Fim da migração para external_worker_policy.
