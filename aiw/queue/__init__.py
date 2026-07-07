"""Queue layer stub (post Round 2 mover 5).

Basic queue structures. Legacy aiw_workspace/agent_queue still holds most logic during migration.
"""

from typing import Any, Dict, List, Optional

class QueueItem:
    def __init__(self, item_id: str, task: str, workspace_id: str, priority: int = 0):
        self.item_id = item_id
        self.task = task
        self.workspace_id = workspace_id
        self.priority = priority
        self.status = "queued"

    def to_dict(self) -> Dict:
        return {
            "item_id": self.item_id,
            "task": self.task,
            "workspace_id": self.workspace_id,
            "priority": self.priority,
            "status": self.status,
        }

class AgentQueue:
    """Lightweight queue facade."""
    def __init__(self):
        self._items: List[QueueItem] = []

    def enqueue(self, workspace_id: str, task: str, priority: int = 0) -> QueueItem:
        import uuid
        item = QueueItem(f"q-{uuid.uuid4().hex[:8]}", task, workspace_id, priority)
        self._items.append(item)
        return item

    def dequeue(self) -> Optional[QueueItem]:
        if self._items:
            return self._items.pop(0)
        return None

    def list(self) -> List[Dict]:
        return [i.to_dict() for i in self._items]

_queue_instance: Optional[AgentQueue] = None

def get_agent_queue() -> AgentQueue:
    global _queue_instance
    if _queue_instance is None:
        _queue_instance = AgentQueue()
    return _queue_instance

# Migração: versão atualizada de create_queue_item_from_inbox (simplificada, usa aiw paths)
# Lógica completa ainda em legado para paths complexos durante transição.
def create_queue_item_from_inbox(workspace_id: str, inbox_item_id: str) -> dict:
    # Delegate to legacy for full impl during migration
    from aiw_workspace.agent_queue import create_queue_item_from_inbox as legacy_fn
    return legacy_fn(workspace_id, inbox_item_id)
