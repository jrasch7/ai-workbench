# MIGRAÇÃO: aiw_workspace/patch_gate.py agora é thin delegate para aiw/patch/.
# Lógica principal migrada para aiw/patch/patch_gate.py
# Mantém compatibilidade para cockpit, aiw/, scripts e flows de revisão/aprovação de patches.
# Review Gate agrega validation, coverage, changed lines, tests para decisão de apply.

from aiw.patch.patch_gate import (
    review_gate_for_patch,
    list_review_gates,
    apply_reviewed_patch,
    rollback_reviewed_patch,
)

__all__ = [
    "review_gate_for_patch",
    "list_review_gates",
    "apply_reviewed_patch",
    "rollback_reviewed_patch",
]

# Fim da migração para este módulo (patch_gate). Ver docs/MIGRATION.md
