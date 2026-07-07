"""Graph definition for LangGraph engineering loop.

This module defines a deterministic LangGraph state machine that orchestrates the
engineering loop: load context → plan → execute → test → analyze → report.
"""

from __future__ import annotations

try:
    from langgraph.graph import StateGraph
    from .state import LoopState
    from .command_runner import run_command, CommandResult
except ImportError:  # pragma: no cover
    StateGraph = None  # type: ignore
    LoopState = None  # type: ignore
    run_command = None  # type: ignore


def build_graph() -> StateGraph:
    """Build the LangGraph state machine for the engineering loop.

    The graph consists of the following nodes:
        - "load_context"
        - "plan"
        - "execute"
        - "test"
        - "analyze"
        - "report"
    Each node receives a ``LoopState`` and returns an updated instance.
    """
    if StateGraph is None:
        raise RuntimeError(
            "LangGraph is not installed. Install with `pip install langgraph` to use the engineering loop."
        )

    graph = StateGraph(LoopState)

    # Node implementations ---------------------------------------------------
    def load_context(state: LoopState) -> LoopState:
        from .context_loader import load_context as lc
        return lc(state)

    def plan(state: LoopState) -> LoopState:
        # Simple static plan for the spike.
        state.plan = {"steps": ["execute", "test"]}
        return state

    def execute(state: LoopState) -> LoopState:
        # Run the compileall command using the safe command runner.
        if run_command is None:
            raise RuntimeError("Command runner unavailable.")
        cmd_str = "python -m compileall aiw_langgraph"
        res = run_command(cmd_str)
        # Record command details
        state.commands.append({
            "command": cmd_str,
            "exit_code": res.get("exit_code"),
            "stdout": res.get("stdout", ""),
            "stderr": res.get("stderr", ""),
            "duration": res.get("duration", 0),
        })
        # Determine success based on exit code.
        if res.get("exit_code") == 0:
            state.success = True
        else:
            state.success = False
            err_msg = res.get("stderr", "Compile failed")
            state.errors.append(err_msg.strip() or "Compile failed")
        return state

    def test(state: LoopState) -> LoopState:
        # In this spike, test step simply records that validation was performed.
        validation = {
            "name": "compileall",
            "passed": state.success,
            "details": "Compilation succeeded" if state.success else "Compilation errors",
        }
        state.validations.append(validation)
        return state

    def analyze(state: LoopState) -> LoopState:
        # Placeholder for future failure analysis logic.
        return state

    def report(state: LoopState) -> LoopState:
        # No action; reporting is handled by reporting.py.
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

    Used by the smoke‑test script. Builds the graph and runs it with an empty
    initial state.
    """
    graph = build_graph()
    initial_state = LoopState(id='smoke', title='LangGraph Smoke', status='queued', context={})
    compiled = graph.compile()
    return compiled.invoke(initial_state)
