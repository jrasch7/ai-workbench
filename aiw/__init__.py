"""AIW - Target package structure (in progress alignment).

This package represents the future organized structure.
Legacy code remains in aiw_workspace/ during migration.

Import example:
    from aiw.providers.execution.registry import get_execution_provider_registry
    from aiw.router.router import get_model_router
"""

# Lazy imports to avoid cycles during alignment
def get_execution_provider_registry():
    from .providers.execution.registry import get_execution_provider_registry as fn
    return fn()

def get_model_provider_registry():
    from .providers.model.registry import get_model_provider_registry as fn
    return fn()

def get_context_provider_registry():
    from .providers.context.registry import get_context_provider_registry as fn
    return fn()

def get_model_router():
    from .router.router import get_model_router as fn
    return fn()

def get_capability_registry():
    from .policy.registry import get_capability_registry as fn
    return fn()

def get_policy_engine():
    from .policy.registry import get_policy_engine as fn
    return fn()

# Reexport for capability policy data/eval (aiw/ preferred in surgical step 4, like runtime; also exposed via get_capability_registry already)
def evaluate_capability_policy(*a, **k):
    from .policy.registry import get_policy_engine as fn
    return fn().evaluate_capability(*a, **k)

def get_capability_policy_profile():
    from .policy.registry import POLICY_PROFILE as p
    return p

def load_profile(*a, **k):
    from .profiles import load_profile as fn
    return fn(*a, **k)

def get_profile(*a, **k):
    from .profiles import get_profile as fn
    return fn(*a, **k)

def list_profiles():
    from .profiles import list_profiles as fn
    return fn()

def run_agent_iterative_loop_once(*a, **k):
    from .agent import run_agent_iterative_loop_once as fn
    return fn(*a, **k)

def list_agent_loop_runs(*a, **k):
    from .agent import list_agent_loop_runs as fn
    return fn(*a, **k)

def read_agent_loop_run(*a, **k):
    from .agent import read_agent_loop_run as fn
    return fn(*a, **k)

# Model providers for convenience
def get_openrouter_provider(**kwargs):
    from .providers.model.openrouter import OpenRouterModelProvider
    return OpenRouterModelProvider(**kwargs)

# Execution providers convenience (newly added stubs)
def get_docker_execution_provider():
    from .providers.execution.docker import get_docker_provider
    return get_docker_provider()

def get_devcontainer_execution_provider():
    from .providers.execution.devcontainer import get_devcontainer_provider
    return get_devcontainer_provider()

# Experiment Lab
def get_experiment_lab():
    from . import experiment
    return experiment

# Queue (5 mover)
def get_agent_queue(workspace_id=None):
    from .queue import get_agent_queue
    return get_agent_queue(workspace_id)

# Minimal mission wrapper (Step 5 approved): create/attach/list with grouping of persistent run + ckpt + auto_pr status.
def create_mission(*a, **k):
    from .mission import create_mission as fn
    return fn(*a, **k)

def list_missions(*a, **k):
    from .mission import list_missions as fn
    return fn(*a, **k)

def get_mission(*a, **k):
    from .mission import get_mission as fn
    return fn(*a, **k)

def attach_run_to_mission(*a, **k):
    from .mission import attach_run_to_mission as fn
    return fn(*a, **k)

def attach_approval_to_mission(*a, **k):
    from .mission import attach_approval_to_mission as fn
    return fn(*a, **k)

def attach_handoff_to_mission(*a, **k):
    from .mission import attach_handoff_to_mission as fn
    return fn(*a, **k)

def enqueue_mission_task(*a, **k):
    from .mission import enqueue_mission_task as fn
    return fn(*a, **k)

from .mission import Mission as Mission  # class reexport for from aiw import Mission

# High-level memory for Step 5 self-improvement (Experiment Lab propose/test/adopt)
def store_high_level_improvement(*a, **k):
    from .memory import store_high_level_improvement as fn
    return fn(*a, **k)

def get_high_level_improvements(*a, **k):
    from .memory import get_high_level_improvements as fn
    return fn(*a, **k)

# Integração (github_intake, outbox, worker) - migrado
def run_github_intake(*a, **k):
    from .integration import run_github_intake as fn
    return fn(*a, **k)

def create_outbox_item(*a, **k):
    from .integration import create_outbox_item as fn
    return fn(*a, **k)

def run_worker(*a, **k):
    from .integration import run_worker as fn
    return fn(*a, **k)

# Patch / Evidence / Review Flow - migrado (evidence bundles, patch review lifecycle)
def create_evidence_bundle(*a, **k):
    from .patch import create_evidence_bundle as fn
    return fn(*a, **k)

def get_patch_review_flow(*a, **k):
    from .patch import get_patch_review_flow as fn
    return fn(*a, **k)

def discover_workspace_patches(*a, **k):
    from .patch import discover_workspace_patches as fn
    return fn(*a, **k)

