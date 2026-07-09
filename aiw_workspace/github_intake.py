# MIGRAÇÃO: aiw_workspace/github_intake.py agora é thin delegate para aiw/.
# Lógica principal migrada para aiw/integration/github_intake.py
# Mantém compatibilidade total para callers legados (cockpit, scripts, outros módulos).
# Atualize novos callers para usar aiw.integration diretamente quando possível.

from aiw.integration.github_intake import (
    create_patch_intent,
    run_github_intake,
    list_inbox_items,
    read_inbox_item,
    update_inbox_item_status,
    resolve_inbox_item_file,
    list_inbox_item_attempts,
)

__all__ = [
    "create_patch_intent",
    "run_github_intake",
    "list_inbox_items",
    "read_inbox_item",
    "update_inbox_item_status",
    "resolve_inbox_item_file",
    "list_inbox_item_attempts",
]

# Fim da migração parcial para este módulo. Ver docs/MIGRATION.md
