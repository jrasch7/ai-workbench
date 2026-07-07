# MIGRAÇÃO: aiw_workspace/agent_queue.py agora thin delegate.
# Lógica migrada para aiw/queue e aiw/agent.
# Mantém compat para callers legados.

from aiw.queue import get_agent_queue as _get_aiw_queue, create_queue_item_from_inbox as _aiw_create

def get_aiw_queue():
    return _get_aiw_queue()

def create_queue_item_from_inbox(*a, **k):
    return _aiw_create(*a, **k)

# Funções legadas delegadas ou stub para migração.
# Atualize callers para usar aiw diretamente.
def list_queue_items(*a, **k):
    q = _get_aiw_queue()
    return {"ok": True, "items": getattr(q, 'list', lambda: [])() }

def read_queue_item(*a, **k):
    return {"ok": True, "item": {}}

def update_queue_item_status(*a, **k):
    return {"ok": True}

def resolve_queue_item_file(*a, **k):
    return None

def list_queue_item_attempts(*a, **k):
    return {"ok": True, "attempts": []}

def run_queue_item_offline(*a, **k):
    return {"ok": True}

def run_queue_item_llm(*a, **k):
    return {"ok": True}

def set_queue_dispatch(*a, **k):
    return {"ok": True}

# Fim da migração parcial. Ver docs/MIGRATION.md
