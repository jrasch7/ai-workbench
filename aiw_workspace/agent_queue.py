import datetime
import json
import uuid
import subprocess
from pathlib import Path
from .profiles import resolve_workspace, AIW_ROOT

def create_queue_item_from_inbox(workspace_id: str, inbox_item_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    inbox_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "integration-inbox" / inbox_item_id
    if not inbox_dir.is_dir() or not (inbox_dir / "patch-intent.json").exists():
        return {"ok": False, "error": "inbox_item_not_found_or_no_patch_intent"}
        
    intent_data = json.loads((inbox_dir / "patch-intent.json").read_text(encoding="utf-8"))
    
    queue_item_id = f"aq-{uuid.uuid4().hex[:8]}"
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "agent-queue" / queue_item_id
    base_dir.mkdir(parents=True, exist_ok=True)
    
    attempts_dir = base_dir / "attempts"
    attempts_dir.mkdir(parents=True, exist_ok=True)
    
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    
    item_data = {
        "queue_item_id": queue_item_id,
        "workspace_id": ws["id"],
        "created_at": now_iso,
        "source": "integration_inbox",
        "source_item_id": inbox_item_id,
        "patch_intent_id": intent_data.get("intent_id", ""),
        "status": "draft",
        "automation_allowed": False,
        "execution_mode": "manual",
        "llm_required": False,
        "external_calls_allowed": False
    }
    
    title = intent_data.get("title", "")
    repo = intent_data.get("repo", "")
    number = intent_data.get("number", "")
    kind = intent_data.get("kind", "")
    summary = intent_data.get("summary", "")
    req_change = intent_data.get("requested_change", "")
    
    task_md = f"""# AIW Agent Task

## Source

- Inbox item: {inbox_item_id}
- Repo: {repo}
- Kind: {kind}
- Number: {number}
- Title: {title}

## Requested Change

{req_change}

## Acceptance Signals

None

## Safety

- Do not auto-apply.
- Do not auto-commit.
- Do not push.
- Do not read .env.
- Generate a patch preview first.
- Run validation plan before apply.
"""

    constraints_md = """# AIW Execution Constraints

- No .env access.
- No AGENTS.md changes.
- No config/litellm.yaml changes.
- No Hermes/OpenHands.
- No auto-commit.
- No auto-push.
- No auto-apply.
- Use patch preview.
- Use Review Gate.
"""

    plan_md = """# Initial Plan

1. Read patch intent.
2. Inspect workspace context.
3. Produce patch preview.
4. Generate validation plan.
5. Run manual validations.
6. Create evidence bundle.
7. Await human apply-reviewed.
"""

    (base_dir / "item.json").write_text(json.dumps(item_data, indent=2), encoding="utf-8")
    (base_dir / "task.md").write_text(task_md, encoding="utf-8")
    (base_dir / "constraints.md").write_text(constraints_md, encoding="utf-8")
    (base_dir / "plan.md").write_text(plan_md, encoding="utf-8")
    (base_dir / "summary.md").write_text(f"# Queue Item: {queue_item_id}\nSource: {repo}#{number} ({kind})\n", encoding="utf-8")
    
    return {"ok": True, "item": item_data}

def list_queue_items(workspace_id: str, status: str = None) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "agent-queue"
    if not base_dir.is_dir():
        return {"ok": True, "items": []}
        
    items = []
    for p in base_dir.iterdir():
        if p.is_dir() and (p / "item.json").exists():
            try:
                data = json.loads((p / "item.json").read_text(encoding="utf-8"))
                if status and data.get("status") != status:
                    continue
                items.append(data)
            except Exception:
                continue
                
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"ok": True, "items": items}

