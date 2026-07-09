# MIGRAÇÃO: aiw_workspace/integration_outbox.py agora é thin delegate para aiw/.
# Lógica principal migrada para aiw/integration/integration_outbox.py
# Mantém compatibilidade total para callers legados (cockpit, aiw-integration-worker, evidence flows).
# Prefira imports de aiw.integration quando a funcionalidade existir em aiw/.

from aiw.integration.integration_outbox import (
    create_outbox_item,
    list_outbox_items,
    read_outbox_item,
    update_outbox_item_status,
    resolve_outbox_item_file,
    set_outbox_dispatch,
)

__all__ = [
    "create_outbox_item",
    "list_outbox_items",
    "read_outbox_item",
    "update_outbox_item_status",
    "resolve_outbox_item_file",
    "set_outbox_dispatch",
]

# Fim da migração parcial para este módulo. Ver docs/MIGRATION.md
