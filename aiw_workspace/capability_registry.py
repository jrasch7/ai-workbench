# Capability Registry (v1 Foundation)
# This module currently holds only metadata schemas and policies for Agent Capabilities.
# Execution logic remains decoupled until the Tool Registry and Agent Loop are finalized.

def list_default_capabilities() -> list[dict]:
    """Returns a list of static baseline capabilities for the AI Workbench."""
    return [
        {
            "name": "file_read",
            "kind": "tool",
            "status": "available",
            "risk": "low",
            "requires_confirmation": False,
            "allows_external_io": False,
            "writes_files": False,
            "runs_code": False,
            "network_access": False,
            "artifacts_path": ".aiw/tools/file_read"
        },
        {
            "name": "file_write",
            "kind": "tool",
            "status": "available",
            "risk": "medium",
            "requires_confirmation": True,
            "allows_external_io": False,
            "writes_files": True,
            "runs_code": False,
            "network_access": False,
            "artifacts_path": ".aiw/tools/file_write"
        },
        {
            "name": "shell_exec",
            "kind": "action",
            "status": "available",
            "risk": "high",
            "requires_confirmation": True,
            "allows_external_io": True,
            "writes_files": True,
            "runs_code": True,
            "network_access": True,
            "artifacts_path": ".aiw/tools/shell_exec"
        },
        {
            "name": "context_rag",
            "kind": "context",
            "status": "planned",
            "risk": "low",
            "requires_confirmation": False,
            "allows_external_io": False,
            "writes_files": False,
            "runs_code": False,
            "network_access": False,
            "artifacts_path": ".aiw/context"
        },
        {
            "name": "codeact_sandbox",
            "kind": "sandbox",
            "status": "planned",
            "risk": "high",
            "requires_confirmation": True,
            "allows_external_io": True,
            "writes_files": True,
            "runs_code": True,
            "network_access": False,
            "artifacts_path": ".aiw/sandbox"
        }
    ]

def validate_capability_definition(capability: dict) -> bool:
    """Validates if a capability dictionary conforms to the expected V1 schema."""
    required_keys = {
        "name", "kind", "status", "risk", "requires_confirmation",
        "allows_external_io", "writes_files", "runs_code", "network_access",
        "artifacts_path"
    }
    return required_keys.issubset(capability.keys())

def classify_capability_risk(capability: dict) -> str:
    """Classifies risk strictly based on the defined properties."""
    if capability.get("runs_code") or capability.get("network_access"):
        return "high"
    if capability.get("writes_files"):
        return "medium"
    return capability.get("risk", "low")