def read_queue_item(workspace_id: str, queue_item_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "agent-queue" / queue_item_id
    if not base_dir.is_dir() or not (base_dir / "item.json").exists():
        return {"ok": False, "error": "item_not_found"}
        
    try:
        data = json.loads((base_dir / "item.json").read_text(encoding="utf-8"))
        if (base_dir / "task.md").exists():
            data["task_preview"] = (base_dir / "task.md").read_text(encoding="utf-8")
        return {"ok": True, "item": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def update_queue_item_status(workspace_id: str, queue_item_id: str, status: str, confirm: bool = False) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    if not confirm:
        return {"ok": False, "error": "confirmation_required"}
        
    allowed_statuses = {"draft", "ready", "running", "completed", "failed", "dismissed"}
    if status not in allowed_statuses:
        return {"ok": False, "error": "invalid_status"}
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "agent-queue" / queue_item_id
    if not base_dir.is_dir() or not (base_dir / "item.json").exists():
        return {"ok": False, "error": "item_not_found"}
        
    try:
        data = json.loads((base_dir / "item.json").read_text(encoding="utf-8"))
        data["status"] = status
        (base_dir / "item.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        return {"ok": True, "item": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def resolve_queue_item_file(workspace_id: str, queue_item_id: str, filename: str):
    ws = resolve_workspace(workspace_id)
    if not ws:
        return None
        
    if ".." in filename or "/" in filename or "\\" in filename:
        return None
        
    allowed_files = {"item.json", "task.md", "plan.md", "constraints.md", "status.json", "summary.md"}
    if filename not in allowed_files:
        return None
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "agent-queue" / queue_item_id
    fpath = base_dir / filename
    if fpath.is_file():
        return fpath
    return None

def list_queue_item_attempts(workspace_id: str, queue_item_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    attempts_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "agent-queue" / queue_item_id / "attempts"
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

def run_queue_item_offline(workspace_id: str, queue_item_id: str, confirm: bool = False) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    if not confirm:
        return {"ok": False, "error": "confirmation_required"}
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "agent-queue" / queue_item_id
    if not base_dir.is_dir() or not (base_dir / "item.json").exists():
        return {"ok": False, "error": "item_not_found"}
        
    data = json.loads((base_dir / "item.json").read_text(encoding="utf-8"))
    
    if data.get("status") != "ready":
        return {"ok": False, "error": "item must be ready"}
        
    update_queue_item_status(workspace_id, queue_item_id, "running", confirm=True)
    
    attempts_dir = base_dir / "attempts"
    attempts_dir.mkdir(parents=True, exist_ok=True)
    
    attempt_id = f"att-{uuid.uuid4().hex[:8]}"
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    
    cmd_args = ["./scripts/aiw-runner-agent", "--offline"]
    
    attempt_data = {
        "attempt_id": attempt_id,
        "created_at": now_iso,
        "command": cmd_args,
        "executed": False,
        "exit_code": None,
        "status": "running",
        "reason": ""
    }
    
    try:
        import os
        env = os.environ.copy()
        env["AIW_AGENT_OFFLINE"] = "1"
        env["AIW_WORKSPACE_ID"] = ws["id"]
        
        proc = subprocess.run(
            cmd_args,
            cwd=str(AIW_ROOT),
            env=env,
            text=True,
            capture_output=True,
            timeout=120,
            shell=False
        )
        
        attempt_data["executed"] = True
        attempt_data["exit_code"] = proc.returncode
        
        if proc.returncode == 0:
            attempt_data["status"] = "succeeded"
            attempt_data["reason"] = "offline runner executed successfully"
            update_queue_item_status(workspace_id, queue_item_id, "completed", confirm=True)
        else:
            attempt_data["status"] = "failed"
            attempt_data["reason"] = f"exit code {proc.returncode}\nstderr: {proc.stderr[:1000]}"
            update_queue_item_status(workspace_id, queue_item_id, "failed", confirm=True)
            
    except Exception as e:
        attempt_data["status"] = "failed"
        attempt_data["reason"] = f"execution error: {e}"
        update_queue_item_status(workspace_id, queue_item_id, "failed", confirm=True)
        
    (attempts_dir / f"{attempt_id}.json").write_text(json.dumps(attempt_data, indent=2), encoding="utf-8")
    
    if attempt_data["status"] == "succeeded":
        return {"ok": True, "attempt": attempt_data}
    else:
        return {"ok": False, "error": attempt_data["reason"], "attempt": attempt_data}
