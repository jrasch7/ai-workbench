"""Background Daemon/Worker for 24/7 autonomous persistent agents (aiw/queue/worker).

Surgical aiw-first impl:
- Uses (durable disk-backed) AgentQueue for task intake. Persists to .aiw/workspaces/{ws}/queue/queue.json
- On start: calls resume_all_checkpoints_as_daemons to recover previous persistent runs across restarts.
- Enqueue/dequeue auto-persist for true daemon durability (survives process kill/restart).
- Starts multiple persistent runs via aiw.agent.iterative_loop (checkpoint recovery).
- Background via daemon threads (monitorable from cockpit).
- Relies on persistent mode (relaxed MAX, ckpt continuation) + policy gates for safety.
- No new hard limits; recovery on daemon restart by listing checkpoints + durable queue.

Can be used by cockpit, scripts/aiw-*-daemon etc.
Add start_24_7_worker for convenience.
"""

import os
import threading
import time
from typing import Any, Dict, List, Optional

from aiw.queue import get_agent_queue
# Durable queue integration + Step 4 observ (structured logs)
try:
    from aiw.observability import log_structured
except Exception:
    log_structured = lambda *a, **k: None
# Durable queue integration: pass ws for per-workspace .aiw/workspaces/{ws}/queue/queue.json backing

# aiw-first: import the loop daemon starters (relaxed persistent)
try:
    from aiw.agent.iterative_loop import (
        start_persistent_agent_daemon,
        list_running_daemons,
        stop_persistent_agent_daemon,
        run_agent_iterative_loop_once,
    )
except Exception:
    # during bootstrap
    start_persistent_agent_daemon = None
    list_running_daemons = None
    stop_persistent_agent_daemon = None
    run_agent_iterative_loop_once = None


