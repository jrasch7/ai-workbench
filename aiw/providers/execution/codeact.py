"""CodeAct Execution Provider (formato atualizado em aiw/).

Lógica de sandbox migrada de aiw_workspace/codeact_sandbox.py.
"""

from .codeact_sandbox import run_codeact_action, validate_codeact_action

from aiw.interfaces.execution_provider import ExecutionProvider as BaseExecutionProvider
from dataclasses import dataclass
from typing import Any, Dict, Optional

# Reusa a estrutura do legado mas em novo local
# Para compat, ainda delega parte para execução provider legado em alguns casos.

@dataclass(frozen=True)
class CodeActExecutionProvider(BaseExecutionProvider):
    name: str = "codeact"
    version: str = "execution_provider_v1"
    capability: str = "codeact_sandbox"

    def name(self) -> str:
        return self.name

    def describe(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "capability": self.capability,
            "kind": "codeact_sandbox",
            "functional": True,
            "description": "CodeAct migrado para estrutura aiw/. Sandbox seguro para python_eval.",
            "supported_runtimes": ["host_best_effort"],
            "supported_operations": ["python_eval_fixed"],
            "executes_dynamic_code": False,
            "metadata_only": False,
        }

    def validate(self, action: Optional[Dict[str, Any]] = None) -> dict:
        if action is None:
            action = {"kind": "python_eval", "code": "print('probe')"}
        result = validate_codeact_action(action)
        return {
            "provider": self.name,
            "version": self.version,
            "valid": result.get("status") == "ok",
            "validation": result,
        }

    def supports_runtime(self, runtime_required: Optional[str]) -> bool:
        return runtime_required in (None, "host_best_effort")

    def supports_operation(self, operation: Optional[str]) -> bool:
        return operation in (None, "python_eval_fixed", "fixed_codeact_python_eval")

    def dry_run(self, workspace_id: str, action: Dict[str, Any], **kwargs) -> dict:
        validation = self.validate(action)
        return {
            "provider": self.name,
            "version": self.version,
            "workspace_id": workspace_id,
            "operation": kwargs.get("operation"),
            "status": "dry_run" if validation.get("valid") else "blocked",
            "validation": validation,
            "stdout_preview": "Would execute safe CodeAct (migrated).",
        }

    def execute(self, workspace_id: str, action: Dict[str, Any], confirm: bool = False, **kwargs) -> dict:
        if not self.supports_operation(kwargs.get("operation")):
            return {"status": "blocked", "reason": "operation_not_supported"}
        return run_codeact_action(workspace_id, action, confirm=confirm)

# Legacy compat reexport if needed
CodeActExecutionProviderLegacy = CodeActExecutionProvider

