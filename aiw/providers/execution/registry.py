"""Basic Execution Provider Registry.

This is the start of aligning with the new architecture.
Currently delegates to legacy for backward compatibility.
"""

from typing import Dict, Optional, Type
from aiw.interfaces.execution_provider import ExecutionProvider

class ExecutionProviderRegistry:
    """Registry for Execution Providers."""

    def __init__(self):
        self._providers: Dict[str, Type[ExecutionProvider]] = {}
        self._register_defaults()

    def _register_defaults(self):
        # CodeAct agora usa implementação migrada (formato atualizado)
        from .codeact import CodeActExecutionProvider
        self.register("codeact", CodeActExecutionProvider)

        # New providers (stubs for priority 2; register classes directly)
        try:
            from .docker import DockerExecutionProvider
            self.register("docker", DockerExecutionProvider)
        except Exception:
            pass
        try:
            from .devcontainer import DevcontainerExecutionProvider
            self.register("devcontainer", DevcontainerExecutionProvider)
        except Exception:
            pass

    def register(self, name: str, provider_class: Type[ExecutionProvider]):
        self._providers[name] = provider_class

    def get(self, name: str = "codeact") -> Optional[ExecutionProvider]:
        entry = self._providers.get(name)
        if entry:
            if callable(entry):
                # Call lazy getter (returns class or instance); ensure instance
                obj = entry()
                if isinstance(obj, type):
                    obj = obj()
                return obj
            if isinstance(entry, type):
                return entry()
            return entry
        return None

    def list(self):
        return list(self._providers.keys())


_registry: Optional[ExecutionProviderRegistry] = None


def get_execution_provider_registry() -> ExecutionProviderRegistry:
    global _registry
    if _registry is None:
        _registry = ExecutionProviderRegistry()
    return _registry
