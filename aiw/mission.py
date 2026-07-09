"""Mission wrapper (expanded Step 5).

Supports multiple runs per mission, approvals attach, queue tie-in for persistent/24/7.

Storage: .aiw/workspaces/{ws}/missions/{mis-xxx}/mission.json
- run_ids list (multiple runs)
- approvals: list of {id, status, run_id?, ts, ...}
- title, task, created, status, queue_tied
- Compatible with aiw/agent/iterative_loop run.json (injects mission_id)
- Queue items can reference mission via enqueue + attach patterns

Usage:
  from aiw.mission import create_mission, list_missions, get_mission, attach_run_to_mission, Mission
  m = create_mission("aiw", "Refatorar X + auto PR")
  m.attach_run("ail-xxx")
  m.attach_approval({"approval_id": "ap-1", "status": "approved", "run_id": "ail-xxx"})
  item = m.enqueue("next task for mission")

Exposed via aiw.* and aiw/agent with mission_id=...
Ties to start_persistent_agent_daemon + queue worker.

Surgical aiw-first: stdlib + existing queue/loop; no new deps.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _get_root() -> Path:
    try:
        # parents[1] because aiw/ is direct child of repo root (ai-workbench); fallback parents[2] legacy
        default = str(Path(__file__).resolve().parents[1])
        return Path(os.environ.get("AIW_ROOT", default)).resolve()
    except Exception:
        return Path.cwd().resolve()


def _get_ws(workspace_id: str | None = None) -> str:
    ws = workspace_id or os.environ.get("AIW_WORKSPACE_ID") or "aiw"
    return str(ws)


def _get_missions_dir(workspace_id: str | None = None) -> Path:
    ws = _get_ws(workspace_id)
    d = _get_root() / ".aiw" / "workspaces" / ws / "missions"
    d.mkdir(parents=True, exist_ok=True)
    return d


def create_mission(workspace_id: str | None = None, title: str = "Missão", task: str = "") -> dict:
    """Create a minimal mission container for grouping persistent runs + ckpts + auto-pr."""
    ws = _get_ws(workspace_id)
    mid = "mis-" + uuid.uuid4().hex[:8]
    mdir = _get_missions_dir(ws) / mid
    mdir.mkdir(parents=True, exist_ok=True)
    mission = {
        "mission_id": mid,
        "workspace_id": ws,
        "title": title or "Missão sem título",
        "task": (task or "")[:500],
        "created_at": _now_iso(),
        "status": "active",
        "run_ids": [],
        "approvals": [],
        "queue_tied": True,
        # Budgets + auto-pause/escalation + cost/tokens (Production Observability Step 4)
        "budget": {
            "max_iterations": 100, "spent_iterations": 0,
            "max_cost_usd": None, "spent_cost_usd": 0.0,
            "max_tokens": None, "spent_tokens": 0,
            "paused": False, "escalation": None,
            "per_iter": [],  # list of {iter, cost, tokens}
        },
    }
    (mdir / "mission.json").write_text(json.dumps(mission, indent=2, ensure_ascii=False), encoding="utf-8")
    return mission


def get_mission(mission_id: str, workspace_id: str | None = None) -> dict | None:
    if not mission_id:
        return None
    mj = _get_missions_dir(workspace_id) / str(mission_id) / "mission.json"
    if mj.exists():
        try:
            return json.loads(mj.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _enrich_mission_status(m: dict, ws: str) -> dict:
    """Minimal enrichment: group run_ids + ckpt presence + auto_pr status (from runs on disk)."""
    m = dict(m)  # shallow copy
    run_ids = list(m.get("run_ids", []))
    m["run_count"] = len(run_ids)
    pr_urls: List[str] = []
    auto_pr_status = None
    has_ckpt = False
    persistent_count = 0
    root = _get_root()
    runs_base = root / ".aiw" / "workspaces" / ws / "agent-iterative-loop" / "runs"
    ck_base = root / ".aiw" / "workspaces" / ws / "agent-iterative-loop" / "checkpoints"
    for rid in run_ids:
        try:
            rj = runs_base / rid / "run.json"
            if rj.exists():
                r = json.loads(rj.read_text(encoding="utf-8"))
                if r.get("persistent"):
                    persistent_count += 1
                if r.get("pr_url"):
                    pr_urls.append(r["pr_url"])
                    auto_pr_status = r.get("auto_pr_status") or "created"
                elif r.get("auto_pr"):
                    auto_pr_status = r.get("auto_pr_status") or "proposed"
            # ckpt
            ck = ck_base / f"{rid}.json"
            if ck.exists():
                has_ckpt = True
        except Exception:
            pass
    m["persistent_run_count"] = persistent_count
    m["has_checkpoint"] = has_ckpt or bool(run_ids)  # at least one run implies recoverable via daemon/ckpt list
    m["auto_pr_status"] = auto_pr_status
    m["pr_urls"] = pr_urls
    approvs = m.get("approvals", []) or []
    m["approval_count"] = len(approvs)
    m["last_approval_status"] = approvs[-1].get("status") if approvs else None
    m["queue_refs"] = m.get("queue_refs", [])
    m["status_summary"] = f"{len(run_ids)} runs (persistent:{persistent_count})" + (f" auto_pr:{auto_pr_status}" if auto_pr_status else "") + (f" approvs:{len(approvs)}" if approvs else "")
    # Budget + pause/escalation + cost/tokens (Production Step 4)
    b = m.get("budget") or {}
    m["budget"] = b
    m["budget_status"] = (
        f"iters={b.get('spent_iterations',0)}/{b.get('max_iterations',0)} "
        f"cost=${b.get('spent_cost_usd',0):.4f} toks={b.get('spent_tokens',0)}"
        + (" PAUSED" if b.get("paused") else "")
        + (f" esc:{b.get('escalation')}" if b.get("escalation") else "")
    )
    return m


def list_missions(workspace_id: str | None = None, limit: int = 20) -> list[dict]:
    """List missions (newest first), enriched with persistent/ckpt/auto_pr status for monitor views."""
    mdir = _get_missions_dir(workspace_id)
    ws = _get_ws(workspace_id)
    items = []
    for d in sorted([p for p in mdir.iterdir() if p.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True)[:limit]:
        mj = d / "mission.json"
        if mj.exists():
            try:
                m = json.loads(mj.read_text(encoding="utf-8"))
                items.append(_enrich_mission_status(m, ws))
            except Exception:
                pass
    return items


def attach_run_to_mission(mission_id: str, run_id: str, workspace_id: str | None = None) -> bool:
    """Attach run_id to mission; inject mission_id into run.json (for loop compat) + group with ckpt/auto_pr."""
    if not mission_id or not run_id:
        return False
    ws = _get_ws(workspace_id)
    mj_path = _get_missions_dir(ws) / mission_id / "mission.json"
    if not mj_path.exists():
        return False
    try:
        m = json.loads(mj_path.read_text(encoding="utf-8"))
        if run_id not in m.get("run_ids", []):
            m.setdefault("run_ids", []).append(run_id)
            mj_path.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
        # Extend the agent run.json for compatibility with list/read in loop/cockpit
        root = _get_root()
        run_j = root / ".aiw" / "workspaces" / ws / "agent-iterative-loop" / "runs" / run_id / "run.json"
        if run_j.exists():
            try:
                rdata = json.loads(run_j.read_text(encoding="utf-8"))
                rdata["mission_id"] = mission_id
                run_j.write_text(json.dumps(rdata, indent=2, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass
        return True
    except Exception:
        return False


def apply_mission_budget_spend(mission_id: str, iterations: int = 1, workspace_id: str | None = None,
                               cost_usd: float = 0.0, tokens: int = 0) -> dict:
    """Budgets + auto-pause/escalation + cost/tokens (Step 4 Production Observability & Cost Control).
    Robust: handles iters + cost + tokens; ties to global budget on exceed; escalation strings.
    Auto-pauses mission and can propagate global pause. Idempotent-ish.
    """
    if not mission_id:
        return {"ok": False, "error": "no_mission"}
    ws = _get_ws(workspace_id)
    mj_path = _get_missions_dir(ws) / mission_id / "mission.json"
    if not mj_path.exists():
        return {"ok": False, "error": "mission_not_found"}
    try:
        m = json.loads(mj_path.read_text(encoding="utf-8"))
        b = m.setdefault("budget", {
            "max_iterations": 100, "spent_iterations": 0,
            "max_cost_usd": None, "spent_cost_usd": 0.0,
            "max_tokens": None, "spent_tokens": 0,
            "paused": False, "escalation": None, "per_iter": [],
        })
        b["spent_iterations"] = int(b.get("spent_iterations", 0)) + max(0, int(iterations))
        b["spent_cost_usd"] = round(float(b.get("spent_cost_usd", 0)) + max(0, float(cost_usd)), 6)
        b["spent_tokens"] = int(b.get("spent_tokens", 0)) + max(0, int(tokens))
        paused = False
        esc = b.get("escalation") or None
        if b.get("max_iterations", 0) > 0 and b["spent_iterations"] > int(b["max_iterations"]):
            b["paused"] = True
            esc = (esc or "") + ";iterations_exceeded"
            paused = True
        if b.get("max_cost_usd") and b["spent_cost_usd"] > float(b["max_cost_usd"]):
            b["paused"] = True
            esc = (esc or "") + ";cost_exceeded"
            paused = True
        if b.get("max_tokens") and b["spent_tokens"] > int(b["max_tokens"]):
            b["paused"] = True
            esc = (esc or "") + ";tokens_exceeded"
            paused = True
        b["escalation"] = esc
        if paused:
            m["status"] = "paused"
        # tie to global for robust cross-mission control
        try:
            from aiw.observability import apply_global_budget_spend
            gres = apply_global_budget_spend(cost_delta=cost_usd, tokens_delta=tokens)
            if gres.get("paused"):
                b["paused"] = True
                b["escalation"] = (b.get("escalation") or "") + ";global_budget_trigger"
                m["status"] = "paused"
        except Exception:
            pass
        mj_path.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"ok": True, "budget": b, "paused": b.get("paused"), "escalation": b.get("escalation")}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def attach_approval_to_mission(mission_id: str, approval: dict, workspace_id: str | None = None) -> bool:
    """Attach approval record to mission (supports approvals/queue tie-in for runs).
    approval: dict e.g. {"approval_id": "ap-xxx", "status": "approved|pending|rejected", "run_id": "...", "ts": "...", "by": "cockpit|cli"}
    """
    if not mission_id or not isinstance(approval, dict):
        return False
    ws = _get_ws(workspace_id)
    mj_path = _get_missions_dir(ws) / mission_id / "mission.json"
    if not mj_path.exists():
        return False
    try:
        m = json.loads(mj_path.read_text(encoding="utf-8"))
        approvs = m.setdefault("approvals", [])
        # idempotent-ish: avoid exact dups
        aid = approval.get("approval_id") or approval.get("id")
        if aid and any((a.get("approval_id") or a.get("id")) == aid for a in approvs):
            return True
        approvs.append(dict(approval))
        mj_path.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
        # If tied to a run, also note on run.json for loop/cockpit compat (approvals/queue tie)
        rid = approval.get("run_id")
        if rid:
            root = _get_root()
            run_j = root / ".aiw" / "workspaces" / ws / "agent-iterative-loop" / "runs" / rid / "run.json"
            if run_j.exists():
                try:
                    rdata = json.loads(run_j.read_text(encoding="utf-8"))
                    rdata.setdefault("approvals", []).append(dict(approval))
                    rdata["approval_status"] = approval.get("status", "pending_approval")
                    run_j.write_text(json.dumps(rdata, indent=2, ensure_ascii=False), encoding="utf-8")
                except Exception:
                    pass
        return True
    except Exception:
        return False


def attach_handoff_to_mission(mission_id: str, handoff: dict, workspace_id: str | None = None) -> bool:
    """Basic multi-agent handoff support (planner -> executor seeds).
    handoff e.g. {"from": "planner_agent", "to": "executor_agent", "plan_ref": "...", "mission_id": "...", "ts": "..."}
    Records in mission + mirrors to run if run_id provided (simple collab coordination via shared mission).
    """
    if not mission_id or not isinstance(handoff, dict):
        return False
    ws = _get_ws(workspace_id)
    mj_path = _get_missions_dir(ws) / mission_id / "mission.json"
    if not mj_path.exists():
        return False
    try:
        m = json.loads(mj_path.read_text(encoding="utf-8"))
        handoffs = m.setdefault("handoffs", [])
        hid = handoff.get("handoff_id") or handoff.get("id") or str(len(handoffs))
        if any((h.get("handoff_id") or h.get("id")) == hid for h in handoffs):
            return True
        handoffs.append(dict(handoff))
        mj_path.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
        rid = handoff.get("run_id")
        if rid:
            root = _get_root()
            run_j = root / ".aiw" / "workspaces" / ws / "agent-iterative-loop" / "runs" / rid / "run.json"
            if run_j.exists():
                try:
                    rdata = json.loads(run_j.read_text(encoding="utf-8"))
                    rdata.setdefault("handoffs", []).append(dict(handoff))
                    rdata["last_handoff"] = handoff.get("from") + "->" + handoff.get("to")
                    run_j.write_text(json.dumps(rdata, indent=2, ensure_ascii=False), encoding="utf-8")
                except Exception:
                    pass
        return True
    except Exception:
        return False


def enqueue_mission_task(mission_id: str, task: str = "", priority: int = 5, workspace_id: str | None = None) -> dict:
    """Queue tie-in: enqueue a task associated with this mission (used by `mission run`, worker, cockpit).
    Returns queue item; caller can then start_persistent... with mission_id.
    """
    if not mission_id:
        return {"ok": False, "error": "no_mission"}
    ws = _get_ws(workspace_id)
    try:
        from aiw.queue import get_agent_queue
        q = get_agent_queue(ws)
        t = task or (get_mission(mission_id, ws) or {}).get("task") or "mission task"
        item = q.enqueue(ws, f"[mission:{mission_id}] {t}", priority=priority, mission_id=mission_id)
        # record queue ref lightly in mission for status
        mj_path = _get_missions_dir(ws) / mission_id / "mission.json"
        if mj_path.exists():
            m = json.loads(mj_path.read_text(encoding="utf-8"))
            qrefs = m.setdefault("queue_refs", [])
            qid = getattr(item, "item_id", str(item))
            if qid not in qrefs:
                qrefs.append(qid)
            mj_path.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"ok": True, "item": getattr(item, "to_dict", lambda: item)(), "mission_id": mission_id}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# Mission class (expanded for multiple runs, approvals, queue tie-in)
class Mission:
    """Minimal wrapper that groups persistent run_id + ckpt + auto_pr status.

    Example:
        from aiw.mission import Mission
        m = Mission.create("aiw", title="Long refactor", task="...")
        m.attach_run("ail-abc123")
        print(m.list())  # classmethod or instance
    """
    def __init__(self, data: dict):
        self.data = data or {}
        self.mission_id = self.data.get("mission_id")
        self.workspace_id = self.data.get("workspace_id")

    @staticmethod
    def create(workspace_id: str | None = None, title: str = "Missão", task: str = "") -> "Mission":
        d = create_mission(workspace_id, title, task)
        return Mission(d)

    @staticmethod
    def list(workspace_id: str | None = None, limit: int = 20) -> list["Mission"]:
        return [Mission(d) for d in list_missions(workspace_id, limit)]

    def attach_run(self, run_id: str, workspace_id: str | None = None) -> bool:
        ok = attach_run_to_mission(self.mission_id, run_id, workspace_id or self.workspace_id)
        if ok:
            # refresh
            refreshed = get_mission(self.mission_id, workspace_id or self.workspace_id)
            if refreshed:
                self.data = refreshed
        return ok

    def attach_approval(self, approval: dict, workspace_id: str | None = None) -> bool:
        """Attach approval (for approvals/queue tie-in)."""
        ok = attach_approval_to_mission(self.mission_id, approval, workspace_id or self.workspace_id)
        if ok:
            refreshed = get_mission(self.mission_id, workspace_id or self.workspace_id)
            if refreshed:
                self.data = refreshed
        return ok

    def attach_handoff(self, handoff: dict, workspace_id: str | None = None) -> bool:
        """Basic multi-agent: record planner<->executor handoff on mission for coordination."""
        ok = attach_handoff_to_mission(self.mission_id, handoff, workspace_id or self.workspace_id)
        if ok:
            refreshed = get_mission(self.mission_id, workspace_id or self.workspace_id)
            if refreshed:
                self.data = refreshed
        return ok

    def enqueue(self, task: str = None, priority: int = 5, workspace_id: str | None = None) -> dict:
        """Queue tie-in: enqueue task for this mission (multiple runs supported)."""
        return enqueue_mission_task(self.mission_id, task or "", priority, workspace_id or self.workspace_id)

    def start_run(self, task: str = None, persistent: bool = True, **kwargs) -> dict:
        """Start a (persistent) run for this mission, via queue + daemon if possible.
        Supports multiple runs per mission. Returns daemon/run result.
        """
        ws = self.workspace_id or "aiw"
        t = task or self.data.get("task") or "mission run"
        try:
            from aiw.queue import get_agent_queue
            from aiw.agent.iterative_loop import start_persistent_agent_daemon
            q = get_agent_queue(ws)
            q.enqueue(ws, f"[mission:{self.mission_id}] {t}", priority=5, mission_id=self.mission_id)
            dres = start_persistent_agent_daemon(
                workspace_id=ws,
                task=t,
                persistent=persistent,
                mission_id=self.mission_id,
                **{k: v for k, v in kwargs.items() if k in ("execute", "confirm", "profile", "resume_run_id")}
            )
            rid = dres.get("run_id")
            if rid:
                self.attach_run(rid)
            return {"ok": True, "mission_id": self.mission_id, "daemon": dres, "run_id": rid}
        except Exception as e:
            return {"ok": False, "error": str(e), "mission_id": self.mission_id}

    def list_runs(self, workspace_id: str | None = None) -> List[dict]:
        """List attached runs (enriched from disk)."""
        ws = workspace_id or self.workspace_id
        runs = []
        root = _get_root()
        for rid in (self.data or {}).get("run_ids", []):
            try:
                rj = root / ".aiw" / "workspaces" / (ws or "aiw") / "agent-iterative-loop" / "runs" / rid / "run.json"
                if rj.exists():
                    runs.append(json.loads(rj.read_text(encoding="utf-8")))
            except Exception:
                runs.append({"run_id": rid, "status": "unreadable"})
        return runs

    def refresh(self) -> dict:
        d = get_mission(self.mission_id, self.workspace_id) or {}
        self.data = d
        return d

    def status(self) -> dict:
        """Return enriched status (multiple runs, approvals, queue, persistent/ckpt/auto_pr)."""
        ws = self.workspace_id
        base = _enrich_mission_status(self.data, ws) if self.data else {}
        base["approval_count"] = len((self.data or {}).get("approvals", []))
        base["last_approval"] = ((self.data or {}).get("approvals") or [{}])[-1] if (self.data or {}).get("approvals") else None
        base["queue_refs"] = (self.data or {}).get("queue_refs", [])
        base["run_ids"] = (self.data or {}).get("run_ids", [])
        return base

    def __repr__(self):
        runs = len((self.data or {}).get("run_ids", []))
        appro = len((self.data or {}).get("approvals", []))
        return f"Mission({self.mission_id}, runs={runs}, approvals={appro}, pr={bool((self.data or {}).get('pr_urls'))})"


# Convenience re-exports for direct import
__all__ = [
    "create_mission",
    "list_missions",
    "get_mission",
    "attach_run_to_mission",
    "attach_approval_to_mission",
    "attach_handoff_to_mission",
    "enqueue_mission_task",
    "Mission",
    "_get_missions_dir",
]
