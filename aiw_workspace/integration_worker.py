import datetime
import json
import uuid
import subprocess
from pathlib import Path
from .profiles import resolve_workspace, AIW_ROOT

def mark_outbox_item_sent(workspace_id: str, item_id: str, pr_number: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "integration-outbox" / item_id
    if not base_dir.is_dir() or not (base_dir / "item.json").exists():
        return {"ok": False, "error": "item_not_found"}
        
    try:
        data = json.loads((base_dir / "item.json").read_text(encoding="utf-8"))
        data["status"] = "sent"
        data["external_sent"] = True
        data["external_sent_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        data["external_target_ref"] = f"github_pr#{pr_number}"
        (base_dir / "item.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def run_worker(workspace_id: str, item_id: str, dry_run: bool = True, confirm_external_send: bool = False, pr_number: str = None) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "integration-outbox" / item_id
    item_path = base_dir / "item.json"
    
    if not base_dir.is_dir() or not item_path.exists():
        return {"ok": False, "error": "item_not_found"}
        
    item_data = json.loads(item_path.read_text(encoding="utf-8"))
    
    if item_data.get("status") != "ready":
        return {"ok": False, "error": f"item is not ready (status: {item_data.get('status')})"}
        
    if item_data.get("target") != "github_pr" or item_data.get("kind") != "pr_summary":
        return {"ok": False, "error": "unsupported target or kind"}
        
    payload_path = base_dir / "payload.md"
    if not payload_path.exists():
        return {"ok": False, "error": "payload.md not found"}
        
    if not dry_run:
        if not confirm_external_send:
            return {"ok": False, "error": "execute requires --confirm-external-send"}
        if not pr_number:
            return {"ok": False, "error": "execute requires --pr-number"}
        if not str(pr_number).isdigit():
            return {"ok": False, "error": "pr-number must be numeric"}
            
    payload_content = payload_path.read_text(encoding="utf-8")
    if "LITELLM_MASTER_KEY" in payload_content or "SECRET_" in payload_content:
        return {"ok": False, "error": "payload contains signs of secrets"}
    
    attempts_dir = base_dir / "attempts"
    attempts_dir.mkdir(parents=True, exist_ok=True)
    
    attempt_id = f"att-{uuid.uuid4().hex[:8]}"
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    
    cmd_args = ["gh", "pr", "edit", str(pr_number or "123"), "--body-file", "payload.md"]
    
    attempt_data = {
        "attempt_id": attempt_id,
        "created_at": now_iso,
        "mode": "dry_run" if dry_run else "execute",
        "target": "github_pr",
        "kind": "pr_summary",
        "pr_number": pr_number,
        "command": cmd_args,
        "executed": False,
        "exit_code": None,
        "status": "dry_run",
        "reason": ""
    }
    
    if dry_run:
        attempt_data["reason"] = "dry run success"
        (attempts_dir / f"{attempt_id}.json").write_text(json.dumps(attempt_data, indent=2), encoding="utf-8")
        return {"ok": True, "attempt": attempt_data}
        
    # Check if gh is installed
    import shutil
    if not shutil.which("gh"):
        attempt_data["status"] = "failed"
        attempt_data["reason"] = "gh cli not found"
        (attempts_dir / f"{attempt_id}.json").write_text(json.dumps(attempt_data, indent=2), encoding="utf-8")
        return {"ok": False, "error": "gh cli not found", "attempt": attempt_data}
        
    # Execute
    try:
        # Resolve payload path absolute for gh
        abs_payload_path = str(payload_path.absolute())
        cmd = ["gh", "pr", "edit", str(pr_number), "--body-file", abs_payload_path]
        
        proc = subprocess.run(
            cmd,
            cwd=str(AIW_ROOT),
            text=True,
            capture_output=True,
            timeout=60,
            shell=False
        )
        attempt_data["executed"] = True
        attempt_data["exit_code"] = proc.returncode
        
        if proc.returncode == 0:
            attempt_data["status"] = "succeeded"
            attempt_data["reason"] = "gh executed successfully"
            mark_outbox_item_sent(workspace_id, item_id, pr_number)
        else:
            attempt_data["status"] = "failed"
            attempt_data["reason"] = f"exit code {proc.returncode}\nstderr: {proc.stderr}"
            
    except Exception as e:
        attempt_data["status"] = "failed"
        attempt_data["reason"] = f"execution error: {e}"
        
    (attempts_dir / f"{attempt_id}.json").write_text(json.dumps(attempt_data, indent=2), encoding="utf-8")
    
    if attempt_data["status"] == "succeeded":
        return {"ok": True, "attempt": attempt_data}
    else:
        return {"ok": False, "error": attempt_data["reason"], "attempt": attempt_data}

def list_item_attempts(workspace_id: str, item_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    attempts_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "integration-outbox" / item_id / "attempts"
    if not attempts_dir.is_dir():
        return {"ok": True, "attempts": []}
        
    attempts = []
    for p in attempts_dir.glob("*.json"):
        try:
            attempts.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            pass
            
    attempts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"ok": True, "attempts": attempts}
