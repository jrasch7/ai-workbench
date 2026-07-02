# Tool Registry (v1)
# This module defines the static tool and capability registry for AI Workbench.

import json

def _capabilities_db() -> list[dict]:
    return [
        {
            "name": "file_read",
            "kind": "tool",
            "status": "available",
            "risk": "low",
            "description": "Reads the content of a file up to a size limit.",
            "requires_confirmation": False,
            "allows_external_io": False,
            "writes_files": False,
            "runs_code": False,
            "network_access": False,
            "modifies_git": False,
            "reads_secrets": False,
            "artifacts_path": ".aiw/tools/file_read",
            "input_schema": {"path": "string", "max_bytes": "integer"},
            "blocked_by_default": False,
            "allowed_modes": ["dry_run", "manual", "auto"],
            "source": "aiw_runtime.tools"
        },
        {
            "name": "codeact_sandbox",
            "kind": "action",
            "status": "experimental",
            "risk": "high",
            "requires_confirmation": True,
            "allows_external_io": False,
            "writes_files": True,
            "runs_code": True,
            "network_access": False,
            "modifies_git": False,
            "reads_secrets": False,
            "blocked_by_default": True,
            "allowed_modes": ["manual"],
            "source": "aiw_workspace.codeact_sandbox"
        },
        {
            "name": "file_write",
            "kind": "tool",
            "status": "available",
            "risk": "medium",
            "description": "Writes or overwrites content to a file.",
            "requires_confirmation": True,
            "allows_external_io": False,
            "writes_files": True,
            "runs_code": False,
            "network_access": False,
            "modifies_git": False,
            "reads_secrets": False,
            "artifacts_path": ".aiw/tools/file_write",
            "input_schema": {"path": "string", "content": "string", "overwrite": "boolean"},
            "blocked_by_default": False,
            "allowed_modes": ["manual", "auto"],
            "source": "aiw_runtime.tools"
        },
        {
            "name": "file_patch",
            "kind": "tool",
            "status": "available",
            "risk": "medium",
            "description": "Replaces specific strings within a file.",
            "requires_confirmation": True,
            "allows_external_io": False,
            "writes_files": True,
            "runs_code": False,
            "network_access": False,
            "modifies_git": False,
            "reads_secrets": False,
            "artifacts_path": ".aiw/tools/file_patch",
            "input_schema": {"path": "string", "old_text": "string", "new_text": "string", "expected_replacements": "integer"},
            "blocked_by_default": False,
            "allowed_modes": ["manual", "auto"],
            "source": "aiw_runtime.tools"
        },
        {
            "name": "shell_exec",
            "kind": "tool",
            "status": "available",
            "risk": "high",
            "description": "Executes shell commands in a constrained environment.",
            "requires_confirmation": True,
            "allows_external_io": True,
            "writes_files": True,
            "runs_code": True,
            "network_access": True,
            "modifies_git": True,
            "reads_secrets": False,
            "artifacts_path": ".aiw/tools/shell_exec",
            "input_schema": {"command": "string", "timeout": "integer"},
            "blocked_by_default": False,
            "allowed_modes": ["manual", "auto"],
            "source": "aiw_runtime.tools"
        },
        {
            "name": "project_patch_preview",
            "kind": "tool",
            "status": "available",
            "risk": "medium",
            "description": "Previews a change without applying it to the project directly.",
            "requires_confirmation": False,
            "allows_external_io": False,
            "writes_files": True,
            "runs_code": False,
            "network_access": False,
            "modifies_git": False,
            "reads_secrets": False,
            "artifacts_path": ".aiw/patches",
            "input_schema": {"path": "string", "old_text": "string", "new_text": "string", "expected_replacements": "integer", "reason": "string"},
            "blocked_by_default": False,
            "allowed_modes": ["dry_run", "manual", "auto"],
            "source": "aiw_runtime.tools"
        },
        {
            "name": "project_patch_apply",
            "kind": "tool",
            "status": "available",
            "risk": "high",
            "description": "Applies a previously generated project patch preview.",
            "requires_confirmation": True,
            "allows_external_io": False,
            "writes_files": True,
            "runs_code": False,
            "network_access": False,
            "modifies_git": False,
            "reads_secrets": False,
            "artifacts_path": ".aiw/patches",
            "input_schema": {"patch_id": "string"},
            "blocked_by_default": False,
            "allowed_modes": ["manual"],
            "source": "aiw_runtime.tools"
        },
        {
            "name": "project_patch_rollback",
            "kind": "tool",
            "status": "available",
            "risk": "high",
            "description": "Rollbacks a previously applied project patch.",
            "requires_confirmation": True,
            "allows_external_io": False,
            "writes_files": True,
            "runs_code": False,
            "network_access": False,
            "modifies_git": False,
            "reads_secrets": False,
            "artifacts_path": ".aiw/patches",
            "input_schema": {"patch_id": "string"},
            "blocked_by_default": False,
            "allowed_modes": ["manual"],
            "source": "aiw_runtime.tools"
        },
        {
            "name": "validation_plan",
            "kind": "workflow",
            "status": "available",
            "risk": "medium",
            "description": "Generates and orchestrates a validation plan for patches.",
            "requires_confirmation": True,
            "allows_external_io": False,
            "writes_files": True,
            "runs_code": True,
            "network_access": False,
            "modifies_git": False,
            "reads_secrets": False,
            "artifacts_path": ".aiw/validation-plans",
            "input_schema": {"patch_id": "string"},
            "blocked_by_default": False,
            "allowed_modes": ["manual"],
            "source": "aiw_workspace.validation_plan"
        },
        {
            "name": "review_gate",
            "kind": "workflow",
            "status": "available",
            "risk": "low",
            "description": "Checks multiple validation dimensions before a patch is approved.",
            "requires_confirmation": False,
            "allows_external_io": False,
            "writes_files": False,
            "runs_code": False,
            "network_access": False,
            "modifies_git": False,
            "reads_secrets": False,
            "artifacts_path": ".aiw/review-gates",
            "input_schema": {"patch_id": "string"},
            "blocked_by_default": False,
            "allowed_modes": ["dry_run", "manual"],
            "source": "aiw_workspace.patch_gate"
        },
        {
            "name": "evidence_bundle",
            "kind": "workflow",
            "status": "available",
            "risk": "medium",
            "description": "Creates bundles of evidence for completed processes.",
            "requires_confirmation": False,
            "allows_external_io": False,
            "writes_files": True,
            "runs_code": False,
            "network_access": False,
            "modifies_git": False,
            "reads_secrets": False,
            "artifacts_path": ".aiw/evidence-bundles",
            "input_schema": {"patch_id": "string"},
            "blocked_by_default": False,
            "allowed_modes": ["dry_run", "manual"],
            "source": "aiw_workspace.evidence_bundle"
        },
        {
            "name": "evidence_export",
            "kind": "workflow",
            "status": "available",
            "risk": "medium",
            "description": "Exports an evidence bundle into a portable format.",
            "requires_confirmation": False,
            "allows_external_io": False,
            "writes_files": True,
            "runs_code": False,
            "network_access": False,
            "modifies_git": False,
            "reads_secrets": False,
            "artifacts_path": ".aiw/evidence-exports",
            "input_schema": {"patch_id": "string", "bundle_id": "string"},
            "blocked_by_default": False,
            "allowed_modes": ["dry_run", "manual"],
            "source": "aiw_workspace.evidence_export"
        },
        {
            "name": "integration_outbox",
            "kind": "workflow",
            "status": "available",
            "risk": "high",
            "description": "Manages items ready to be exported to external integrations.",
            "requires_confirmation": True,
            "allows_external_io": True,
            "writes_files": True,
            "runs_code": False,
            "network_access": True,
            "modifies_git": False,
            "reads_secrets": False,
            "artifacts_path": ".aiw/outbox",
            "input_schema": {"patch_id": "string", "target": "string", "kind": "string"},
            "blocked_by_default": False,
            "allowed_modes": ["manual"],
            "source": "aiw_workspace.integration_outbox"
        },
        {
            "name": "worker_loop",
            "kind": "workflow",
            "status": "available",
            "risk": "high",
            "description": "Loop that executes actions from the outbox.",
            "requires_confirmation": True,
            "allows_external_io": True,
            "writes_files": True,
            "runs_code": True,
            "network_access": True,
            "modifies_git": True,
            "reads_secrets": False,
            "artifacts_path": ".aiw/worker-runs",
            "input_schema": {},
            "blocked_by_default": False,
            "allowed_modes": ["manual"],
            "source": "aiw_workspace.worker_loop"
        },
        {
            "name": "agent_queue",
            "kind": "workflow",
            "status": "available",
            "risk": "low",
            "description": "Manages tasks queued for agent execution.",
            "requires_confirmation": False,
            "allows_external_io": False,
            "writes_files": True,
            "runs_code": False,
            "network_access": False,
            "modifies_git": False,
            "reads_secrets": False,
            "artifacts_path": ".aiw/queue",
            "input_schema": {"inbox_item_id": "string"},
            "blocked_by_default": False,
            "allowed_modes": ["dry_run", "manual"],
            "source": "aiw_workspace.agent_queue"
        },
        {
            "name": "agent_dispatcher",
            "kind": "workflow",
            "status": "available",
            "risk": "high",
            "description": "Dispatches tasks from queue to local runners or LLMs.",
            "requires_confirmation": True,
            "allows_external_io": False,
            "writes_files": True,
            "runs_code": True,
            "network_access": False,
            "modifies_git": False,
            "reads_secrets": False,
            "artifacts_path": ".aiw/dispatcher-runs",
            "input_schema": {},
            "blocked_by_default": False,
            "allowed_modes": ["manual", "auto"],
            "source": "aiw_workspace.agent_dispatcher"
        }
    ]

