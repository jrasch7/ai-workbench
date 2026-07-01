import datetime
import json
import uuid
import subprocess
from pathlib import Path
from .profiles import resolve_workspace, AIW_ROOT

def create_patch_intent(workspace_id: str, item_id: str, source_data: dict, kind: str, repo: str, number: int) -> dict:
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / workspace_id / "integration-inbox" / item_id
    
    title = source_data.get("title", "")
    body = source_data.get("body", "")
    state = source_data.get("state", "unknown")
    labels = [l.get("name") for l in source_data.get("labels", [])] if isinstance(source_data.get("labels"), list) else []
    comments_count = len(source_data.get("comments", []))
    
    summary = f"{title}\n\n{body[:500]}..." if len(body) > 500 else f"{title}\n\n{body}"
    summary += f"\n\n[Comments: {comments_count}]"
    
    intent_id = f"pin-{uuid.uuid4().hex[:8]}"
    intent_data = {
        "intent_id": intent_id,
        "workspace_id": workspace_id,
        "source_item_id": item_id,
        "source": "github",
        "kind": kind,
        "repo": repo,
        "number": number,
        "title": title,
        "state": state,
        "labels": labels,
        "summary": summary,
        "requested_change": "Analyze issue and implement changes." if kind == "issue" else "Review PR and adapt.",
        "acceptance_signals": [],
        "risk_flags": [],
        "suggested_next_step": "manual_review",
        "automation_allowed": False
    }
    
    intent_md = f"""# AIW Patch Intent

## Source

- GitHub: {kind}
- Repo: {repo}
- Number: {number}
- Title: {title}
- State: {state}

## Summary

{summary}

## Requested Change

{intent_data['requested_change']}

## Acceptance Signals

None extracted automatically.

## Risk Flags

None extracted automatically.

## Safety

- Automation allowed: false
- Manual review required
- No patch generated automatically
"""

    (base_dir / "patch-intent.json").write_text(json.dumps(intent_data, indent=2), encoding="utf-8")
    (base_dir / "patch-intent.md").write_text(intent_md, encoding="utf-8")
    
    return intent_data