class PersistentAgentWorker:
    """Daemon worker that processes queue items into persistent agent runs (bg, recoverable via ckpts).

    Uses durable AgentQueue (auto-persist on enq/deq). start() triggers resume_all_checkpoints_as_daemons.
    describe() now includes pid, uptime_s, started_at + health for live status (used by aiw-daemon --pidfile / --status, cockpit /api/worker/status). health() for systemd health probes + cockpit real-time.
    """

    def __init__(self, workspace_id: str = "aiw", poll_interval: float = 5.0, max_concurrent: int = 3):
        self.workspace_id = workspace_id
        self.poll_interval = poll_interval
        self.max_concurrent = max_concurrent
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._active_daemons: Dict[str, dict] = {}
        self._lock = threading.Lock()
        # Use per-ws durable queue (disk-backed); on enq/deq it auto-persists
        self._q = get_agent_queue(self.workspace_id)
        self.pid = os.getpid()
        self._started_at = time.time()
        self._last_heartbeat = time.time()
        self._error_count = 0
        self._last_error: Optional[str] = None

    def start(self) -> dict:
        if self._running:
            return {"ok": True, "status": "already_running"}
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name=f"agent-persistent-worker-{self.workspace_id}")
        self._thread.start()
        log_structured("worker_started", workspace_id=self.workspace_id, pid=self.pid)
        # Wire resume_all_checkpoints_as_daemons on worker start for clean 24/7 recovery
        try:
            resume_all_checkpoints_as_daemons(self.workspace_id)
        except Exception:
            pass  # best effort; daemons may start later
        return {"ok": True, "status": "started", "worker": self.describe()}

    def stop(self) -> dict:
        self._running = False
        # best effort stop children
        for did in list(self._active_daemons.keys()):
            try:
                if stop_persistent_agent_daemon:
                    stop_persistent_agent_daemon(did)
            except Exception:
                pass
        # best effort wait for worker thread (non-daemon for join here? but keep as-is for bg)
        if self._thread and self._thread.is_alive():
            try:
                self._thread.join(timeout=3.0)
            except Exception:
                pass
        return {"ok": True, "status": "stopping"}

    def _loop(self):
        while self._running:
            try:
                self._last_heartbeat = time.time()
                self._process_one()
            except Exception as e:
                self._error_count += 1
                self._last_error = str(e)[:200]
                log_structured("worker_loop_err", level="warning", error=str(e)[:120], workspace_id=self.workspace_id)
                # never crash worker; continue for production resilience
            time.sleep(self.poll_interval)

    def _process_one(self):
        # intake + prioritize by mission (for 24/7 production UX: missions get preference)
        items = []
        try:
            # drain a few to allow priority sort (small batch for surgical)
            for _ in range(min(5, getattr(self._q, "_items", []) and len(self._q._items) or 3)):
                it = self._q.dequeue()
                if it:
                    items.append(it)
        except Exception:
            pass
        if not items:
            return
        # sort: missions first (by field or task marker), then higher priority (lower num = higher), stable
        def _mission_pri_key(it):
            mid = getattr(it, "mission_id", None)
            t = getattr(it, "task", "") or ""
            has_m = bool(mid) or ("[mission:" in str(t))
            pri = getattr(it, "priority", 5) or 5
            return (0 if has_m else 1, pri)
        items.sort(key=_mission_pri_key)
        item = items[0]
        # re-enqueue any non-chosen (preserves order lightly)
        for extra in items[1:]:
            try:
                self._q.enqueue(getattr(extra, "workspace_id", self.workspace_id), getattr(extra, "task", ""), getattr(extra, "priority", 5), getattr(extra, "mission_id", None))
            except Exception:
                pass

        ws = getattr(item, "workspace_id", None) or self.workspace_id
        task = getattr(item, "task", None) or str(item)
        mid = getattr(item, "mission_id", None)

        # Daemon reacts to real GitHub events (issue/PR comment/CI failure) -> auto-create mission if marker present (builds on github_intake)
        if not mid and ("[github:" in str(task) or "github_event" in str(task).lower() or "ci fail" in str(task).lower() or "pr comment" in str(task).lower()):
            try:
                from aiw.integration.github_intake import github_event_to_mission
                # parse minimal from task e.g. [github:issue:owner/r#123]
                import re
                m = re.search(r"github:([^:]+):([^#]+)#(\d+)", str(task))
                if m:
                    gkind, grepo, gnum = m.group(1), m.group(2), int(m.group(3))
                    gres = github_event_to_mission(ws, grepo, gkind, gnum, fetch=False, confirm_external_read=False, auto_start=False)
                    mid = gres.get("mission_id") or mid
                    if gres.get("ok"):
                        task = f"[mission:{mid}] {task}"
            except Exception:
                pass  # best effort; continue with mid=None or existing

        with self._lock:
            if len(self._active_daemons) >= self.max_concurrent:
                # re-enqueue lightly or drop (policy decides via run)
                try:
                    self._q.enqueue(ws, task, priority=1, mission_id=mid)  # low pri requeue
                except Exception:
                    pass
                return

        # Start via the persistent daemon helper (uses loop + ckpt + queue already enqueued)
        if start_persistent_agent_daemon:
            res = start_persistent_agent_daemon(
                workspace_id=ws,
                task=task,
                execute=True,
                confirm=True,  # gates still apply inside loop
                profile=None,
                mission_id=mid,
            )
            did = res.get("daemon_id") or res.get("run_id")
            if did:
                with self._lock:
                    self._active_daemons[did] = {"item": getattr(item, "to_dict", lambda: item)(), "started": time.time(), "res": res, "mission_id": mid, "task": task[:120]}
        else:
            # fallback direct persistent run (non-daemon thread here)
            if run_agent_iterative_loop_once:
                try:
                    run_agent_iterative_loop_once(ws, task, persistent=True, execute=True, confirm_agent_loop=True, max_iterations=0, mission_id=mid)
                except Exception as e:
                    self._error_count += 1
                    self._last_error = str(e)[:200]
                    pass

    def describe(self) -> dict:
        h = self.health()
        with self._lock:
            active = list(self._active_daemons.keys())
            active_details = []
            for did in active:
                inf = self._active_daemons.get(did, {})
                det = {"daemon_id": did, "mission_id": inf.get("mission_id"), "task": inf.get("task")}
                # live status: try load current iter/task from run on disk (aiw-first, best-effort)
                try:
                    rid = did
                    root = __import__("pathlib").Path(__import__("os").environ.get("AIW_ROOT", ".")).resolve()
                    rj = root / ".aiw" / "workspaces" / self.workspace_id / "agent-iterative-loop" / "runs" / rid / "run.json"
                    if rj.exists():
                        r = __import__("json").loads(rj.read_text(encoding="utf-8"))
                        det["current_iter"] = r.get("total_iterations_executed") or r.get("last_iteration", 0)
                        det["status"] = r.get("status")
                        det["task"] = det.get("task") or (r.get("task") or "")[:120]
                        det["mission_id"] = det.get("mission_id") or r.get("mission_id")
                except Exception:
                    pass
                active_details.append(det)
        uptime = time.time() - getattr(self, "_started_at", time.time())
        d = {
            "workspace_id": self.workspace_id,
            "running": self._running,
            "poll_interval": self.poll_interval,
            "max_concurrent": self.max_concurrent,
            "active_count": len(active),
            "active_daemons": active,
            "active_details": active_details,  # includes current_iter, task, mission for live UX
            "pid": getattr(self, "pid", None),
            "uptime_s": round(uptime, 1),
            "started_at": getattr(self, "_started_at", None),
        }
        d.update({"health": h.get("healthy", False), "last_heartbeat_s": h.get("last_heartbeat_s")})
        return d

    def health(self) -> dict:
        """Basic production health check for systemd/cockpit monitoring. File/HTTP consumers can poll describe or this."""
        with self._lock:
            active = list(self._active_daemons.keys())
        uptime = time.time() - getattr(self, "_started_at", time.time())
        hb = getattr(self, "_last_heartbeat", self._started_at)
        hb_age = time.time() - hb
        # healthy if running and not too many errors, and heartbeat recent (< 2*poll)
        is_healthy = bool(self._running) and (getattr(self, "_error_count", 0) < 100) and (hb_age < max(30.0, self.poll_interval * 2))
        return {
            "ok": True,
            "healthy": is_healthy,
            "running": self._running,
            "active_count": len(active),
            "active_daemons": active,
            "active_details": [self._active_daemons.get(d, {}) for d in active],  # live mission/task/iter surface
            "pid": getattr(self, "pid", None),
            "uptime_s": round(uptime, 1),
            "last_heartbeat_s": round(hb_age, 1),
            "error_count": getattr(self, "_error_count", 0),
            "last_error": getattr(self, "_last_error", None),
            "max_concurrent": self.max_concurrent,
            "poll_interval": self.poll_interval,
        }

    def list_daemons(self) -> dict:
        base = list_running_daemons(self.workspace_id) if list_running_daemons else {"daemons": []}
        with self._lock:
            base["worker_active"] = list(self._active_daemons.keys())
            base["active_details"] = []
            for did, inf in self._active_daemons.items():
                ddet = {"daemon_id": did, "mission_id": inf.get("mission_id"), "task": inf.get("task"), "started": inf.get("started")}
                # enrich live current iter/task from disk run (for cockpit describe UX)
                try:
                    rid = did
                    import json, os
                    from pathlib import Path
                    root = Path(os.environ.get("AIW_ROOT", ".")).resolve()
                    rj = root / ".aiw" / "workspaces" / self.workspace_id / "agent-iterative-loop" / "runs" / rid / "run.json"
                    if rj.exists():
                        r = json.loads(rj.read_text(encoding="utf-8"))
                        ddet["current_iter"] = r.get("total_iterations_executed") or 0
                        ddet["current_status"] = r.get("status")
                        ddet["mission_id"] = ddet.get("mission_id") or r.get("mission_id")
                except Exception:
                    pass
                base["active_details"].append(ddet)
        # live status: surface worker pid/uptime if present on the singleton
        try:
            w = get_persistent_worker(self.workspace_id)
            base["worker_pid"] = getattr(w, "pid", None)
            base["worker_uptime_s"] = round(time.time() - getattr(w, "_started_at", time.time()), 1) if hasattr(w, "_started_at") else None
        except Exception:
            pass
        return base


