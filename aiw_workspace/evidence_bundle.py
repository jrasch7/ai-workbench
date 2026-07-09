# MIGRAÇÃO: aiw_workspace/evidence_bundle.py agora é thin delegate para aiw/.
# Lógica principal migrada para aiw/patch/evidence_bundle.py
# Mantém compatibilidade para cockpit, patch_gate, evidence_export e flows de revisão.
# Evidence Bundle agrega gate + validation + coverage + tests para decisão de patch.

from aiw.patch.evidence_bundle import (
    compute_risk_summary,
    create_evidence_bundle,
    list_evidence_bundles,
    read_evidence_bundle,
    record_patch_decision,
)

__all__ = [
    "compute_risk_summary",
    "create_evidence_bundle",
    "list_evidence_bundles",
    "read_evidence_bundle",
    "record_patch_decision",
]

# Fim da migração parcial para este módulo (patch/evidence). Ver docs/MIGRATION.md
