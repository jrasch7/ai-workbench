"""Execution layer (target).

Re-exports from providers for convenience during alignment.
"""

from ..providers.execution.registry import get_execution_provider_registry
from ..providers.execution import (
    CodeActExecutionProvider,
    DockerExecutionProvider,
    DevcontainerExecutionProvider,
)

__all__ = [
    "get_execution_provider_registry",
    "CodeActExecutionProvider",
    "DockerExecutionProvider",
    "DevcontainerExecutionProvider",
]
