# Tool Registry (v1) - legacy, now delegates to aligned aiw/policy
# Data lives in aiw/policy/capabilities.py to avoid duplication.

def _get_reg():
    from aiw.policy.registry import get_capability_registry
    return get_capability_registry()

def _capabilities_db() -> list[dict]:
    return _get_reg().list_all()

def list_capabilities() -> list[dict]:
    return _get_reg().list_all()

def list_tools() -> list[dict]:
    return [c for c in _get_reg().list_all() if c.get("kind") == "tool"]

def get_capability(name: str) -> dict | None:
    return _get_reg().get(name)

def validate_capability_definition(capability: dict) -> bool:
    return _get_reg().validate(capability)
    return _get_reg().validate(capability)

def classify_capability_risk(capability: dict) -> str:
    if capability.get("runs_code") or capability.get("network_access") or capability.get("modifies_git") or capability.get("allows_external_io") or capability.get("name") in ["project_patch_apply", "project_patch_rollback"]:
        return "high"
    if capability.get("writes_files") or capability.get("name") == "project_patch_preview":
        return "medium"
    return "low"

def filter_capabilities(kind: str = None, status: str = None, risk: str = None) -> list[dict]:
    results = _get_reg().list_all()
    if kind:
        results = [c for c in results if c["kind"] == kind]
    if status:
        results = [c for c in results if c["status"] == status]
    if risk:
        results = [c for c in results if c["risk"] == risk]
    return results

def capability_requires_confirmation(name: str) -> bool:
    cap = get_capability(name)
    if not cap:
        return True
    return cap.get("requires_confirmation", True)

def capability_allows_external_io(name: str) -> bool:
    cap = get_capability(name)
    if not cap:
        return False
    return cap.get("allows_external_io", False)

def capability_writes_files(name: str) -> bool:
    cap = get_capability(name)
    if not cap:
        return False
    return cap.get("writes_files", False)

def capability_runs_code(name: str) -> bool:
    cap = get_capability(name)
    if not cap:
        return False
    return cap.get("runs_code", False)

def export_capabilities_manifest() -> dict:
    caps = list_capabilities()
    by_kind = {}
    by_risk = {}
    requires_conf = 0
    blocked_def = 0
    for c in caps:
        k = c.get("kind", "unknown")
        r = c.get("risk", "unknown")
        by_kind[k] = by_kind.get(k, 0) + 1
        by_risk[r] = by_risk.get(r, 0) + 1
        if c.get("requires_confirmation"):
            requires_conf += 1
        if c.get("blocked_by_default"):
            blocked_def += 1
    return {
        "version": 1,
        "capabilities": caps,
        "summary": {
            "total": len(caps),
            "by_kind": by_kind,
            "by_risk": by_risk,
            "requires_confirmation": requires_conf,
            "blocked_by_default": blocked_def
        }
    }