# Step 1 migration: reexports for patch_gate (now local in aiw/patch) + changed_lines + other bridges + experiment
def review_gate_for_patch(*a, **k):
    from .patch import review_gate_for_patch as fn
    return fn(*a, **k)

def list_review_gates(*a, **k):
    from .patch import list_review_gates as fn
    return fn(*a, **k)

def apply_reviewed_patch(*a, **k):
    from .patch import apply_reviewed_patch as fn
    return fn(*a, **k)

def rollback_reviewed_patch(*a, **k):
    from .patch import rollback_reviewed_patch as fn
    return fn(*a, **k)

def validation_plan_for_patch(*a, **k):
    from .patch import validation_plan_for_patch as fn
    return fn(*a, **k)

def ensure_validation_plan_snapshot(*a, **k):
    from .patch import ensure_validation_plan_snapshot as fn
    return fn(*a, **k)

def list_validation_plan_snapshots(*a, **k):
    from .patch import list_validation_plan_snapshots as fn
    return fn(*a, **k)

def get_validation_plan_snapshot(*a, **k):
    from .patch import get_validation_plan_snapshot as fn
    return fn(*a, **k)

def compare_validation_plan_snapshots(*a, **k):
    from .patch import compare_validation_plan_snapshots as fn
    return fn(*a, **k)

def load_patch_preview(*a, **k):
    from .patch import load_patch_preview as fn
    return fn(*a, **k)

def analyze_changed_lines_coverage(*a, **k):
    from .patch import analyze_changed_lines_coverage as fn
    return fn(*a, **k)

# coverage
def analyze_patch_coverage(*a, **k):
    from .patch import analyze_patch_coverage as fn
    return fn(*a, **k)

def load_coverage_reports(*a, **k):
    from .patch import load_coverage_reports as fn
    return fn(*a, **k)

def capture_test_run_coverage(*a, **k):
    from .patch import capture_test_run_coverage as fn
    return fn(*a, **k)

def validation_reliability(*a, **k):
    from .patch import validation_reliability as fn
    return fn(*a, **k)

def preview_validation_plan_command(*a, **k):
    from .patch import preview_validation_plan_command as fn
    return fn(*a, **k)

def run_validation_plan_commands(*a, **k):
    from .patch import run_validation_plan_commands as fn
    return fn(*a, **k)

def run_benchmark(*a, **k):
    from .experiment import run_benchmark as fn
    return fn(*a, **k)

def run_arena(*a, **k):
    from .experiment import run_arena as fn
    return fn(*a, **k)

# Workspace helpers bridge (para preferir 'from aiw import ...' em scripts/cockpit durante migração)
# Lógica agora em aiw/workspace/profiles.py (migrado cirurgicamente); exposto via aiw/ namespace (aiw-first).
def resolve_workspace(*a, **k):
    from .workspace.profiles import resolve_workspace as fn
    return fn(*a, **k)

def load_workspaces_config(*a, **k):
    from .workspace.profiles import load_workspaces_config as fn
    return fn(*a, **k)

# Additional workspace profile symbols (aiw-first after profiles migration)
def validate_profile(*a, **k):
    from .workspace.profiles import validate_profile as fn
    return fn(*a, **k)

def validate_test_command(*a, **k):
    from .workspace.profiles import validate_test_command as fn
    return fn(*a, **k)

def execution_policy(*a, **k):
    from .workspace.profiles import execution_policy as fn
    return fn(*a, **k)

def load_external_worker_policy(*a, **k):
    from .workspace.external_worker_policy import load_external_worker_policy as fn
    return fn(*a, **k)

def validate_external_worker_policy(*a, **k):
    from .workspace.external_worker_policy import validate_external_worker_policy as fn
    return fn(*a, **k)

def can_worker_execute(*a, **k):
    from .workspace.external_worker_policy import can_worker_execute as fn
    return fn(*a, **k)

# Step 1 reexports (test/cov related + dispatcher/worker_loop related)
def preview_test_command(*a, **k):
    from .patch import preview_test_command as fn
    return fn(*a, **k)

def run_test_command(*a, **k):
    from .patch import run_test_command as fn
    return fn(*a, **k)

def get_test_run(*a, **k):
    from .patch import get_test_run as fn  # via patch reexp or direct
    try:
        from .patch.test_runner import get_test_run as fn2
        return fn2(*a, **k)
    except Exception:
        return fn(*a, **k)

def list_test_runs(*a, **k):
    from .patch.test_runner import list_test_runs as fn
    return fn(*a, **k)

def get_current_coverage_baseline(*a, **k):
    from .patch import get_current_coverage_baseline as fn
    return fn(*a, **k)

def promote_coverage_baseline(*a, **k):
    from .patch import promote_coverage_baseline as fn
    return fn(*a, **k)

