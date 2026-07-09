# MIGRAÇÃO: aiw_workspace/changed_lines_coverage.py agora é thin delegate para aiw/patch/.
# Lógica principal migrada para aiw/patch/changed_lines_coverage.py
# Mantém compatibilidade para patch_gate, cockpit e análise de cobertura linha a linha.

from aiw.patch.changed_lines_coverage import analyze_changed_lines_coverage

__all__ = [
    "analyze_changed_lines_coverage",
]

# Fim da migração parcial para este módulo. Ver docs/MIGRATION.md
