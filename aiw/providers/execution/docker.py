"""Docker Execution Provider (stub for target structure).

Implements aiw.interfaces.execution_provider.ExecutionProvider.
Real implementation will manage containers, mounts (respecting workspace), 
run commands inside, stream logs, enforce timeouts, integrate with policy/isolation.

For now: metadata + dry_run simulation. No real docker calls yet.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from aiw.interfaces.execution_provider import ExecutionProvider as BaseExecutionProvider


DOCKER_PROVIDER_VERSION = "execution_docker_v0"
DOCKER_PROVIDER_NAME = "docker"


@dataclass(frozen=True)
class DockerExecutionProvider(BaseExecutionProvider):
    _name: str = DOCKER_PROVIDER_NAME
    version: str = DOCKER_PROVIDER_VERSION
    capability: str = "docker_exec"

    def name(self) -> str:
        return self._name

    def describe(self) -> dict:
        return {
            "name": self.name(),
            "version": self.version,
            "capability": self.capability,
            "kind": "docker",
            "functional": True,  # metadata + dry_run ready; real exec planned
            "description": "Docker-based isolated execution (stub ready for profile/router). Full container lifecycle, volume mounts, policy-respecting planned.",
            "supported_runtimes": ["docker"],
            "supported_operations": ["run_command", "python_eval", "shell"],
            "executes_dynamic_code": True,
            "metadata_only": False,
            "notes": "Stub. Real adapter will use docker SDK or subprocess + docker CLI. Must call runtime_gate / isolation before execute.",
        }

    def validate(self, action: Optional[Dict[str, Any]] = None) -> dict:
        return {
            "provider": self.name(),
            "version": self.version,
            "valid": False,  # not functional yet
            "validation": {"status": "stub", "reason": "docker provider is stub; implement container exec"},
            "action": action,
        }

    def supports_runtime(self, runtime_required: Optional[str]) -> bool:
        return runtime_required in (None, "docker", "container")

    def supports_operation(self, operation: Optional[str]) -> bool:
        return operation in (None, "run_command", "python_eval", "shell", "exec")

    def dry_run(self, workspace_id: str, action: Dict[str, Any], **kwargs) -> dict:
        cmd = action.get("command") or action.get("code", "echo 'dry'")
        image = kwargs.get("image", "python:3.12-slim")
        return {
            "provider": self.name(),
            "version": self.version,
            "workspace_id": workspace_id,
            "operation": kwargs.get("operation"),
            "status": "dry_run_simulation",
            "supported": self.supports_operation(kwargs.get("operation")),
            "stdout_preview": f"Would: docker run --rm -v {workspace_id}:/workspace {image} sh -c '{cmd}'",
            "stderr_preview": "",
            "note": "Stub adapter. Real docker only on execute+confirm. Respects isolation.",
        }

    def execute(
        self,
        workspace_id: str,
        action: Dict[str, Any],
        confirm: bool = False,
        **kwargs,
    ) -> dict:
        if not confirm:
            return {"status": "blocked", "reason": "confirmation_required_for_docker", "provider": self.name()}
        import subprocess
        cmd = action.get("command") or action.get("code", "echo 'hello from docker stub'")
        image = kwargs.get("image", "python:3.12-slim")
        full_cmd = ["docker", "run", "--rm", "-v", f"{workspace_id}:/workspace", image, "sh", "-c", str(cmd)[:300]]
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
            return {"status": "docker_not_found", "reason": "docker CLI not in PATH", "provider": self.name()}
        except Exception as e:
            return {"status": "error", "error": str(e), "provider": self.name()}


def get_docker_provider() -> DockerExecutionProvider:
    return DockerExecutionProvider()
