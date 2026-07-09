# MIGRAÇÃO: aiw_workspace/integration_worker.py agora é thin delegate para aiw/.
# Lógica principal migrada para aiw/integration/integration_worker.py
# Mantém compatibilidade total para callers legados (scripts, cockpit flows de integração).
# Inclui checagens de policy e marcação de sent.

from aiw.integration.integration_worker import (
    mark_outbox_item_sent,
    run_worker,
    list_item_attempts,
)

__all__ = [
    "mark_outbox_item_sent",
    "run_worker",
    "list_item_attempts",
]

# Fim da migração parcial para este módulo. Ver docs/MIGRATION.md
