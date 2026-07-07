"""AIW - Target package structure (in progress alignment).

This package represents the future organized structure.
Legacy code remains in aiw_workspace/ during migration.

Import example:
    from aiw.providers.execution.registry import get_execution_provider_registry
    from aiw.router.router import get_model_router
"""

# Lazy imports to avoid cycles during alignment
def get_execution_provider_registry():
    from .providers.execution.registry import get_execution_provider_registry as fn
    return fn()

def get_model_provider_registry():
    from .providers.model.registry import get_model_provider_registry as fn
    return fn()

def get_context_provider_registry():
    from .providers.context.registry import get_context_provider_registry as fn
    return fn()

def get_model_router():
    from .router.router import get_model_router as fn
    return fn()

def get_capability_registry():
    from .policy.registry import get_capability_registry as fn
    return fn()

def get_policy_engine():
    from .policy.registry import get_policy_engine as fn
    return fn()

def load_profile(*a, **k):
    from .profiles import load_profile as fn
    return fn(*a, **k)

def get_profile(*a, **k):
    from .profiles import get_profile as fn
    return fn(*a, **k)

def list_profiles():
    from .profiles import list_profiles as fn
    return fn()

def run_agent_iterative_loop_once(*a, **k):
    from .agent import run_agent_iterative_loop_once as fn
    return fn(*a, **k)

def list_agent_loop_runs(*a, **k):
    from .agent import list_agent_loop_runs as fn
    return fn(*a, **k)

def read_agent_loop_run(*a, **k):
    from .agent import read_agent_loop_run as fn
    return fn(*a, **k)

# Model providers for convenience
def get_openrouter_provider(**kwargs):
    from .providers.model.openrouter import OpenRouterModelProvider
    return OpenRouterModelProvider(**kwargs)

# Execution providers convenience (newly added stubs)
def get_docker_execution_provider():
    from .providers.execution.docker import get_docker_provider
    return get_docker_provider()

def get_devcontainer_execution_provider():
    from .providers.execution.devcontainer import get_devcontainer_provider
    return get_devcontainer_provider()

# Experiment Lab
def get_experiment_lab():
    from . import experiment
    return experiment

# Queue (5 mover)
def get_agent_queue():
    from .queue import get_agent_queue
    return get_agent_queue()

__all__ = [
    "get_execution_provider_registry",
    "get_model_provider_registry",
    "get_context_provider_registry",
    "get_model_router",
    "get_capability_registry",
    "get_policy_engine",
    "load_profile",
    "get_profile",
    "list_profiles",
    "run_agent_iterative_loop_once",
    "list_agent_loop_runs",
    "read_agent_loop_run",
    "get_openrouter_provider",
    "get_docker_execution_provider",
    "get_devcontainer_execution_provider",
    "get_experiment_lab",
    "get_agent_queue",
]
