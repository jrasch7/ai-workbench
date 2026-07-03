from .capability_registry import get_capability, validate_capability_definition


def evaluate_capability_policy(
    workspace_id: str,
    capability_name: str,
    mode: str,
    confirmed: bool = False,
    fixed_code: bool = False,
    local_execution: bool = True,
    tracked: bool = True,
) -> dict:
    cap = get_capability(capability_name)
    decision = {
        "workspace_id": workspace_id,
        "capability": capability_name,
        "allowed": False,
        "mode": mode,
        "risk": None,
        "requires_confirmation": True,
        "confirmed": bool(confirmed),
        "runs_code": False,
        "writes_files": False,
        "external_io": False,
        "blocked_by_default": True,
        "dry_run": mode == "dry-run",
        "reason": None,
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

    if mode == "dry-run":
        decision["allowed"] = True
        decision["reason"] = "dry_run_simulation"
        return decision

    if mode != "offline":
        decision["reason"] = "unsupported_mode"
        return decision

    if decision["external_io"]:
        decision["reason"] = "external_io_blocked"
        return decision

    if decision["requires_confirmation"] and not confirmed:
        decision["reason"] = "confirmation_required"
        return decision

    if capability_name == "codeact_sandbox" and fixed_code and local_execution and tracked:
        decision["allowed"] = True
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
