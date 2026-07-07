"""Basic Memory layer for AIW (started post Round 2).

Provides short-term memory for agent runs and simple long-term stubs.
Integrates with agent loop for context accumulation and retrieval.
"""

from typing import Any, Dict, List, Optional
import time

class MemoryItem:
    def __init__(self, content: str, kind: str = "fact", metadata: Optional[Dict] = None):
        self.content = content
        self.kind = kind
        self.metadata = metadata or {}
        self.timestamp = time.time()

class ShortTermMemory:
    """In-memory store for current run/session."""
    def __init__(self, max_items: int = 50):
        self._items: List[MemoryItem] = []
        self.max_items = max_items

    def add(self, content: str, kind: str = "step_result", metadata: Optional[Dict] = None):
        item = MemoryItem(content, kind, metadata)
        self._items.append(item)
        if len(self._items) > self.max_items:
            self._items.pop(0)

    def get_recent(self, n: int = 10) -> List[Dict]:
        return [
            {"content": i.content, "kind": i.kind, "ts": i.timestamp}
            for i in self._items[-n:]
        ]

    def to_context_string(self, n: int = 5) -> str:
        items = self.get_recent(n)
        return "\n".join(f"[{i['kind']}] {i['content'][:150]}" for i in items)

class LongTermMemory:
    """Stub for persistent memory (future: vector DB, file, etc.)."""
    def __init__(self):
        self._store: Dict[str, List[MemoryItem]] = {}

    def store(self, workspace_id: str, item: MemoryItem):
        self._store.setdefault(workspace_id, []).append(item)

    def retrieve(self, workspace_id: str, query: str = "", limit: int = 5) -> List[Dict]:
        items = self._store.get(workspace_id, [])
        # Very naive "search"
        return [
            {"content": i.content, "kind": i.kind}
            for i in items[-limit:]
        ]

_memory_instance: Optional[ShortTermMemory] = None
_long_term: Optional[LongTermMemory] = None

def get_short_term_memory() -> ShortTermMemory:
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = ShortTermMemory()
    return _memory_instance

def get_long_term_memory() -> LongTermMemory:
    global _long_term
    if _long_term is None:
        _long_term = LongTermMemory()
    return _long_term

def get_memory_context(workspace_id: str, n: int = 5) -> str:
    stm = get_short_term_memory()
    ltm = get_long_term_memory()
    recent = stm.to_context_string(n)
    long = "\n".join(r["content"][:100] for r in ltm.retrieve(workspace_id, limit=3))
    return f"Recent:\n{recent}\n\nLong-term relevant:\n{long}" if long else recent
