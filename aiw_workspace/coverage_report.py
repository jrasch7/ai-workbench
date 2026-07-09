# MIGRAÇÃO CIRÚRGICA: Lógica movida para aiw/patch/coverage_report.py
# Este arquivo agora é thin delegate reexportando de aiw/ (aiw-first).
# Mantém compatibilidade total.
# Prefer: from aiw.patch import analyze_patch_coverage etc.

from aiw.patch.coverage_report import (
    parse_cobertura_xml,
    parse_lcov,
    load_coverage_reports,
    analyze_patch_coverage,
    capture_test_run_coverage,
)

__all__ = [
    "parse_cobertura_xml",
    "parse_lcov",
    "load_coverage_reports",
    "analyze_patch_coverage",
    "capture_test_run_coverage",
]

# Fim da migração para coverage_report (aiw/patch primary).