# Global singleton worker per ws (for cockpit start/monitor)
_workers: Dict[str, PersistentAgentWorker] = {}
_worker_lock = threading.Lock()


def get_persistent_worker(workspace_id: str = "aiw") -> PersistentAgentWorker:
    with _worker_lock:
        if workspace_id not in _workers:
            _workers[workspace_id] = PersistentAgentWorker(workspace_id=workspace_id)
        return _workers[workspace_id]


def start_daemon_worker(workspace_id: str = "aiw", **opts) -> dict:
    """Start (durable) daemon worker. For full 24/7 recovery use start_24_7_worker."""
    w = get_persistent_worker(workspace_id)
    # ensure queue for ws (triggers load from disk if present)
    try:
        get_agent_queue(workspace_id)
    except Exception:
        pass
    return w.start()


def stop_daemon_worker(workspace_id: str = "aiw") -> dict:
    w = get_persistent_worker(workspace_id)
    return w.stop()


def list_daemon_workers(workspace_id: str = None) -> dict:
    res = {}
    with _worker_lock:
        for ws, w in _workers.items():
            if workspace_id and ws != workspace_id:
                continue
            res[ws] = w.describe()
    return {"ok": True, "workers": res}


def worker_health(workspace_id: str = "aiw") -> dict:
    """Expose health for cockpit / --status consumers (production-grade)."""
    try:
        w = get_persistent_worker(workspace_id)
        return w.health()
    except Exception as e:
        return {"ok": False, "healthy": False, "error": str(e)}


