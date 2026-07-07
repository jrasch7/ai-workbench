# Execution Orchestration

Orchestrates calls to Execution Providers for the agent runtime.

**Note:** The actual provider implementations live in `../providers/execution/`.

**Current status:** Thin orchestration. Main dispatch logic is being wired in `../agent/iterative_loop.py`.

See providers/execution for CodeAct, Docker, Devcontainer.
