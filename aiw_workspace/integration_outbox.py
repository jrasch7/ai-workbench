import datetime
import json
import uuid
from pathlib import Path
from .profiles import resolve_workspace, AIW_ROOT
from .evidence_export import read_evidence_export, list_evidence_exports

def create_outbox_item(workspace_id: str, patch_id: str, target: str, kind: str, export_id: str = None) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    if target != "github_pr" or kind != "pr_summary":
        return {"ok": False, "error": "unsupported_target_or_kind"}
        
    if not export_id:
        ex_payload = list_evidence_exports(ws["id"], patch_id)
        exports = ex_payload.get("exports", [])
        if not exports:
            return {"ok": False, "error": "no_evidence_export_found"}
        export_id = exports[0].get("export_id")
        
    export_payload = read_evidence_export(ws["id"], patch_id, export_id)
    if not export_payload.get("ok"):
        return {"ok": False, "error": f"export_error: {export_payload.get('error')}"}
        
    export_data = export_payload.get("export", {})
    file_contents = export_data.get("file_contents", {})
    
    pr_summary = file_contents.get("pr-summary.md", "")
    if not pr_summary:
        return {"ok": False, "error": "pr-summary.md not found in export"}
        
    item_id = f"out-{uuid.uuid4().hex[:8]}"
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "integration-outbox" / item_id
    base_dir.mkdir(parents=True, exist_ok=True)
    
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    
    # payload.md
    payload_md = f"<!-- Generated locally by AIW Integration Outbox. Review before sending. -->\n\n{pr_summary}"
    (base_dir / "payload.md").write_text(payload_md, encoding="utf-8")
    
    # payload.json
    payload_json = {
        "target": target,
        "kind": kind,
        "body_markdown": payload_md,
        "source": {
            "workspace_id": ws["id"],
            "patch_id": patch_id,
            "export_id": export_id,
            "bundle_id": export_data.get("bundle_id")
        }
    }
    (base_dir / "payload.json").write_text(json.dumps(payload_json, indent=2), encoding="utf-8")
    
    # command-preview.sh
    cmd_preview = (
        "#!/bin/bash\n"
        "# Preview only. Do not execute automatically.\n"
        "# Example:\n"
        "# gh pr edit <PR_NUMBER> --body-file payload.md\n"
    )
    (base_dir / "command-preview.sh").write_text(cmd_preview, encoding="utf-8")
    
    # item.json
    item_data = {
        "item_id": item_id,
        "workspace_id": ws["id"],
        "patch_id": patch_id,
        "bundle_id": export_data.get("bundle_id"),
        "export_id": export_id,
        "created_at": now_iso,
        "target": target,
        "kind": kind,
        "status": "draft",
        "source_files": {
            "pr_summary": "payload.md"
        },
        "safe_to_send": False,
        "external_sent": False
    }
    (base_dir / "item.json").write_text(json.dumps(item_data, indent=2), encoding="utf-8")
    
    return {"ok": True, "item": item_data}

def list_outbox_items(workspace_id: str, patch_id: str = None, status: str = None) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "integration-outbox"
    if not base_dir.is_dir():
        return {"ok": True, "items": []}
        
    items = []
    for p in base_dir.iterdir():
        if p.is_dir() and (p / "item.json").exists():
            try:
                data = json.loads((p / "item.json").read_text(encoding="utf-8"))
                if patch_id and data.get("patch_id") != patch_id:
                    continue
                if status and data.get("status") != status:
                    continue
                items.append(data)
            except Exception:
                continue
                
    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"ok": True, "items": items}

def read_outbox_item(workspace_id: str, item_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "integration-outbox" / item_id
    if not base_dir.is_dir() or not (base_dir / "item.json").exists():
        return {"ok": False, "error": "item_not_found"}
        
    try:
        data = json.loads((base_dir / "item.json").read_text(encoding="utf-8"))
        # attach a preview of payload.md for UI convenience
        if (base_dir / "payload.md").exists():
            data["payload_preview"] = (base_dir / "payload.md").read_text(encoding="utf-8")
        return {"ok": True, "item": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def update_outbox_item_status(workspace_id: str, item_id: str, status: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    allowed_statuses = {"draft", "ready", "copied", "dismissed"}
    if status not in allowed_statuses:
        if status == "sent":
            return {"ok": False, "error": "status 'sent' can only be set by the integration worker"}
        return {"ok": False, "error": "invalid_status"}
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "integration-outbox" / item_id
    if not base_dir.is_dir() or not (base_dir / "item.json").exists():
        return {"ok": False, "error": "item_not_found"}
        
    try:
        data = json.loads((base_dir / "item.json").read_text(encoding="utf-8"))
        data["status"] = status
        if status == "ready":
            data["safe_to_send"] = True
        elif status == "dismissed":
            data["safe_to_send"] = False
        (base_dir / "item.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        return {"ok": True, "item": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def resolve_outbox_item_file(workspace_id: str, item_id: str, filename: str):
    ws = resolve_workspace(workspace_id)
    if not ws:
        return None
        
    if ".." in filename or "/" in filename or "\\" in filename:
        return None
        
    allowed_files = {"item.json", "payload.md", "payload.json", "command-preview.sh", "summary.md"}
    if filename not in allowed_files:
        return None
        
    base_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "integration-outbox" / item_id
    fpath = base_dir / filename
    if fpath.is_file():
        return fpath
    return None
