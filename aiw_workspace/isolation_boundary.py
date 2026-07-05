from .runtime_gate import (
    FIXED_CODEACT_OPERATIONS,
    KNOWN_RUNTIME_OPERATIONS,
    RUNTIME_PROFILE,
    RUNTIME_PROFILES,
    evaluate_runtime_gate,
)

ISOLATION_PROFILE = RUNTIME_PROFILE
ISOLATION_PROFILES = tuple(RUNTIME_PROFILES)
KNOWN_ISOLATION_OPERATIONS = {
    *KNOWN_RUNTIME_OPERATIONS,
}


def _base_decision(operation: str, isolation_profile: str) -> dict:
    return {
        "isolation_profile": isolation_profile,
        "operation": operation,
        "allowed": False,
        "reason": None,
        "runtime_decision": None,
        "runtime_required": isolation_profile,
        "runtime_profile": None,
        "runtime_allowed": False,
        "requires_stronger_runtime": False,
        "requires_devcontainer": False,
        "requires_vm": False,
        "llm_real_allowed": False,
        "dynamic_code_allowed": False,
        "shell_allowed": False,
        "network_allowed": False,
        "external_write_allowed": False,
        "localhost_http_allowed": True,
    }


def evaluate_isolation_boundary(
    operation: str,
    mode: str = "offline",
    confirmed: bool = False,
    fixed_code: bool = False,
    local_execution: bool = True,
    tracked: bool = True,
    isolation_profile: str = ISOLATION_PROFILE,
) -> dict:
    """Return a serializable isolation gate decision without executing anything."""
    decision = _base_decision(operation, isolation_profile)

    if isolation_profile not in ISOLATION_PROFILES:
        decision["reason"] = "unknown_isolation_profile"
        decision["requires_devcontainer"] = True
        return decision

    if operation not in KNOWN_ISOLATION_OPERATIONS:
        decision["reason"] = "unknown_operation"
        return decision

    runtime_decision = evaluate_runtime_gate(
        operation=operation,
        mode=mode,
        requires_confirmation=True,
        writes_files=operation == "external_write",
        runs_code=operation in {
            *FIXED_CODEACT_OPERATIONS,
            "dynamic_codeact_python_eval",
            "shell_command",
        },
        external_io=operation == "network_access",
        dynamic_code=operation == "dynamic_codeact_python_eval",
        llm=operation == "llm_planner" or mode == "llm",
        shell=operation == "shell_command",
    )
    decision.update({
        "runtime_decision": runtime_decision,
        "runtime_required": runtime_decision.get("runtime_required"),
        "runtime_profile": runtime_decision.get("runtime_profile"),
        "runtime_allowed": bool(runtime_decision.get("allowed")),
        "requires_stronger_runtime": bool(runtime_decision.get("requires_stronger_runtime")),
        "requires_devcontainer": runtime_decision.get("runtime_required") == "devcontainer",
        "requires_vm": runtime_decision.get("runtime_required") == "vm",
    })

    if operation in FIXED_CODEACT_OPERATIONS:
        if mode == "dry-run":
            decision["allowed"] = True
            decision["reason"] = "dry_run_no_execution"
            return decision
        if (
            mode == "offline"
            and confirmed
            and fixed_code
            and local_execution
            and tracked
            and isolation_profile == "host_best_effort"
        ):
            decision["allowed"] = True
            decision["reason"] = "host_best_effort_fixed_code_confirmed"
            return decision
        decision["reason"] = "fixed_codeact_requires_offline_confirmation"
        return decision

    if operation in {"dynamic_codeact_python_eval", "llm_planner"}:
        decision["reason"] = "stronger_isolation_required"
        decision["requires_devcontainer"] = True
        return decision

    if operation == "shell_command":
        decision["reason"] = "shell_blocked_by_isolation_boundary"
        decision["requires_devcontainer"] = True
        return decision

    if operation == "network_access":
        decision["reason"] = "external_network_blocked"
        decision["requires_devcontainer"] = True
        return decision

    if operation == "external_write":
        decision["reason"] = "external_write_blocked"
        decision["requires_devcontainer"] = True
        return decision

    decision["reason"] = "blocked_by_isolation_boundary"
    return decision


def assert_isolation_allowed(**kwargs) -> dict:
    decision = evaluate_isolation_boundary(**kwargs)
    if not decision.get("allowed"):
        raise PermissionError(decision.get("reason") or "isolation_blocked")
    return decision
