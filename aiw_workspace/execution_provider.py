from dataclasses import dataclass
from typing import Any

from aiw.interfaces.execution_provider import ExecutionProvider as BaseExecutionProvider
# Migrado: usa versão atualizada em aiw
from aiw.providers.execution.codeact_sandbox import run_codeact_action, validate_codeact_action
from .runtime_gate import RUNTIME_PROFILE


EXECUTION_PROVIDER_VERSION = "execution_provider_v1"
CODEACT_PROVIDER_NAME = "codeact"
CODEACT_SUPPORTED_OPERATIONS = {
    "python_eval_fixed",
    "fixed_codeact_python_eval",
}


@dataclass(frozen=True)
class CodeActExecutionProvider(BaseExecutionProvider):
    _name: str = CODEACT_PROVIDER_NAME
    version: str = EXECUTION_PROVIDER_VERSION
    capability: str = "codeact_sandbox"

    def name(self) -> str:
        return self._name

    def describe(self) -> dict:
        return {
            "name": self.name(),
            "version": self.version,
            "capability": self.capability,
            "kind": "codeact_sandbox",
            "functional": True,
            "description": "Wraps the existing CodeAct Sandbox without changing its safety rules.",
            "supported_runtimes": [RUNTIME_PROFILE],
            "supported_operations": sorted(CODEACT_SUPPORTED_OPERATIONS),
            "executes_dynamic_code": False,
            "metadata_only": False,
        }

    def validate(self, action: dict[str, Any] | None = None) -> dict:
        if action is None:
            action = _fixed_probe_action()
        result = validate_codeact_action(action)
        return {
            "provider": self.name(),
            "version": self.version,
            "valid": result.get("status") == "ok",
            "validation": result,
        }

    def supports_runtime(self, runtime_required: str | None) -> bool:
        return runtime_required == RUNTIME_PROFILE

    def supports_operation(self, operation: str | None) -> bool:
        return operation in CODEACT_SUPPORTED_OPERATIONS

    def dry_run(self, workspace_id: str, action: dict[str, Any], operation: str) -> dict:
        validation = self.validate(action)
        supported = self.supports_operation(operation)
        return {
            "provider": self.name(),
            "version": self.version,
            "workspace_id": workspace_id,
            "operation": operation,
            "status": "dry_run" if validation.get("valid") and supported else "blocked",
            "supported": supported,
            "validation": validation,
            "stdout_preview": "Would execute fixed safe offline CodeAct action.",
            "stderr_preview": "",
        }

    def execute(
        self,
        workspace_id: str,
        action: dict[str, Any],
        operation: str,
        confirm: bool = False,
    ) -> dict:
        if not self.supports_operation(operation):
            return {"status": "blocked", "reason": "operation_not_supported_by_execution_provider"}
        return run_codeact_action(workspace_id, action, confirm=confirm)


def _fixed_probe_action() -> dict:
    return {
        "kind": "python_eval",
        "title": "AIW Execution Provider Validation Probe",
        "code": "print('AIW_EXECUTION_PROVIDER_PROBE_OK')",
        "timeout_seconds": 5,
        "max_stdout_chars": 2000,
        "max_stderr_chars": 2000,
    }


def list_execution_providers() -> list[dict]:
    from aiw.providers.execution.registry import get_execution_provider_registry
    reg = get_execution_provider_registry()
    return [reg.get(name).describe() for name in reg.list()] if reg.list() else [CodeActExecutionProvider().describe()]


def get_execution_provider(name: str = CODEACT_PROVIDER_NAME) -> CodeActExecutionProvider | None:
    # Aligned
    from aiw.providers.execution.registry import get_execution_provider_registry
    return get_execution_provider_registry().get(name) or CodeActExecutionProvider() if name == CODEACT_PROVIDER_NAME else None


def provider_for_capability(capability_name: str, exec_provider_name: str = None) -> CodeActExecutionProvider | None:
    # Aligned: delegate to new bridge
    from aiw.providers.execution.bridge import provider_for_capability as new_provider_for_capability
    return new_provider_for_capability(capability_name, exec_provider_name)


def describe_execution_provider(name: str) -> dict:
    provider = get_execution_provider(name)
    if not provider:
        return {"ok": False, "error": "execution_provider_not_found", "provider": name}
    return {"ok": True, "provider": provider.describe()}


def validate_execution_provider(name: str) -> dict:
    provider = get_execution_provider(name)
    if not provider:
        return {"ok": False, "error": "execution_provider_not_found", "provider": name}
    validation = provider.validate()
    return {"ok": bool(validation.get("valid")), "validation": validation}
