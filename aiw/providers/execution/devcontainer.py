"""Devcontainer Execution Provider (stub for target structure).

Implements aiw.interfaces.execution_provider.ExecutionProvider.
Devcontainers provide reproducible dev environments (via .devcontainer/devcontainer.json + docker-compose or docker).

Real impl: detect .devcontainer, use `devcontainer up` / `devcontainer exec`, run commands inside the container with proper workspace mount.

For now: metadata + simulation only.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from aiw.interfaces.execution_provider import ExecutionProvider as BaseExecutionProvider


DEVCONTAINER_PROVIDER_VERSION = "execution_devcontainer_v0"
DEVCONTAINER_PROVIDER_NAME = "devcontainer"


@dataclass(frozen=True)
class DevcontainerExecutionProvider(BaseExecutionProvider):
    _name: str = DEVCONTAINER_PROVIDER_NAME
    version: str = DEVCONTAINER_PROVIDER_VERSION
    capability: str = "devcontainer_exec"

    def name(self) -> str:
        return self._name

    def describe(self) -> dict:
        return {
            "name": self.name(),
            "version": self.version,
            "capability": self.capability,
            "kind": "devcontainer",
            "functional": True,  # metadata + dry_run ready; real exec planned
            "description": "Devcontainer-based execution (stub ready). Uses VS Code devcontainer spec for consistent envs + isolation.",
            "supported_runtimes": ["devcontainer", "docker"],
            "supported_operations": ["run_command", "python_eval", "shell", "full_dev_env"],
            "executes_dynamic_code": True,
            "metadata_only": False,
            "notes": "Stub. Will integrate `devcontainer` CLI or docker + post-create. Respects workspace path hygiene and policy gates.",
        }

    def validate(self, action: Optional[Dict[str, Any]] = None) -> dict:
        return {
            "provider": self.name(),
            "version": self.version,
            "valid": False,
            "validation": {"status": "stub", "reason": "devcontainer provider is stub"},
            "action": action,
        }

    def supports_runtime(self, runtime_required: Optional[str]) -> bool:
        return runtime_required in (None, "devcontainer", "docker", "container")

    def supports_operation(self, operation: Optional[str]) -> bool:
        return operation in (None, "run_command", "python_eval", "shell", "full_dev_env", "exec")

    def dry_run(self, workspace_id: str, action: Dict[str, Any], **kwargs) -> dict:
        cmd = action.get("command") or action.get("code", "echo 'dry'")
        return {
            "provider": self.name(),
            "version": self.version,
            "workspace_id": workspace_id,
            "operation": kwargs.get("operation"),
            "status": "dry_run_simulation",
            "supported": self.supports_operation(kwargs.get("operation")),
            "stdout_preview": f"Would: devcontainer exec --workspace-folder . -- {cmd}",
            "stderr_preview": "",
            "note": "Stub adapter. Full devcontainer on execute+confirm.",
        }

    def execute(
        self,
        workspace_id: str,
        action: Dict[str, Any],
        confirm: bool = False,
        **kwargs,
    ) -> dict:
        if not confirm:
            return {"status": "blocked", "reason": "confirmation_required_for_devcontainer", "provider": self.name()}
        import subprocess
        cmd = action.get("command") or action.get("code", "echo 'hello from devcontainer'")
        full_cmd = ["devcontainer", "exec", "--workspace-folder", ".", "--", "sh", "-c", str(cmd)[:300]]
        try:
            out = subprocess.run(full_cmd, capture_output=True, text=True, timeout=30)
            return {
                "status": "executed",
                "provider": self.name(),
                "stdout": out.stdout[:2000],
                "stderr": out.stderr[:1000],
                "returncode": out.returncode,
            }
        except FileNotFoundError:
            return {"status": "devcontainer_not_found", "reason": "devcontainer CLI not available", "provider": self.name()}
        except Exception as e:
            return {"status": "error", "error": str(e), "provider": self.name()}


def get_devcontainer_provider() -> DevcontainerExecutionProvider:
    return DevcontainerExecutionProvider()
