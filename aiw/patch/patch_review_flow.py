# MIGRAÇÃO: Lógica movida de aiw_workspace/patch_review_flow.py para aiw/patch/patch_review_flow.py
# aiw_workspace/patch_review_flow.py agora é thin delegate.
# Suporta Fluxo de Revisão de Patch, lifecycle tracking e link com queue/inbox.

"""Fluxo de Revisão de Patch (Patch Review Flow).

Gerencia o ciclo de vida de um patch:
- discover
- link_to_queue
- validação, review_gate, evidence_bundle
- decisão e apply/rollback status

Usado por cockpit e scripts de run-approve/reject.
Integra com Evidence Bundles, Queue Items e Inbox (GitHub Intake).
"""

import json
import datetime
from pathlib import Path

def _get_workspace_helpers():
    # aiw-first prefer after profiles migration (thin compat)
    try:
        from aiw.workspace.profiles import resolve_workspace, AIW_ROOT
    except Exception:
        from aiw_workspace.profiles import resolve_workspace, AIW_ROOT
    return resolve_workspace, AIW_ROOT

def _get_review_helpers():
    # aiw-first: prefer local migrated patch_gate
    from .patch_gate import review_gate_for_patch
    from aiw_workspace.agent_queue import read_queue_item
    return review_gate_for_patch, read_queue_item

# relative for migrated sibling (safe, no legacy)
from .evidence_bundle import list_evidence_bundles


def _get_lifecycle_dir(workspace_id: str) -> Path:
    resolve_workspace, AIW_ROOT = _get_workspace_helpers()
    ws = resolve_workspace(workspace_id)
    if not ws:
        return None
    return AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "patch-review-flow"


def get_patch_lifecycle(workspace_id: str, patch_id: str) -> dict:
    ldir = _get_lifecycle_dir(workspace_id)
    if not ldir:
        return None
    fpath = ldir / patch_id / "lifecycle.json"
    if fpath.exists():
        try:
            return json.loads(fpath.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def save_patch_lifecycle(workspace_id: str, patch_id: str, data: dict):
    ldir = _get_lifecycle_dir(workspace_id)
    if not ldir:
        return
    pdir = ldir / patch_id
    pdir.mkdir(parents=True, exist_ok=True)
    (pdir / "lifecycle.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def _init_lifecycle(workspace_id: str, patch_id: str) -> dict:
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "workspace_id": workspace_id,
        "patch_id": patch_id,
        "queue_item_id": None,
        "source_inbox_item_id": None,
        "patch_intent_id": None,
        "created_at": now_iso,
        "updated_at": now_iso,
        "status": "discovered",
        "agent_attempt_id": None,
        "validation_snapshot_id": None,
        "review_gate_status": None,
        "evidence_bundle_id": None,
        "applied_at": None,
        "rolled_back_at": None
    }


def discover_workspace_patches(workspace_id: str) -> dict:
    resolve_workspace, AIW_ROOT = _get_workspace_helpers()
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    patches = []
    
    def _scan_dir(pdir: Path, source_name: str):
        if not pdir.is_dir():
            return
        for item in pdir.iterdir():
            if item.is_dir() and (item / "patch.json").exists():
                try:
                    pdata = json.loads((item / "patch.json").read_text(encoding="utf-8"))
                    pid = item.name
                    life = get_patch_lifecycle(ws["id"], pid)
                    patches.append({
                        "patch_id": pid,
                        "workspace_id": ws["id"],
                        "changed_files": pdata.get("changed_files", []) or ([pdata.get("path")] if pdata.get("path") else []),
                        "created_at": pdata.get("timestamp") or "",
                        "source": source_name,
                        "has_lifecycle": life is not None,
                        "lifecycle_status": life.get("status", "discovered") if life else "discovered",
                        "linked_queue_item_id": life.get("queue_item_id") if life else None
                    })
                except Exception:
                    pass

    scoped_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "patches"
    legacy_dir = AIW_ROOT / ".aiw" / "patches"
    
    _scan_dir(scoped_dir, "scoped")
    _scan_dir(legacy_dir, "legacy")
    
    patches.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"ok": True, "patches": patches}


