"""Graph definition for LangGraph engineering loop.

This is a minimal placeholder that defines a simple sequential graph using
LangGraph's `StateGraph` if the library is available. If LangGraph is not
installed, the module provides a fallback `run` function that raises a clear
error explaining how to install the dependency.
"""

from __future__ import annotations

try:
    from langgraph.graph import StateGraph
    from .state import LoopState
except ImportError:  # pragma: no cover
    StateGraph = None  # type: ignore
    LoopState = None  # type: ignore


def build_graph() -> StateGraph:
    """Build a simple LangGraph state machine for the engineering loop.

    The graph consists of the following nodes:
        - "load_context"
        - "plan"
        - "execute"
        - "test"
        - "analyze"
        - "report"

    Each node receives the ``LoopState`` and returns an updated instance.
    """
    if StateGraph is None:
        raise RuntimeError(
            "LangGraph is not installed. Install with `pip install langgraph` to use the engineering loop."
        )

    graph = StateGraph(LoopState)

    # Placeholder node implementations – in a real spike they would contain
    # actual logic; here we simply pass the state through.
    def load_context(state: LoopState):
        state.context = {"loaded": True}
        return state

    def plan(state: LoopState):
        state.plan = {"steps": ["execute", "test"]}
        return state

    def execute(state: LoopState):
        state.result = "execution result"
        state.success = True
        return state

    def test(state: LoopState):
        # Pretend tests passed
        return state

    def analyze(state: LoopState):
        # No failure analysis needed for the spike
        return state

    def report(state: LoopState):
        # Reporting handled in `reporting.py`
        return state

    # Register nodes in order
    graph.add_node("load_context", load_context)
    graph.add_node("plan", plan)
    graph.add_node("execute", execute)
    graph.add_node("test", test)
    graph.add_node("analyze", analyze)
    graph.add_node("report", report)

    # Define edges – linear flow for this spike
    graph.add_edge("load_context", "plan")
    graph.add_edge("plan", "execute")
    graph.add_edge("execute", "test")
    graph.add_edge("test", "analyze")
    graph.add_edge("analyze", "report")
    graph.set_entry_point("load_context")
    graph.set_finish_point("report")
    return graph


def run() -> LoopState:
    """Execute the engineering loop and return the final ``LoopState``.

    This function is used by the smoke‑test script. It builds the graph and
    runs it with an empty initial state.
    """
    graph = build_graph()
    initial_state = LoopState(context={})
    compiled = graph.compile()
    return compiled.invoke(initial_state)
