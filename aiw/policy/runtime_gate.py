"""Runtime Gate (Porta de Runtime / Avaliação de Runtime).

Lógica principal migrada cirurgicamente para aiw/policy/ (target).
aiw_workspace/runtime_gate.py agora é thin delegate (compat total).

Usado por PolicyEngine no caminho do Loop Iterativo do Agente + Cockpit (via registry).
Mantém gates para Execução Real vs dry-run, profiles de runtime (host, devcontainer, docker).
Termos PT: Porta de Runtime, Perfil de Runtime, Execução Real, Loop Iterativo do Agente.

NÃO altera lógica de decisão; apenas reorganização + delegates.
"""

from typing import Any, Dict, Optional
from pathlib import Path


def is_trusted_ws(workspace_id: Optional[str]) -> bool:
    """aiw-first helper (dupe minimal to avoid cycles): relax for ws=="aiw" e.g. network_access in host for trusted.
    (full in registry; used here for runtime_gate polish). Still gated overall.
    """
    ws = str(workspace_id or "").strip()
    return ws == "aiw"

RUNTIME_PROFILE = "host_best_effort"
RUNTIME_PROFILES: Dict[str, Dict[str, Any]] = {
    "host_best_effort": {
        "name": "host_best_effort",
        "kind": "host",
        "available": True,
        "allowed_this_sprint": True,
        "strong_isolation": False,
        "description": "Local host best-effort guardrails only; not strong isolation.",
    },
    "devcontainer": {
        "name": "devcontainer",
        "kind": "container",
        "available": True,
        "allowed_this_sprint": True,
        "strong_isolation": True,
        "description": "Devcontainer target (stub + planned full adapter). Strong isolation.",
    },
    "docker": {
        "name": "docker",
        "kind": "container",
        "available": True,
        "allowed_this_sprint": True,
        "strong_isolation": True,
        "description": "Docker target (stub + planned full adapter). Strong isolation.",
    },
    "vm": {
        "name": "vm",
        "kind": "virtual_machine",
        "available": False,
        "allowed_this_sprint": False,
        "strong_isolation": True,
        "description": "Future VM target; metadata only in this sprint.",
    },
}

FIXED_CODEACT_OPERATIONS = {"python_eval_fixed", "fixed_codeact_python_eval"}
KNOWN_RUNTIME_OPERATIONS = {
    *FIXED_CODEACT_OPERATIONS,
    "dynamic_codeact_python_eval",
    "llm_planner",
    "shell_command",
    "network_access",
    "external_write",
}


def _profile(name: str) -> dict:
    return dict(RUNTIME_PROFILES[name])


def _base_decision(
    capability: str | None,
    operation: str,
    mode: str,
    runtime_required: str = RUNTIME_PROFILE,
) -> dict:
    profile = _profile(runtime_required)
    return {
        "capability": capability,
        "operation": operation,
        "mode": mode,
        "allowed": False,
        "runtime_allowed": False,
        "runtime_required": runtime_required,
        "runtime_profile": profile,
        "blocked_reason": None,
        "requires_stronger_runtime": runtime_required != RUNTIME_PROFILE,
        "profiles": {name: _profile(name) for name in RUNTIME_PROFILES},
        "requires_confirmation": False,
        "writes_files": False,
        "runs_code": False,
        "external_io": False,
        "dynamic_code": False,
        "llm": False,
        "shell": False,
    }


def _block(
    decision: dict,
    runtime_required: str,
    blocked_reason: str,
) -> dict:
    decision["runtime_required"] = runtime_required
    decision["runtime_profile"] = _profile(runtime_required)
    decision["blocked_reason"] = blocked_reason
    decision["requires_stronger_runtime"] = runtime_required != RUNTIME_PROFILE
    decision["allowed"] = False
    decision["runtime_allowed"] = False
    return decision


def evaluate_runtime_gate(
    capability: str | None = None,
    operation: str = "python_eval_fixed",
    mode: str = "offline",
    requires_confirmation: bool = False,
    writes_files: bool = False,
    runs_code: bool = False,
    external_io: bool = False,
    dynamic_code: bool = False,
    llm: bool = False,
    shell: bool = False,
    workspace_id: Optional[str] = None,  # step 5: ws context for trusted aiw relax
) -> dict:
    """Return the runtime needed for an operation without executing anything.

    Porta de Runtime usada pelo Loop Iterativo do Agente (policy checks em Execução Real).
    """
    decision = _base_decision(capability, operation, mode)
    decision.update({
        "requires_confirmation": bool(requires_confirmation),
        "writes_files": bool(writes_files),
        "runs_code": bool(runs_code),
        "external_io": bool(external_io),
        "dynamic_code": bool(dynamic_code),
        "llm": bool(llm),
        "shell": bool(shell),
    })

    if operation not in KNOWN_RUNTIME_OPERATIONS:
        return _block(decision, "devcontainer", "unknown_operation")

    if bool(shell) or operation == "shell_command":
        return _block(decision, "devcontainer", "shell_requires_devcontainer")

    if bool(llm) or mode == "llm" or operation == "llm_planner":
        return _block(decision, "devcontainer", "llm_requires_devcontainer")

    if bool(dynamic_code) or operation == "dynamic_codeact_python_eval":
        return _block(decision, "devcontainer", "dynamic_code_requires_devcontainer")

    if operation == "external_write":
        return _block(decision, "devcontainer", "external_write_requires_devcontainer")

    if bool(external_io) or operation == "network_access":
        if is_trusted_ws(workspace_id):
            # relax for trusted aiw ws (policy polish): allow host for network in persistent/success paths etc.
            # still gated overall (cap/network_access checked upstream in policy engine + loop)
            decision["allowed"] = True
            decision["runtime_allowed"] = True
            decision["runtime_required"] = RUNTIME_PROFILE
            decision["runtime_profile"] = _profile(RUNTIME_PROFILE)
            decision["blocked_reason"] = None
            decision["requires_stronger_runtime"] = False
            decision["trusted_ws_relax"] = True
            decision["note"] = "network relaxed for aiw trusted ws (gated by cap)"
            return decision
        return _block(decision, "devcontainer", "external_network_requires_devcontainer")

    if operation in FIXED_CODEACT_OPERATIONS:
        decision["allowed"] = True
        decision["runtime_allowed"] = True
        decision["runtime_required"] = RUNTIME_PROFILE
        decision["runtime_profile"] = _profile(RUNTIME_PROFILE)
        decision["blocked_reason"] = None
        decision["requires_stronger_runtime"] = False
        return decision

    return _block(decision, "devcontainer", "operation_requires_devcontainer")


def assert_runtime_allowed(**kwargs) -> dict:
    decision = evaluate_runtime_gate(**kwargs)
    if not decision.get("allowed"):
        raise PermissionError(decision.get("blocked_reason") or "runtime_blocked")
    return decision


# Reexports explícitos para compat (usado por isolation_boundary, execution_provider, registry, etc)
__all__ = [
    "RUNTIME_PROFILE",
    "RUNTIME_PROFILES",
    "FIXED_CODEACT_OPERATIONS",
    "KNOWN_RUNTIME_OPERATIONS",
    "evaluate_runtime_gate",
    "assert_runtime_allowed",
]

