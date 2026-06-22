"""Context loader for LangGraph engineering loop.

Placeholder implementation that loads static context data. In a real
implementation it could read configuration files, environment variables,
or query services.
"""

from .state import LoopState

def load_context(state: LoopState) -> LoopState:
    """Load engineering context into the LoopState.

    For this spike we simply set a static dictionary.
    """
    state.context = {
        "project": "AI Workbench",
        "engine": "LangGraph",
        "timestamp": None,
    }
    return state
