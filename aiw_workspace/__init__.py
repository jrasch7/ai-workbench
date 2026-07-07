"""Workspace profile resolution for AIW.

Aligned parts re-exported from new aiw/ structure.
"""

# Reexports from aligned new structure
# Lazy delegate to aiw/ for alignment (avoid cycles)
def _get_aiw():
    import aiw
    return aiw

def list_capabilities():
    return _get_aiw().get_capability_registry().list_all()

def get_capability(name):
    return _get_aiw().get_capability_registry().get(name)

def validate_capability_definition(cap):
    return _get_aiw().get_capability_registry().validate(cap)

# Reexports from aligned aiw/ (lazy)
def load_profile(*a, **k):
    return _get_aiw().load_profile(*a, **k)

def get_profile(*a, **k):
    return _get_aiw().get_profile(*a, **k)

def list_profiles():
    return _get_aiw().list_profiles()

def get_model_router():
    return _get_aiw().get_model_router()

def get_execution_provider_registry():
    return _get_aiw().get_execution_provider_registry()

def get_policy_engine():
    return _get_aiw().get_policy_engine()

def get_capability_registry():
    return _get_aiw().get_capability_registry()

def run_agent_iterative_loop_once(*a, **k):
    return _get_aiw().run_agent_iterative_loop_once(*a, **k)

def list_agent_loop_runs(*a, **k):
    return _get_aiw().list_agent_loop_runs(*a, **k)

def read_agent_loop_run(*a, **k):
    return _get_aiw().read_agent_loop_run(*a, **k)

# Additional reexports/delegates for Round 2 alignment (4. mover)
def get_experiment_lab():
    return _get_aiw().get_experiment_lab()

def get_docker_execution_provider():
    return _get_aiw().get_docker_execution_provider()

def get_devcontainer_execution_provider():
    return _get_aiw().get_devcontainer_execution_provider()

def get_agent_queue():
    return _get_aiw().get_agent_queue()

# Mais migração: delegando funções de queue para aiw/
def create_queue_item_from_inbox(*a, **k):
    from .agent_queue import create_queue_item_from_inbox as fn
    return fn(*a, **k)

# Mais migração: delegates para worker loop
def run_worker_loop_once(*a, **k):
    from .worker_loop import run_worker_loop_once as fn
    return fn(*a, **k)

def list_worker_loop_runs(*a, **k):
    from .worker_loop import list_worker_loop_runs as fn
    return fn(*a, **k)


from .profiles import (
    DEFAULT_WORKSPACE,
    load_workspaces_config,
    normalize_workspace_id,
    resolve_workspace,
    execution_policy,
    validate_workspace_path,
    detect_stack,
    validate_profile,
    validate_test_command,
    add_workspace,
    remove_workspace,
)
from .test_runner import (
    tests_payload,
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
)
from .validation_plan import (
    validation_plan_for_patch,
    ensure_validation_plan_snapshot,
    list_validation_plan_snapshots,
    get_validation_plan_snapshot,
    compare_validation_plan_snapshots,
    validation_reliability,
    preview_validation_plan_command,
    run_validation_plan_commands,
)
from .patch_gate import (
    review_gate_for_patch,
    list_review_gates,
    apply_reviewed_patch,
    rollback_reviewed_patch,
)
from .patch_review_flow import (
    discover_workspace_patches,
    link_patch_to_queue_item,
    get_patch_review_flow,
    get_patch_lifecycle,
    update_patch_lifecycle,
)
from .test_coverage_intent import analyze_test_coverage_intent
from .coverage_report import analyze_patch_coverage
from .coverage_baseline import get_current_coverage_baseline, promote_coverage_baseline, list_coverage_baselines, coverage_diff
from .changed_lines_coverage import analyze_changed_lines_coverage
from .test_result_report import analyze_test_results
from .evidence_bundle import create_evidence_bundle, list_evidence_bundles, read_evidence_bundle, record_patch_decision
from .evidence_export import create_evidence_export, list_evidence_exports, read_evidence_export, resolve_evidence_export_file
from .integration_outbox import create_outbox_item, list_outbox_items, read_outbox_item, update_outbox_item_status, resolve_outbox_item_file, set_outbox_dispatch
from .github_intake import run_github_intake, list_inbox_items, read_inbox_item, update_inbox_item_status, resolve_inbox_item_file, list_inbox_item_attempts
from .agent_queue import create_queue_item_from_inbox, list_queue_items, read_queue_item, update_queue_item_status, resolve_queue_item_file, list_queue_item_attempts, run_queue_item_offline, run_queue_item_llm, set_queue_dispatch
from .external_worker_policy import load_external_worker_policy, validate_external_worker_policy, can_worker_execute
from .worker_loop import list_worker_loop_runs, read_worker_loop_run
from .agent_dispatcher import list_agent_dispatcher_runs, read_agent_dispatcher_run
# Delegate to aligned aiw (lazy)
from .agent_iterative_loop import run_agent_iterative_loop_once, list_agent_loop_runs, read_agent_loop_run
from .isolation_boundary import evaluate_isolation_boundary, assert_isolation_allowed

