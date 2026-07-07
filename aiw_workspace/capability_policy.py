# Aligned: use new policy engine for evaluate (lazy)
def _get_new_policy():
    from aiw.policy.registry import get_policy_engine
    return get_policy_engine()

from .capability_registry import get_capability, validate_capability_definition
from .isolation_boundary import (
    FIXED_CODEACT_OPERATIONS,
    ISOLATION_PROFILE,
    KNOWN_ISOLATION_OPERATIONS,
    evaluate_isolation_boundary,
)


POLICY_PROFILE = "local_offline_v1"
KNOWN_OPERATIONS = set(KNOWN_ISOLATION_OPERATIONS)


def evaluate_capability_policy(
    workspace_id: str,
    capability_name: str,
    mode: str,
    operation: str = "python_eval_fixed",
    confirmed: bool = False,
    fixed_code: bool = False,
    local_execution: bool = True,
    tracked: bool = True,
) -> dict:
    # Aligned: prefer new policy engine
    try:
        return _get_new_policy().evaluate_capability(
            workspace_id, capability_name, mode=mode, operation=operation,
            confirmed=confirmed, fixed_code=fixed_code, local_execution=local_execution, tracked=tracked
        )
    except Exception:
        pass  # fallback to local impl below

    cap = get_capability(capability_name)
    decision = {
        "workspace_id": workspace_id,
        "capability": capability_name,
        "allowed": False,
        "mode": mode,
        "operation": operation,
        "policy_profile": POLICY_PROFILE,
        "risk": None,
        "requires_confirmation": True,
        "confirmed": bool(confirmed),
        "runs_code": False,
        "writes_files": False,
        "external_io": False,
        "blocked_by_default": True,
        "dry_run": mode == "dry-run",
        "simulation_only": False,
        "capability_not_executed": True,
        "reason": None,
        "isolation_profile": ISOLATION_PROFILE,
        "isolation_allowed": False,
        "isolation_reason": None,
        "isolation_decision": None,
        "runtime_decision": None,
        "runtime_required": None,
        "runtime_profile": None,
        "runtime_allowed": False,
        "requires_stronger_runtime": True,
        "requires_devcontainer": False,
        "requires_vm": False,
        "requires_stronger_isolation_before_llm": True,
        "llm_real_allowed": False,
        "dynamic_code_allowed": False,
        "shell_allowed": False,
        "network_allowed": False,
        "external_write_allowed": False,
        "localhost_http_allowed": True,
    }

    if not cap:
        decision["reason"] = "capability_missing"
        return decision

    decision.update({
        "risk": cap.get("risk"),
        "requires_confirmation": bool(cap.get("requires_confirmation", True)),
        "runs_code": bool(cap.get("runs_code")),
        "writes_files": bool(cap.get("writes_files")),
        "external_io": bool(cap.get("allows_external_io") or cap.get("network_access")),
        "blocked_by_default": bool(cap.get("blocked_by_default", True)),
    })

    if not validate_capability_definition(cap):
        decision["reason"] = "capability_invalid"
        return decision

    if operation not in KNOWN_OPERATIONS:
        decision["reason"] = "unknown_operation"
        return decision

    isolation_operation = operation
    if mode == "llm" and operation in FIXED_CODEACT_OPERATIONS:
        isolation_operation = "llm_planner"
    isolation_decision = evaluate_isolation_boundary(
        operation=isolation_operation,
        mode=mode,
        confirmed=confirmed,
        fixed_code=fixed_code,
        local_execution=local_execution,
        tracked=tracked,
    )
    decision.update({
        "isolation_profile": isolation_decision.get("isolation_profile"),
        "isolation_allowed": bool(isolation_decision.get("allowed")),
        "isolation_reason": isolation_decision.get("reason"),
        "isolation_decision": isolation_decision,
        "runtime_decision": isolation_decision.get("runtime_decision"),
        "runtime_required": isolation_decision.get("runtime_required"),
        "runtime_profile": isolation_decision.get("runtime_profile"),
        "runtime_allowed": bool(isolation_decision.get("runtime_allowed")),
        "requires_stronger_runtime": bool(isolation_decision.get("requires_stronger_runtime")),
        "requires_devcontainer": bool(isolation_decision.get("requires_devcontainer")),
        "requires_vm": bool(isolation_decision.get("requires_vm")),
        "requires_stronger_isolation_before_llm": not bool(isolation_decision.get("llm_real_allowed")),
        "llm_real_allowed": bool(isolation_decision.get("llm_real_allowed")),
        "dynamic_code_allowed": bool(isolation_decision.get("dynamic_code_allowed")),
        "shell_allowed": bool(isolation_decision.get("shell_allowed")),
        "network_allowed": bool(isolation_decision.get("network_allowed")),
        "external_write_allowed": bool(isolation_decision.get("external_write_allowed")),
        "localhost_http_allowed": bool(isolation_decision.get("localhost_http_allowed")),
    })

    if mode == "dry-run" and not isolation_decision.get("allowed"):
        decision["reason"] = isolation_decision.get("reason") or "isolation_blocked"
        return decision

    if mode == "dry-run":
        decision["allowed"] = True
        decision["simulation_only"] = True
        decision["capability_not_executed"] = True
        decision["reason"] = "dry_run_simulation"
        return decision

    if mode == "llm":
        decision["reason"] = isolation_decision.get("reason") or "stronger_isolation_required"
        return decision

    if mode != "offline":
        decision["reason"] = "unsupported_mode"
        return decision

    if operation not in FIXED_CODEACT_OPERATIONS:
        decision["reason"] = isolation_decision.get("reason") or "isolation_blocked"
        return decision

    if decision["external_io"]:
        decision["reason"] = "external_io_blocked"
        return decision

    if decision["requires_confirmation"] and not confirmed:
        decision["reason"] = "confirmation_required"
        return decision

    if decision["runs_code"] and not confirmed:
        decision["reason"] = "runs_code_requires_confirmation"
        return decision

    if decision["blocked_by_default"] and not confirmed:
        decision["reason"] = "blocked_by_default_requires_confirmation"
        return decision

    if not isolation_decision.get("allowed"):
        decision["reason"] = isolation_decision.get("reason") or "isolation_blocked"
        return decision

    if capability_name == "codeact_sandbox" and operation in FIXED_CODEACT_OPERATIONS and fixed_code and local_execution and tracked:
        decision["allowed"] = True
        decision["capability_not_executed"] = False
        decision["reason"] = "offline_confirmed_fixed_codeact_eval"
        return decision

    if decision["blocked_by_default"]:
        decision["reason"] = "blocked_by_default"
        return decision

    decision["allowed"] = True
    decision["reason"] = "offline_confirmed_local_tracked"
    return decision


def assert_capability_allowed(**kwargs) -> dict:
    decision = evaluate_capability_policy(**kwargs)
    if not decision.get("allowed"):
        raise PermissionError(decision.get("reason") or "capability_blocked")
    return decision
