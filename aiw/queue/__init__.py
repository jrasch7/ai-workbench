"""Queue layer (post Round 2 mover 5 + daemon-next).

Basic queue structures + durable disk-backed impl. Legacy aiw_workspace/agent_queue still holds most logic during migration.
Durable disk-backed for 24/7 daemon restarts: persists to .aiw/workspaces/{ws}/queue/queue.json

High-level usage for 24/7 daemon:
- from aiw.queue import get_agent_queue, start_daemon_worker, get_persistent_worker
- q = get_agent_queue(); q.enqueue("aiw", "minha missão longa")
- start_daemon_worker("aiw")  # bg PersistentAgentWorker polling queue -> persistent runs
- Use env AIW_PERSISTENT_MAX_ITERATIONS=0 for unlimited iters (rely on checkpoints + !should_continue + policy)
- Resume: from aiw.agent.iterative_loop import start_persistent_agent_daemon; start_persistent_agent_daemon(..., resume_run_id=..., persistent=True)
- Cockpit: checkbox "Start as background daemon" or /runner/start-daemon or /api/daemons
- Monitor: list_daemon_workers(), list_running_daemons()
- Also: ./scripts/aiw-agent-loop --persistent --resume --run-id ...
- Reexports PersistentAgentWorker etc used by cockpit and aiw-daemon flows.
See docs/runbooks/AIW_AGENT_ITERATIVE_LOOP.md (seção Daemon 24/7) and docs/MIGRATION.md
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

class QueueItem:
    def __init__(self, item_id: str, task: str, workspace_id: str, priority: int = 0, mission_id: str | None = None):
        self.item_id = item_id
        self.task = task
        self.workspace_id = workspace_id
        self.priority = priority
        self.mission_id = mission_id
        self.status = "queued"

    def to_dict(self) -> Dict:
        d = {
            "item_id": self.item_id,
            "task": self.task,
            "workspace_id": self.workspace_id,
            "priority": self.priority,
            "status": self.status,
        }
        if self.mission_id:
            d["mission_id"] = self.mission_id
        return d

    @classmethod
    def from_dict(cls, d: Dict) -> "QueueItem":
        if not isinstance(d, dict):
            d = {}
        item = cls(
            d.get("item_id", "q-unknown"),
            d.get("task", ""),
            d.get("workspace_id", "aiw"),
            int(d.get("priority", 0)),
            d.get("mission_id"),
        )
        item.status = d.get("status", "queued")
        return item

class AgentQueue:
    """Lightweight queue facade. Now disk-backed for daemon durability.

    Persists items (as list of dicts) to .aiw/workspaces/{ws}/queue/queue.json
    Loads on init if present. Survives process restarts for 24/7 daemons.
    """
    def __init__(self, workspace_id: str = "aiw"):
        self.workspace_id = str(workspace_id or "aiw")
        self._items: List[QueueItem] = []
        try:
            root = Path(os.environ.get("AIW_ROOT", str(Path(__file__).resolve().parents[2]))).resolve()
        except Exception:
            root = Path.cwd().resolve()
        self._qdir = root / ".aiw" / "workspaces" / self.workspace_id / "queue"
        self._qfile = self._qdir / "queue.json"
        self.load()

    def _ensure_dir(self) -> None:
        try:
            self._qdir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def load(self) -> None:
        """Load persisted items from disk if queue.json exists. Best-effort."""
        self._items = []
        try:
            if self._qfile.exists():
                data = json.loads(self._qfile.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    for d in data:
                        try:
                            self._items.append(QueueItem.from_dict(d))
                        except Exception:
                            pass
        except Exception:
            # best effort, start empty on corruption
            self._items = []

    def persist(self) -> None:
        """Persist current items (simple list of dicts) to disk."""
        try:
            self._ensure_dir()
            data = [i.to_dict() for i in self._items]
            self._qfile.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass  # best effort for durability

    def clear_completed(self) -> dict:
        """Remove completed items and persist. Returns count cleared."""
        before = len(self._items)
        self._items = [i for i in self._items if getattr(i, "status", None) != "completed"]
        cleared = before - len(self._items)
        if cleared:
            self.persist()
        return {"cleared": cleared, "remaining": len(self._items)}

    def enqueue(self, workspace_id: str, task: str, priority: int = 0, mission_id: str | None = None) -> QueueItem:
        import uuid
        ws = str(workspace_id or self.workspace_id)
        # Delegate to correct per-ws queue instance to keep persistence files correct per-ws
        if ws != self.workspace_id:
            try:
                other = get_agent_queue(ws)
                if other is not self:
                    return other.enqueue(ws, task, priority, mission_id)
            except Exception:
                pass
        item = QueueItem(f"q-{uuid.uuid4().hex[:8]}", task, ws, priority, mission_id)
        self._items.append(item)
        self.persist()
        return item

    def dequeue(self) -> Optional[QueueItem]:
        if self._items:
            item = self._items.pop(0)
            self.persist()
            return item
        return None

    def list(self) -> List[Dict]:
        return [i.to_dict() for i in self._items]

_queue_instances: Dict[str, AgentQueue] = {}

def get_agent_queue(workspace_id: Optional[str] = None) -> AgentQueue:
    """Return (or create) the AgentQueue for a workspace. Defaults to 'aiw'.

    Now supports per-ws for durable separate queue.json files.
    Backwards compatible: get_agent_queue() or get_agent_queue('aiw') works.
    """
    global _queue_instances
    ws = str(workspace_id or "aiw")
    if ws not in _queue_instances:
        _queue_instances[ws] = AgentQueue(workspace_id=ws)
    return _queue_instances[ws]

# Reexports for 24/7 persistent daemon worker (aiw.queue.get_persistent_worker etc; used by cockpit + scripts/aiw-daemon)
# Placed after get_agent_queue to avoid import cycle during module init.
from .worker import (
    PersistentAgentWorker,
    get_persistent_worker,
    start_daemon_worker,
    stop_daemon_worker,
    list_daemon_workers,
    resume_all_checkpoints_as_daemons,
    start_24_7_worker,
    worker_health,
)

# Step 1: agent_dispatcher related (moved to aiw/queue for queue/agent flows)
from .agent_dispatcher import (
    run_agent_dispatcher_once,
    run_agent_dispatcher_watch,
    list_agent_dispatcher_runs,
    read_agent_dispatcher_run,
)

# Migração: versão atualizada de create_queue_item_from_inbox (simplificada, usa aiw paths)
# Lógica completa ainda em legado para paths complexos durante transição.
def create_queue_item_from_inbox(workspace_id: str, inbox_item_id: str) -> dict:
    # Delegate to legacy for full impl during migration
    from aiw_workspace.agent_queue import create_queue_item_from_inbox as legacy_fn
    return legacy_fn(workspace_id, inbox_item_id)
