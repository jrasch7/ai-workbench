"""Public interfaces for AIW (target architecture).

See docs/ARCHITECTURE.md and docs/interfaces/ for full definitions.
Currently only the implemented ones are exposed in Python.
"""

from .model_provider import ModelProvider
from .execution_provider import ExecutionProvider
from .context_provider import ContextProvider
from .model_router import ModelRouter
from .agent_profile import AgentProfile

__all__ = [
    "ModelProvider",
    "ExecutionProvider",
    "ContextProvider",
    "ModelRouter",
    "AgentProfile",
]