# For direct use / recovery: resume any checkpointed run as daemon
# Cleanly exposes checkpoint-based recovery (scans .aiw/.../checkpoints + persistent runs)
def resume_all_checkpoints_as_daemons(workspace_id: str = "aiw") -> dict:
    """Resume checkpoints as daemons (primary for 24/7 restart recovery)."""
    resumed = []
    ws = str(workspace_id or "aiw")
    seen = set()
    try:
        # Prefer direct checkpoint scan for recovery (even if run status not 'in_progress')
        import json
        from pathlib import Path
        import os
        root = Path(os.environ.get("AIW_ROOT", str(Path.cwd()))).resolve()
        ck_dir = root / ".aiw" / "workspaces" / ws / "agent-iterative-loop" / "checkpoints"
        if ck_dir.exists():
            for p in sorted(ck_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:20]:
                try:
                    ck = json.loads(p.read_text(encoding="utf-8"))
                    rid = ck.get("run_id") or p.stem
                    if not rid or rid in seen:
                        continue
                    seen.add(rid)
                    task = (ck.get("run") or {}).get("task") or ck.get("task") or f"resume from checkpoint {rid}"
                    if start_persistent_agent_daemon:
                        dres = start_persistent_agent_daemon(ws, task, resume_run_id=rid, execute=True, confirm=True)
                        resumed.append(dres)
                except Exception:
                    pass
        # Fallback/augment via list (for flagged persistent runs without ckpt yet)
        from aiw.agent.iterative_loop import list_agent_loop_runs
        runs = list_agent_loop_runs(ws, limit=20).get("runs", [])
        for r in runs:
            rid = r.get("run_id")
            if not rid or rid in seen:
                continue
            if r.get("persistent") and r.get("status") in ("in_progress", "resumed", "created", "running", None, ""):
                seen.add(rid)
                task = r.get("task") or f"resume persistent {rid}"
                if start_persistent_agent_daemon:
                    dres = start_persistent_agent_daemon(ws, task, resume_run_id=rid, execute=True, confirm=True)
                    resumed.append(dres)
    except Exception as e:
        return {"ok": False, "error": str(e), "resumed": resumed}
    return {"ok": True, "resumed": resumed, "count": len(resumed)}


# Simple 24/7 helper: starts the durable worker + triggers resume for full daemon recovery
def start_24_7_worker(workspace_id: str = "aiw", **opts) -> dict:
    """Convenience to start PersistentAgentWorker in durable mode for 24/7.
    Calls start (which does resume) + ensures queue is loaded/persisted.
    """
    w = get_persistent_worker(workspace_id)
    res = w.start()
    # Ensure queue loaded for this ws (durable init does load)
    try:
        q = get_agent_queue(workspace_id)
        q.load()  # idempotent refresh
        # optional: clear old completed on start
        q.clear_completed()
    except Exception:
        pass
    # resume again for good measure (idempotent-ish)
    try:
        resume_all_checkpoints_as_daemons(workspace_id)
    except Exception:
        pass
    res["24_7"] = True
    return res