def link_patch_to_queue_item(workspace_id: str, patch_id: str, queue_item_id: str) -> dict:
    resolve_workspace, AIW_ROOT = _get_workspace_helpers()
    review_gate_for_patch, read_queue_item = _get_review_helpers()
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    q_res = read_queue_item(workspace_id, queue_item_id)
    if not q_res.get("ok"):
        return {"ok": False, "error": "queue_item_not_found"}
        
    q_item = q_res.get("item", {})
    if q_item.get("status") == "dismissed":
        return {"ok": False, "error": "queue_item_dismissed"}
        
    # Check if patch exists
    scoped_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "patches" / patch_id
    legacy_dir = AIW_ROOT / ".aiw" / "patches" / patch_id
    if not (scoped_dir / "patch.json").exists() and not (legacy_dir / "patch.json").exists():
        return {"ok": False, "error": "patch_not_found"}
        
    life = get_patch_lifecycle(ws["id"], patch_id)
    if not life:
        life = _init_lifecycle(ws["id"], patch_id)
        
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    life["updated_at"] = now_iso
    life["queue_item_id"] = queue_item_id
    life["source_inbox_item_id"] = q_item.get("source_item_id")
    life["patch_intent_id"] = q_item.get("patch_intent_id")
    
    if life["status"] in ("discovered", "linked"):
        life["status"] = "validation_required"
        
    save_patch_lifecycle(ws["id"], patch_id, life)
    return {"ok": True, "lifecycle": life}


def update_patch_lifecycle(workspace_id: str, patch_id: str, updates: dict) -> dict:
    resolve_workspace, AIW_ROOT = _get_workspace_helpers()
    life = get_patch_lifecycle(workspace_id, patch_id)
    if not life:
        life = _init_lifecycle(workspace_id, patch_id)
        
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    life["updated_at"] = now_iso
    for k, v in updates.items():
        life[k] = v
        
    save_patch_lifecycle(workspace_id, patch_id, life)
    return {"ok": True, "lifecycle": life}


def get_patch_review_flow(workspace_id: str, patch_id: str) -> dict:
    resolve_workspace, AIW_ROOT = _get_workspace_helpers()
    review_gate_for_patch, read_queue_item = _get_review_helpers()
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    life = get_patch_lifecycle(ws["id"], patch_id)
    if not life:
        life = _init_lifecycle(ws["id"], patch_id)
        
    q_item_data = None
    if life.get("queue_item_id"):
        q_res = read_queue_item(ws["id"], life["queue_item_id"])
        if q_res.get("ok"):
            q_item_data = q_res.get("item")
            
    gate_data = review_gate_for_patch(ws["id"], patch_id)
    gate_status = gate_data.get("status", "unknown") if gate_data else "unknown"
    gate_score = gate_data.get("score", 0) if gate_data else 0
    
    ev_bundles = list_evidence_bundles(ws["id"], patch_id=patch_id)
    latest_bundle = None
    if ev_bundles.get("ok") and ev_bundles.get("bundles"):
        latest_bundle = ev_bundles["bundles"][0]
        
    # plan snapshots path
    snapshots_dir = AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "validation" / patch_id / "snapshots"
    latest_snapshot = None
    has_plan = False
    if snapshots_dir.is_dir():
        snaps = list(snapshots_dir.glob("*.json"))
        if snaps:
            has_plan = True
            latest_snapshot = sorted([s.name.replace(".json", "") for s in snaps])[-1]
            
    applied = life.get("status") == "applied"
    can_apply = gate_status in ("ready", "docs_only") and not applied and life.get("status") != "rolled_back"
    
    next_action = "unknown"
    if applied:
        next_action = "none"
    elif life.get("status") == "rolled_back":
        next_action = "none"
    elif can_apply:
        next_action = "apply_reviewed_manual"
    elif gate_status == "unknown":
        next_action = "run_validation_plan"
        
    return {
        "ok": True,
        "workspace_id": ws["id"],
        "patch_id": patch_id,
        "status": life.get("status"),
        "queue_item": {
            "queue_item_id": life.get("queue_item_id"),
            "status": q_item_data.get("status") if q_item_data else None
        },
        "validation": {
            "has_plan": has_plan,
            "latest_snapshot_id": latest_snapshot,
            "status": "passed" if latest_snapshot else "unknown"
        },
        "review_gate": {
            "status": gate_status,
            "score": gate_score,
            "can_apply": can_apply
        },
        "evidence": {
            "latest_bundle_id": latest_bundle.get("bundle_id") if latest_bundle else None,
            "decision": latest_bundle.get("decision_record", {}).get("decision") if latest_bundle else None
        },
        "apply": {
            "applied": applied,
            "can_apply_reviewed": can_apply
        },
        "next_action": next_action
    }