def list_capabilities() -> list[dict]:
    """Returns all registered capabilities (tools, workflows, sandboxes, etc)."""
    return _capabilities_db()

def list_tools() -> list[dict]:
    """Returns all registered capabilities of kind 'tool'."""
    return filter_capabilities(kind="tool")

def get_capability(name: str) -> dict | None:
    """Returns a specific capability by name, or None if not found."""
    for cap in _capabilities_db():
        if cap["name"] == name:
            return cap
    return None

def validate_capability_definition(capability: dict) -> bool:
    """Validates if a capability dictionary conforms to the expected V1 schema."""
    required_keys = {
        "name", "kind", "status", "risk", "description", "requires_confirmation",
        "allows_external_io", "writes_files", "runs_code", "network_access",
        "modifies_git", "reads_secrets", "artifacts_path", "input_schema",
        "blocked_by_default", "allowed_modes", "source"
    }
    if not required_keys.issubset(capability.keys()):
        return False

    if capability.get("reads_secrets") is True:
        return False

    return True

def classify_capability_risk(capability: dict) -> str:
    """Classifies risk based on defined properties. Follows strict policy."""
    if capability.get("runs_code") or capability.get("network_access") or capability.get("modifies_git") or capability.get("allows_external_io") or capability.get("name") in ["project_patch_apply", "project_patch_rollback"]:
        return "high"
    if capability.get("writes_files") or capability.get("name") == "project_patch_preview":
        return "medium"
    return "low"

