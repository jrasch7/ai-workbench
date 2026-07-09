"""Basic Memory layer for AIW (started post Round 2).

Provides short-term memory for agent runs and simple long-term stubs.
Integrates with agent loop for context accumulation and retrieval.

Extended for STEP 2 (Long-term Memory + Cross-Mission Learning):
- Persistent lessons (success/failure patterns, preferences) per ws/mission.
- Semantic index of past runs (BOW on run summaries + lessons).
- retrieve_relevant for auto-inject "relevant past experiences" into planner/loop.
- Cross-mission reuse: lessons from prior missions influence new missions on same ws.
"""

from typing import Any, Dict, List, Optional
import json
import os
import re
import time
import math
from collections import Counter
from pathlib import Path

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
    """Stub for persistent memory (future: vector DB, file, etc.).
    Supports high-level improvements for self-improvement via Experiment Lab (Step 5).
    STEP 2 extension (surgical): persistent lessons for lessons-learned/success/failure patterns/preferences
    per workspace/mission; semantic (BOW) indexing of past runs; retrieve_relevant for cross-mission injection.
    """
    def __init__(self):
        self._store: Dict[str, List[MemoryItem]] = {}
        self._lessons: Dict[str, List[Dict]] = {}  # ws -> list of lesson dicts (persisted)

    def _get_memory_dir(self, workspace_id: str) -> Path:
        root = Path(os.environ.get("AIW_ROOT", str(Path(__file__).resolve().parents[2]))).resolve()
        ws = str(workspace_id or "aiw")
        d = root / ".aiw" / "workspaces" / ws / "memory"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _get_lessons_path(self, workspace_id: str) -> Path:
        return self._get_memory_dir(workspace_id) / "lessons.json"

    def _load_lessons(self, workspace_id: str) -> None:
        ws = str(workspace_id or "aiw")
        p = self._get_lessons_path(ws)
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    self._lessons[ws] = data
            except Exception:
                pass
        if ws not in self._lessons:
            self._lessons[ws] = []

    def _save_lessons(self, workspace_id: str) -> None:
        ws = str(workspace_id or "aiw")
        p = self._get_lessons_path(ws)
        try:
            p.write_text(json.dumps(self._lessons.get(ws, []), indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def _tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        return re.findall(r'[a-zA-Z_][a-zA-Z0-9_]{2,}', text.lower())

    def _cosine(self, c1: Counter, c2: Counter) -> float:
        if not c1 or not c2:
            return 0.0
        inter = set(c1.keys()) & set(c2.keys())
        dot = sum(c1[t] * c2[t] for t in inter)
        n1 = math.sqrt(sum(v * v for v in c1.values()))
        n2 = math.sqrt(sum(v * v for v in c2.values()))
        if n1 == 0.0 or n2 == 0.0:
            return 0.0
        return dot / (n1 * n2)

    def store(self, workspace_id: str, item: MemoryItem):
        self._store.setdefault(workspace_id, []).append(item)
        # Also surface run summaries as lessons when kind indicates
        if item.kind in ("resumo_run", "run_summary", "lesson", "success", "failure"):
            self.store_lesson(workspace_id, item.content, kind=item.kind, metadata=item.metadata)

    def retrieve(self, workspace_id: str, query: str = "", limit: int = 5) -> List[Dict]:
        items = self._store.get(workspace_id, [])
        # Very naive "search" (kept for compat); semantic used via retrieve_relevant
        return [
            {"content": i.content, "kind": i.kind}
            for i in items[-limit:]
        ]

    # STEP 2: lessons learned, success/failure patterns, preferences (persistent + per-mission)
    def store_lesson(self, workspace_id: str, content: str, kind: str = "lesson", metadata: Optional[Dict] = None):
        ws = str(workspace_id or "aiw")
        self._load_lessons(ws)
        lesson = {
            "content": content,
            "kind": kind,
            "metadata": metadata or {},
            "ts": time.time(),
        }
        # avoid dups on identical content+kind
        if not any(l.get("content") == content and l.get("kind") == kind for l in self._lessons.get(ws, [])):
            self._lessons.setdefault(ws, []).append(lesson)
            self._save_lessons(ws)

    def retrieve_relevant(self, workspace_id: str, query: str = "", limit: int = 5, mission_id: Optional[str] = None) -> List[Dict]:
        """Semantic retrieve of past lessons/runs (cross-mission reuse). Scores by BOW cosine on content."""
        ws = str(workspace_id or "aiw")
        self._load_lessons(ws)
        lessons = list(self._lessons.get(ws, []))
        if mission_id:
            lessons = [l for l in lessons if (l.get("metadata") or {}).get("mission_id") == mission_id or not (l.get("metadata") or {}).get("mission_id")]
        if not query:
            return lessons[-limit:]
        qvec = Counter(self._tokenize(query))
        scored = []
        for l in lessons:
            lvec = Counter(self._tokenize(str(l.get("content", "")) + " " + str((l.get("metadata") or {}).get("task", ""))))
            sc = self._cosine(qvec, lvec)
            scored.append((sc, l))
        scored.sort(key=lambda x: x[0], reverse=True)
        out = []
        for sc, l in scored[:limit]:
            r = dict(l)
            r["score"] = round(sc, 4)
            out.append(r)
        return out or lessons[-limit:]

    # Index past runs from disk (run.json) semantically into lessons (idempotent-ish, patterns for success/failure)
    def index_past_runs_semantically(self, workspace_id: str) -> int:
        ws = str(workspace_id or "aiw")
        root = Path(os.environ.get("AIW_ROOT", str(Path(__file__).resolve().parents[2]))).resolve()
        runs_dir = root / ".aiw" / "workspaces" / ws / "agent-iterative-loop" / "runs"
        count = 0
        if not runs_dir.exists():
            return 0
        self._load_lessons(ws)
        for rdir in sorted(runs_dir.iterdir()):
            if not rdir.is_dir():
                continue
            rj = rdir / "run.json"
            if not rj.exists():
                continue
            try:
                r = json.loads(rj.read_text(encoding="utf-8"))
                rid = r.get("run_id")
                task = (r.get("task") or "")[:200]
                status = r.get("status", "")
                mid = r.get("mission_id")
                accum = (r.get("accumulated_context") or "")[:300]
                outcome = "success" if status in ("completed", "dry_run") and r.get("has_real_execution", False) else ("failure" if status in ("blocked", "error") else "run")
                content = f"past_run[{outcome}]: task={task} status={status} mission={mid or '-'} | ctx_snip={accum[:120]}"
                meta = {"run_id": rid, "mission_id": mid, "task": task, "status": status, "source": "past_run_index"}
                # store as lesson (store_lesson dedups)
                self.store_lesson(ws, content, kind=f"past_{outcome}", metadata=meta)
                count += 1
                if count > 20:
                    break  # surgical bound
            except Exception:
                continue
        self._save_lessons(ws)
        return count

    # High-level memory for self-improvement (persist proposed/tested/adopted improvements)
    def store_improvement(self, workspace_id: str, improvement: dict):
        """Store an adopted improvement (e.g. new action_hint pattern or replan heuristic) as high-level memory."""
        meta = improvement.get("metadata") or improvement.get("meta") or {}
        item = MemoryItem(json.dumps(improvement, ensure_ascii=False), kind="high_level_improvement", metadata=meta)
        self.store(workspace_id, item)

    def get_high_level_improvements(self, workspace_id: str, limit: int = 10) -> List[Dict]:
        """Retrieve persisted high-level improvements (used to influence agent behavior)."""
        items = [i for i in self._store.get(workspace_id, []) if getattr(i, "kind", "") == "high_level_improvement"]
        out = []
        for i in items[-limit:]:
            try:
                data = json.loads(i.content) if isinstance(i.content, str) else i.content
            except Exception:
                data = {"raw": i.content}
            out.append({"improvement": data, "kind": i.kind, "ts": i.timestamp, "metadata": i.metadata})
        return out

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
    # High-level improvements (self-improvement via Experiment Lab) surfaced in context
    highs = ltm.get_high_level_improvements(workspace_id, limit=3)
    high_str = ""
    if highs:
        high_str = "\nHigh-level improvements (adopted via experiment):\n" + "\n".join(
            f"  - {h.get('improvement',{}).get('type','imp')}: {str(h.get('improvement',{}))[:120]}" for h in highs
        )
    base = f"Recent:\n{recent}\n\nLong-term relevant:\n{long}" if long else recent
    return base + high_str if high_str else base

def store_high_level_improvement(workspace_id: str, improvement: dict):
    """Convenience: persist improvement (from experiment validate) as high-level memory."""
    get_long_term_memory().store_improvement(workspace_id, improvement)

def get_high_level_improvements(workspace_id: str, limit: int = 10) -> List[Dict]:
    return get_long_term_memory().get_high_level_improvements(workspace_id, limit)

# STEP 2: top-level helper for planner/loop to auto-inject relevant past experiences (lessons + indexed past runs)
# Semantic + cross-mission: past success/failure patterns per ws (and optionally scoped to mission).
def get_relevant_past_experiences(workspace_id: str, task: str = "", mission_id: Optional[str] = None, limit: int = 4) -> List[Dict]:
    ltm = get_long_term_memory()
    # ensure past runs are indexed into lessons for semantic reuse (light, bounded)
    try:
        ltm.index_past_runs_semantically(workspace_id)
    except Exception:
        pass
    return ltm.retrieve_relevant(workspace_id, query=task or "", limit=limit, mission_id=mission_id)

def get_memory_context_with_experiences(workspace_id: str, task: str = "", n: int = 5, mission_id: Optional[str] = None) -> str:
    base = get_memory_context(workspace_id, n)
    exps = get_relevant_past_experiences(workspace_id, task, mission_id=mission_id, limit=3)
    if not exps:
        return base
    exp_lines = []
    for e in exps:
        sc = e.get("score")
        scs = f" (score={sc})" if sc is not None else ""
        exp_lines.append(f"  - [{e.get('kind','past')}{scs}] {str(e.get('content',''))[:140]}")
    return base + "\n\nRelevant past experiences (cross-mission lessons/success-failure patterns; auto-indexed):\n" + "\n".join(exp_lines)