__all__ = [
    "DEFAULT_WORKSPACE",
    "load_workspaces_config",
    "normalize_workspace_id",
    "resolve_workspace",
    "execution_policy",
    "validate_workspace_path",
    "detect_stack",
    "validate_profile",
    "validate_test_command",
    "add_workspace",
    "remove_workspace",
    "tests_payload",
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
    "validation_plan_for_patch",
    "ensure_validation_plan_snapshot",
    "list_validation_plan_snapshots",
    "get_validation_plan_snapshot",
    "compare_validation_plan_snapshots",
    "validation_reliability",
    "preview_validation_plan_command",
    "run_validation_plan_commands",
    "review_gate_for_patch",
    "list_review_gates",
    "apply_reviewed_patch",
    "analyze_test_coverage_intent",
    "analyze_patch_coverage",
    "get_current_coverage_baseline",
    "promote_coverage_baseline",
    "list_coverage_baselines",
    "coverage_diff",
    "analyze_changed_lines_coverage",
    "analyze_test_results",
    "create_evidence_bundle",
    "list_evidence_bundles",
    "read_evidence_bundle",
    "record_patch_decision",
    "create_evidence_export",
    "list_evidence_exports",
    "read_evidence_export",
    "resolve_evidence_export_file",
    "create_outbox_item",
    "list_outbox_items",
    "read_outbox_item",
    "update_outbox_item_status",
    "resolve_outbox_item_file",
    "run_github_intake",
    "list_inbox_items",
    "read_inbox_item",
    "update_inbox_item_status",
    "resolve_inbox_item_file",
    "list_inbox_item_attempts",
    "create_queue_item_from_inbox",
    "list_queue_items",
    "read_queue_item",
    "update_queue_item_status",
    "resolve_queue_item_file",
    "list_queue_item_attempts",
    "run_queue_item_offline",
    "rollback_reviewed_patch",
    "discover_workspace_patches",
    "link_patch_to_queue_item",
    "get_patch_review_flow",
    "get_patch_lifecycle",
    "update_patch_lifecycle",
    "load_external_worker_policy",
    "validate_external_worker_policy",
    "can_worker_execute",
    "set_outbox_dispatch",
    "list_worker_loop_runs",
    "read_worker_loop_run",
    "run_queue_item_llm",
    "set_queue_dispatch",
    "list_agent_dispatcher_runs",
    "read_agent_dispatcher_run",
    "run_agent_iterative_loop_once",
    "list_agent_loop_runs",
    "read_agent_loop_run",
    "evaluate_isolation_boundary",
    "assert_isolation_allowed",
    "get_experiment_lab",
    "get_docker_execution_provider",
    "get_devcontainer_execution_provider",
    "get_agent_queue",
]
