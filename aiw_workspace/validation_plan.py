# MIGRAÇÃO CIRÚRGICA: Lógica movida para aiw/patch/validation_plan.py
# Este arquivo agora é thin delegate reexportando de aiw/ (aiw-first).
# Mantém compatibilidade total para callers legados (aiw_workspace.*, cockpit, etc).
# Prefer: from aiw.patch import ... ou from aiw import validation_...

from aiw.patch.validation_plan import (
    validation_plan_for_patch,
    ensure_validation_plan_snapshot,
    list_validation_plan_snapshots,
    get_validation_plan_snapshot,
    compare_validation_plan_snapshots,
    validation_reliability,
    preview_validation_plan_command,
    run_validation_plan_commands,
)

__all__ = [
    "validation_plan_for_patch",
    "ensure_validation_plan_snapshot",
    "list_validation_plan_snapshots",
    "get_validation_plan_snapshot",
    "compare_validation_plan_snapshots",
    "validation_reliability",
    "preview_validation_plan_command",
    "run_validation_plan_commands",
]

# Fim da migração para validation_plan (aiw/patch primary).
