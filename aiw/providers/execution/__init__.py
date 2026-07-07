"""Execution Providers module (target structure)."""

from .registry import ExecutionProviderRegistry, get_execution_provider_registry
from .codeact import CodeActExecutionProvider  # migrado

# New providers (stubs started)
from .docker import DockerExecutionProvider, get_docker_provider
from .devcontainer import DevcontainerExecutionProvider, get_devcontainer_provider

def list_execution_providers() -> list[dict]:
    reg = get_execution_provider_registry()
    return [reg.get(name).describe() for name in reg.list()]

def get_execution_provider(name: str = "codeact"):
    return get_execution_provider_registry().get(name)

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

__all__ = [
    "ExecutionProviderRegistry",
    "get_execution_provider_registry",
    "CodeActExecutionProvider",
    "DockerExecutionProvider",
    "get_docker_provider",
    "DevcontainerExecutionProvider",
    "get_devcontainer_provider",
    "describe_execution_provider",
    "get_execution_provider",
    "list_execution_providers",
    "validate_execution_provider",
]