def filter_capabilities(kind: str = None, status: str = None, risk: str = None) -> list[dict]:
    """Filters capabilities based on kind, status, or risk."""
    results = _capabilities_db()
    if kind:
        results = [c for c in results if c["kind"] == kind]
    if status:
        results = [c for c in results if c["status"] == status]
    if risk:
        results = [c for c in results if c["risk"] == risk]
    return results

def capability_requires_confirmation(name: str) -> bool:
    """Checks if a capability requires explicit confirmation to run."""
    cap = get_capability(name)
    if not cap:
        return True # Default to safe
    return cap.get("requires_confirmation", True)

def capability_allows_external_io(name: str) -> bool:
    """Checks if a capability allows external I/O."""
    cap = get_capability(name)
    if not cap:
        return False
    return cap.get("allows_external_io", False)

def capability_writes_files(name: str) -> bool:
    """Checks if a capability writes to files."""
    cap = get_capability(name)
    if not cap:
        return False
    return cap.get("writes_files", False)

def capability_runs_code(name: str) -> bool:
    """Checks if a capability runs arbitrary code."""
    cap = get_capability(name)
    if not cap:
        return False
    return cap.get("runs_code", False)

def export_capabilities_manifest() -> dict:
    """Exports a structured manifest of all capabilities."""
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
