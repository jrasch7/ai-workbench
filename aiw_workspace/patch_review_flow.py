# MIGRAÇÃO: aiw_workspace/patch_review_flow.py agora é thin delegate para aiw/.
# Lógica principal migrada para aiw/patch/patch_review_flow.py
# Mantém compatibilidade para cockpit, patch_gate, agent_queue e flows de aprovação de patches.
# Fluxo de Revisão de Patch (lifecycle, link queue, get status/next_action).

from aiw.patch.patch_review_flow import (
    _get_lifecycle_dir,
    get_patch_lifecycle,
    save_patch_lifecycle,
    _init_lifecycle,
    discover_workspace_patches,
    link_patch_to_queue_item,
    update_patch_lifecycle,
    get_patch_review_flow,
)

__all__ = [
    "_get_lifecycle_dir",
    "get_patch_lifecycle",
    "save_patch_lifecycle",
    "_init_lifecycle",
    "discover_workspace_patches",
    "link_patch_to_queue_item",
    "update_patch_lifecycle",
    "get_patch_review_flow",
]

# Fim da migração parcial para este módulo (patch/evidence). Ver docs/MIGRATION.md
