"""Integration layer (GitHub Intake, Outbox, Worker).

Migrated high-value modules from aiw_workspace/ to aiw/ structure.
Mantém compatibilidade via thin delegates em aiw_workspace/.

Termos:
- GitHub Intake: ingestão de issues/PRs para gerar Patch Intent.
- Integration Outbox: fila de saída para envios (ex: PR summaries).
- Integration Worker: worker para execução de envios externos (com dry-run e policy).
"""

# Reexports principais (lazy safe)
def run_github_intake(*a, **k):
    from .github_intake import run_github_intake as fn
    return fn(*a, **k)

def create_patch_intent(*a, **k):
    from .github_intake import create_patch_intent as fn
    return fn(*a, **k)

def list_inbox_items(*a, **k):
    from .github_intake import list_inbox_items as fn
    return fn(*a, **k)

def read_inbox_item(*a, **k):
    from .github_intake import read_inbox_item as fn
    return fn(*a, **k)

def update_inbox_item_status(*a, **k):
    from .github_intake import update_inbox_item_status as fn
    return fn(*a, **k)

def resolve_inbox_item_file(*a, **k):
    from .github_intake import resolve_inbox_item_file as fn
    return fn(*a, **k)

def list_inbox_item_attempts(*a, **k):
    from .github_intake import list_inbox_item_attempts as fn
    return fn(*a, **k)


def create_outbox_item(*a, **k):
    from .integration_outbox import create_outbox_item as fn
    return fn(*a, **k)

def list_outbox_items(*a, **k):
    from .integration_outbox import list_outbox_items as fn
    return fn(*a, **k)

def read_outbox_item(*a, **k):
    from .integration_outbox import read_outbox_item as fn
    return fn(*a, **k)

def update_outbox_item_status(*a, **k):
    from .integration_outbox import update_outbox_item_status as fn
    return fn(*a, **k)

def resolve_outbox_item_file(*a, **k):
    from .integration_outbox import resolve_outbox_item_file as fn
    return fn(*a, **k)

def set_outbox_dispatch(*a, **k):
    from .integration_outbox import set_outbox_dispatch as fn
    return fn(*a, **k)


def run_worker(*a, **k):
    from .integration_worker import run_worker as fn
    return fn(*a, **k)

def mark_outbox_item_sent(*a, **k):
    from .integration_worker import mark_outbox_item_sent as fn
    return fn(*a, **k)

def list_item_attempts(*a, **k):
    from .integration_worker import list_item_attempts as fn
    return fn(*a, **k)


__all__ = [
    "run_github_intake", "create_patch_intent",
    "list_inbox_items", "read_inbox_item", "update_inbox_item_status",
    "resolve_inbox_item_file", "list_inbox_item_attempts",
    "create_outbox_item", "list_outbox_items", "read_outbox_item",
    "update_outbox_item_status", "resolve_outbox_item_file", "set_outbox_dispatch",
    "run_worker", "mark_outbox_item_sent", "list_item_attempts",
]
