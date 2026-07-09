# MIGRAÇÃO CIRÚRGICA STEP 1: aiw_workspace/test_runner.py agora thin delegate.
# Lógica principal em aiw/patch/test_runner.py (aiw-first).
# Usa reexport simples (compat com lazy __getattr__ em __init__.py para evitar ciclos).
# Prefer aiw/ imports em todo lugar. Sem mudança de comportamento.

from aiw.patch.test_runner import (
    preview_test_command,
    run_test_command,
    list_test_runs,
    list_all_test_runs,
    get_test_run,
    rerun_test_run,
    load_patch_preview,
    suggest_tests_for_patch,
    preview_patch_suggested_test,
    run_patch_suggested_test,
    tests_payload,
    _workspace_base,
    _command_from_profile,
)

__all__ = [
    "preview_test_command",
    "run_test_command",
    "list_test_runs",
    "list_all_test_runs",
    "get_test_run",
    "rerun_test_run",
    "load_patch_preview",
    "suggest_tests_for_patch",
    "preview_patch_suggested_test",
    "run_patch_suggested_test",
    "tests_payload",
    "_workspace_base",
    "_command_from_profile",
]

# Fim da migração para test_runner (aiw/patch primary). Ver docs/MIGRATION.md
