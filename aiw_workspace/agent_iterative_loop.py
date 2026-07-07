# Delegates to aiw/agent for the target architecture alignment. Lazy.
def run_agent_iterative_loop_once(*a, **k):
    from aiw.agent.iterative_loop import run_agent_iterative_loop_once as fn
    return fn(*a, **k)

def list_agent_loop_runs(*a, **k):
    from aiw.agent.iterative_loop import list_agent_loop_runs as fn
    return fn(*a, **k)

def read_agent_loop_run(*a, **k):
    from aiw.agent.iterative_loop import read_agent_loop_run as fn
    return fn(*a, **k)
