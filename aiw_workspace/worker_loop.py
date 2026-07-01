import datetime
import json
import uuid
import time
import subprocess
import signal
import sys
from pathlib import Path
from .profiles import resolve_workspace, AIW_ROOT
from .integration_outbox import list_outbox_items
from .external_worker_policy import can_worker_execute

def _create_run_record(workspace_id: str, mode: str, loop_mode: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return None
        
    runs_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "worker-loop" / "runs"
    run_id = f"wlr-{uuid.uuid4().hex[:8]}"
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
    run_dir = AIW_ROOT / ".aiw" / "workspaces" / workspace_id / "worker-loop" / "runs" / run_id
    (run_dir / "run.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    summary_md = f"# Worker Loop Run: {run_id}\n\n"
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
    item_id = item["item_id"]
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws_id / "integration-outbox" / item_id
    dispatch_path = base_dir / "dispatch.json"
    
    if not dispatch_path.exists():
        return
        
    try:
        dispatch = json.loads(dispatch_path.read_text(encoding="utf-8"))
    except Exception:
        return
        
    if not dispatch.get("enabled") or not dispatch.get("confirm_dispatch"):
        return
        
    run_data["items_eligible"] += 1
    
    policy_res = can_worker_execute(
        workspace_id=ws_id,
        worker_name=dispatch.get("worker_name", "github_pr_edit"),
        action=dispatch.get("action", "pr_edit"),
        mode="manual_cli_only"
    )
    
    run_dir = AIW_ROOT / ".aiw" / "workspaces" / ws_id / "worker-loop" / "runs" / run_data["run_id"]
    item_log = {
        "item_id": item_id,
        "dispatch_id": dispatch.get("dispatch_id"),
        "policy_allowed": policy_res.get("allowed", False),
        "policy_reason": policy_res.get("reason", "")
    }
    
    if not policy_res.get("allowed"):
        run_data["items_blocked"] += 1
        item_log["status"] = "blocked"
        (run_dir / "items" / f"{item_id}.json").write_text(json.dumps(item_log, indent=2), encoding="utf-8")
        _save_run_record(ws_id, run_data["run_id"], run_data)
        return
        
    if not execute:
        run_data["items_executed"] += 1
        run_data["items_succeeded"] += 1
        item_log["status"] = "would_execute"
        (run_dir / "items" / f"{item_id}.json").write_text(json.dumps(item_log, indent=2), encoding="utf-8")
        _save_run_record(ws_id, run_data["run_id"], run_data)
        return
        
    # Execute
    cmd = [
        sys.executable,
        str(AIW_ROOT / "scripts" / "aiw-integration-worker"),
        "--workspace", ws_id,
        "--item", item_id,
        "--execute",
        "--confirm-external-send",
        "--pr-number", str(dispatch.get("pr_number"))
    ]
    
    try:
        run_data["items_executed"] += 1
        proc = subprocess.run(cmd, cwd=str(AIW_ROOT), capture_output=True, text=True, shell=False)
        item_log["exit_code"] = proc.returncode
        # truncate logs safely
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

def run_worker_loop_once(workspace_id: str, execute: bool = False, confirm_worker_loop: bool = False) -> dict:
    if execute and not confirm_worker_loop:
        return {"ok": False, "error": "execute_requires_confirm_worker_loop"}
        
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    run_data = _create_run_record(workspace_id, "execute" if execute else "dry_run", "once")
    
    outbox_res = list_outbox_items(workspace_id, status="ready")
    items = outbox_res.get("items", [])
    
    for item in items:
        if item.get("target") == "github_pr" and item.get("kind") == "pr_summary" and not item.get("external_sent"):
            run_data["items_seen"] += 1
            _process_item(workspace_id, item, run_data, execute)
            
    return {"ok": True, "run": run_data}

def run_worker_loop_watch(workspace_id: str, interval_seconds: int = 30, execute: bool = False, confirm_worker_loop: bool = False):
    if execute and not confirm_worker_loop:
        return {"ok": False, "error": "execute_requires_confirm_worker_loop"}
        
    if interval_seconds < 10 or interval_seconds > 3600:
        return {"ok": False, "error": "interval_seconds must be between 10 and 3600"}
        
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    print(f"Starting Foreground Worker Loop (mode: {'execute' if execute else 'dry_run'}, interval: {interval_seconds}s)")
    print("Press Ctrl+C to exit.")
    
    keep_running = True
    def signal_handler(sig, frame):
        nonlocal keep_running
        print("\nExiting Foreground Worker Loop gracefully...")
        keep_running = False
        
    signal.signal(signal.SIGINT, signal_handler)
    
    while keep_running:
        print(f"[{datetime.datetime.now().isoformat()}] Running loop cycle...")
        res = run_worker_loop_once(workspace_id, execute, confirm_worker_loop)
        if not res.get("ok"):
            print(f"Error in cycle: {res.get('error')}")
            
        if keep_running:
            for _ in range(interval_seconds):
                if not keep_running:
                    break
                time.sleep(1)
                
    return {"ok": True}

def list_worker_loop_runs(workspace_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    runs_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "worker-loop" / "runs"
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

def read_worker_loop_run(workspace_id: str, run_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    run_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "worker-loop" / "runs" / run_id
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
