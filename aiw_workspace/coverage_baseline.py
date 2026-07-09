# MIGRAÇÃO CIRÚRGICA STEP 1: aiw_workspace/coverage_baseline.py agora thin delegate.
# Lógica principal em aiw/patch/coverage_baseline.py (aiw-first).
# Prefer aiw/ . Sem mudança de comportamento.

from aiw.patch.coverage_baseline import (
    get_current_coverage_baseline,
    promote_coverage_baseline,
    list_coverage_baselines,
    coverage_diff,
)

__all__ = [
    "get_current_coverage_baseline",
    "promote_coverage_baseline",
    "list_coverage_baselines",
    "coverage_diff",
]

# Fim da migração para coverage_baseline (aiw/patch primary). Ver docs/MIGRATION.md
