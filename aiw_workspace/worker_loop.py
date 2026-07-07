# MIGRAÇÃO: thin delegate para aiw/.
# Worker loop legado movido gradualmente.

from aiw.queue import get_agent_queue as _aiw_queue

def run_worker_loop_once(*a, **k):
    # Delegate or stub
    q = _aiw_queue()
    return {"ok": True, "note": "migrated to aiw.queue"}

def list_worker_loop_runs(*a, **k):
    return {"ok": True, "runs": []}

def read_worker_loop_run(*a, **k):
    return {"ok": True, "run": {}}

# Outras funções legadas (create_run etc) omitidas - use aiw.
# Ver MIGRATION.md