def list_coverage_baselines(*a, **k):
    from .patch import list_coverage_baselines as fn
    return fn(*a, **k)

def coverage_diff(*a, **k):
    from .patch import coverage_diff as fn
    return fn(*a, **k)

def run_agent_dispatcher_once(*a, **k):
    from .queue.agent_dispatcher import run_agent_dispatcher_once as fn
    return fn(*a, **k)

def list_agent_dispatcher_runs(*a, **k):
    from .queue.agent_dispatcher import list_agent_dispatcher_runs as fn
    return fn(*a, **k)

def read_agent_dispatcher_run(*a, **k):
    from .queue.agent_dispatcher import read_agent_dispatcher_run as fn
    return fn(*a, **k)

def replay_agent_run(*a, **k):
    from .agent.iterative_loop import replay_agent_run as fn
    return fn(*a, **k)

__all__ = [
    "get_execution_provider_registry",
    "get_model_provider_registry",
    "get_context_provider_registry",
    "get_model_router",
    "get_capability_registry",
    "get_policy_engine",
    "evaluate_capability_policy",
    "get_capability_policy_profile",  # POLICY_PROFILE via aiw/ (surgical cap migration)
    "load_profile",
    "get_profile",
    "list_profiles",
    "run_agent_iterative_loop_once",
    "list_agent_loop_runs",
    "read_agent_loop_run",
    "get_openrouter_provider",
    "get_docker_execution_provider",
    "get_devcontainer_execution_provider",
    "get_experiment_lab",
    "get_agent_queue",
    # Step 5 (expanded): mission wrapper (multiple runs + approvals + queue tie-in)
    "create_mission",
    "list_missions",
    "get_mission",
    "attach_run_to_mission",
    "attach_approval_to_mission",
    "attach_handoff_to_mission",
    "enqueue_mission_task",
    "Mission",
    "store_high_level_improvement",
    "get_high_level_improvements",
    # migrated integration + patch/evidence
    "run_github_intake",
    "create_outbox_item",
    "run_worker",
    "create_evidence_bundle",
    "get_patch_review_flow",
    "discover_workspace_patches",
    # step 2: validation_plan + coverage_report (aiw/patch primary, reexported)
    # prior step 1: patch_gate + changed_lines_coverage reexports (aiw-first)
    "review_gate_for_patch",
    "list_review_gates",
    "apply_reviewed_patch",
    "rollback_reviewed_patch",
    "validation_plan_for_patch",
    "ensure_validation_plan_snapshot",
    "list_validation_plan_snapshots",
    "get_validation_plan_snapshot",
    "compare_validation_plan_snapshots",
    "validation_reliability",
    "preview_validation_plan_command",
    "run_validation_plan_commands",
    "load_patch_preview",
    "analyze_changed_lines_coverage",
    "analyze_patch_coverage",
    "load_coverage_reports",
    "capture_test_run_coverage",
    "run_benchmark",
    "run_arena",
    "resolve_workspace",
    "load_workspaces_config",
    "validate_profile",
    "validate_test_command",
    "execution_policy",
    "load_external_worker_policy",
    "validate_external_worker_policy",
    "can_worker_execute",
    # step 1 reexports
    "preview_test_command", "run_test_command", "get_test_run", "list_test_runs",
    "get_current_coverage_baseline", "promote_coverage_baseline", "list_coverage_baselines", "coverage_diff",
    "run_agent_dispatcher_once", "list_agent_dispatcher_runs", "read_agent_dispatcher_run",
    # Step 4 (Production Observability & Cost Control): structured logs, cost/token tracking, replay, global budgets
    "get_structured_logger", "log_structured",
    "record_iteration_cost", "get_run_metrics", "estimate_cost",
    "get_global_budget", "apply_global_budget_spend",
    "replay_session", "get_mission_metrics",
    "replay_agent_run",
]

# Observability reexports (aiw-first)
def get_structured_logger(*a, **k):
    from .observability import get_structured_logger as fn
    return fn(*a, **k)

def log_structured(*a, **k):
    from .observability import log_structured as fn
    return fn(*a, **k)

def record_iteration_cost(*a, **k):
    from .observability import record_iteration_cost as fn
    return fn(*a, **k)

def get_run_metrics(*a, **k):
    from .observability import get_run_metrics as fn
    return fn(*a, **k)

def estimate_cost(*a, **k):
    from .observability import estimate_cost as fn
    return fn(*a, **k)

def get_global_budget(*a, **k):
    from .observability import get_global_budget as fn
    return fn(*a, **k)

def apply_global_budget_spend(*a, **k):
    from .observability import apply_global_budget_spend as fn
    return fn(*a, **k)

def replay_session(*a, **k):
    from .observability import replay_session as fn
    return fn(*a, **k)

def get_mission_metrics(*a, **k):
    from .observability import get_mission_metrics as fn
    return fn(*a, **k)