def run_github_intake(workspace_id: str, repo: str, kind: str, number: int, fetch: bool = False, confirm_external_read: bool = False) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    if kind not in ("issue", "pull_request"):
        return {"ok": False, "error": "kind must be issue or pull_request"}
        
    if not repo or "/" not in repo:
        return {"ok": False, "error": "repo must be in format owner/repo"}
        
    if not str(number).isdigit() or int(number) <= 0:
        return {"ok": False, "error": "number must be a positive integer"}
        
    if fetch and not confirm_external_read:
        return {"ok": False, "error": "fetch requires --confirm-external-read"}
        
    item_id = f"in-{uuid.uuid4().hex[:8]}"
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "integration-inbox" / item_id
    base_dir.mkdir(parents=True, exist_ok=True)
    
    attempts_dir = base_dir / "attempts"
    attempts_dir.mkdir(parents=True, exist_ok=True)
    
    attempt_id = f"att-{uuid.uuid4().hex[:8]}"
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    
    if kind == "issue":
        cmd_args = ["gh", "issue", "view", str(number), "--repo", repo, "--json", "number,title,body,state,labels,assignees,author,url,createdAt,updatedAt,comments"]
    else:
        cmd_args = ["gh", "pr", "view", str(number), "--repo", repo, "--json", "number,title,body,state,labels,assignees,author,url,createdAt,updatedAt,headRefName,baseRefName,files,comments,reviews"]
        
    attempt_data = {
        "attempt_id": attempt_id,
        "created_at": now_iso,
        "mode": "fetch" if fetch else "dry_run",
        "command": cmd_args,
        "executed": False,
        "exit_code": None,
        "status": "dry_run",
        "reason": ""
    }
    
    if not fetch:
        attempt_data["reason"] = "dry run success"
        (attempts_dir / f"{attempt_id}.json").write_text(json.dumps(attempt_data, indent=2), encoding="utf-8")
        return {"ok": True, "attempt": attempt_data}
        
    # Execute
    import shutil
    if not shutil.which("gh"):
        attempt_data["status"] = "failed"
        attempt_data["reason"] = "gh cli not found"
        (attempts_dir / f"{attempt_id}.json").write_text(json.dumps(attempt_data, indent=2), encoding="utf-8")
        return {"ok": False, "error": "gh cli not found", "attempt": attempt_data}
        
    try:
        proc = subprocess.run(
            cmd_args,
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
            
            source_data = json.loads(proc.stdout)
            
            # Mask potential secrets manually (very basic)
            stdout_safe = proc.stdout.replace("LITELLM_MASTER_KEY", "[REDACTED]")
            
            # Write source artifacts
            (base_dir / "source.json").write_text(stdout_safe, encoding="utf-8")
            (base_dir / "source.md").write_text(f"```json\n{stdout_safe}\n```", encoding="utf-8")
            
            item_data = {
                "item_id": item_id,
                "workspace_id": ws["id"],
                "created_at": now_iso,
                "source": "github",
                "kind": kind,
                "repo": repo,
                "number": number,
                "status": "fetched",
                "external_read": True,
                "external_modified": False
            }
            (base_dir / "item.json").write_text(json.dumps(item_data, indent=2), encoding="utf-8")
            
            summary_content = f"# Intake: {repo}#{number}\nFetched successfully at {now_iso}."
            (base_dir / "summary.md").write_text(summary_content, encoding="utf-8")
            
            # Create Patch Intent
            create_patch_intent(ws["id"], item_id, source_data, kind, repo, number)
            
        else:
            attempt_data["status"] = "failed"
            attempt_data["reason"] = f"exit code {proc.returncode}\nstderr: {proc.stderr}"
            
    except Exception as e:
        attempt_data["status"] = "failed"
        attempt_data["reason"] = f"execution error: {e}"
        
    (attempts_dir / f"{attempt_id}.json").write_text(json.dumps(attempt_data, indent=2), encoding="utf-8")
    
    if attempt_data["status"] == "succeeded":
        return {"ok": True, "attempt": attempt_data, "item_id": item_id}
    else:
        return {"ok": False, "error": attempt_data["reason"], "attempt": attempt_data}

def list_inbox_items(workspace_id: str, status: str = None) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "integration-inbox"
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

def read_inbox_item(workspace_id: str, item_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "integration-inbox" / item_id
    if not base_dir.is_dir() or not (base_dir / "item.json").exists():
        return {"ok": False, "error": "item_not_found"}
        
    try:
        data = json.loads((base_dir / "item.json").read_text(encoding="utf-8"))
        if (base_dir / "patch-intent.md").exists():
            data["patch_intent_preview"] = (base_dir / "patch-intent.md").read_text(encoding="utf-8")
        return {"ok": True, "item": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def update_inbox_item_status(workspace_id: str, item_id: str, status: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    allowed_statuses = {"draft", "fetched", "ready", "dismissed"}
    if status not in allowed_statuses:
        return {"ok": False, "error": "invalid_status"}
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "integration-inbox" / item_id
    if not base_dir.is_dir() or not (base_dir / "item.json").exists():
        return {"ok": False, "error": "item_not_found"}
        
    try:
        data = json.loads((base_dir / "item.json").read_text(encoding="utf-8"))
        data["status"] = status
        (base_dir / "item.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        return {"ok": True, "item": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def resolve_inbox_item_file(workspace_id: str, item_id: str, filename: str):
    ws = resolve_workspace(workspace_id)
    if not ws:
        return None
        
    if ".." in filename or "/" in filename or "\\" in filename:
        return None
        
    allowed_files = {"item.json", "source.json", "source.md", "patch-intent.json", "patch-intent.md", "summary.md"}
    if filename not in allowed_files:
        return None
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "integration-inbox" / item_id
    fpath = base_dir / filename
    if fpath.is_file():
        return fpath
    return None

def list_inbox_item_attempts(workspace_id: str, item_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    attempts_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "integration-inbox" / item_id / "attempts"
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
