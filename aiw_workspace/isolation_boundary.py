ISOLATION_PROFILE = "host_best_effort"
ISOLATION_PROFILES = ("host_best_effort", "devcontainer_required", "vm_required")

FIXED_CODEACT_OPERATIONS = {"python_eval_fixed", "fixed_codeact_python_eval"}
KNOWN_ISOLATION_OPERATIONS = {
    *FIXED_CODEACT_OPERATIONS,
    "dynamic_codeact_python_eval",
    "llm_planner",
    "shell_command",
    "network_access",
    "external_write",
}


def _base_decision(operation: str, isolation_profile: str) -> dict:
    return {
        "isolation_profile": isolation_profile,
        "operation": operation,
        "allowed": False,
        "reason": None,
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
        return decision

    if operation == "external_write":
        decision["reason"] = "external_write_blocked"
        return decision

    decision["reason"] = "blocked_by_isolation_boundary"
    return decision


def assert_isolation_allowed(**kwargs) -> dict:
    decision = evaluate_isolation_boundary(**kwargs)
    if not decision.get("allowed"):
        raise PermissionError(decision.get("reason") or "isolation_blocked")
    return decision
