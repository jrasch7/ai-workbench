# MIGRAÇÃO CIRÚRGICA STEP 1: aiw_workspace/agent_dispatcher.py agora thin delegate.
# Lógica principal em aiw/queue/agent_dispatcher.py (aiw-first, relacionado a queue/dispatcher).
# Prefer aiw/ . Sem mudança de comportamento.

from aiw.queue.agent_dispatcher import (
    run_agent_dispatcher_once,
    run_agent_dispatcher_watch,
    list_agent_dispatcher_runs,
    read_agent_dispatcher_run,
)

__all__ = [
    "run_agent_dispatcher_once",
    "run_agent_dispatcher_watch",
    "list_agent_dispatcher_runs",
    "read_agent_dispatcher_run",
]

# Fim da migração para agent_dispatcher (aiw/queue primary). Ver docs/MIGRATION.md
