from .profiles import resolve_workspace

def load_external_worker_policy(workspace_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
        
    policy = ws.get("profile", {}).get("external_workers", {})
    return {
        "ok": True,
        "workspace_id": ws["id"],
        "policy": policy
    }

def validate_external_worker_policy(workspace_id: str) -> dict:
    # Just loads and returns as validated since _merge_profile handles schema validation
    return load_external_worker_policy(workspace_id)

def can_worker_execute(workspace_id: str, worker_name: str, action: str, mode: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"allowed": False, "reason": "Workspace not found.", "requires_confirm": True, "mode": "disabled"}
        
    policy = ws.get("profile", {}).get("external_workers", {})
    
    if not policy.get("enabled"):
        return {"allowed": False, "reason": "External workers are globally disabled.", "requires_confirm": True, "mode": "disabled"}
        
    if mode == "background" and not policy.get("allow_background"):
        return {"allowed": False, "reason": "Background workers are disabled.", "requires_confirm": True, "mode": "manual_cli_only"}
        
    if mode == "ui" and not policy.get("allow_ui_execution"):
        return {"allowed": False, "reason": "UI execution is disabled.", "requires_confirm": True, "mode": "manual_cli_only"}
        
    workers = policy.get("workers", [])
    target_worker = next((w for w in workers if w.get("name") == worker_name), None)
    
    if not target_worker:
        return {"allowed": False, "reason": f"Worker '{worker_name}' is not configured.", "requires_confirm": True, "mode": "disabled"}
        
    if not target_worker.get("enabled"):
        return {"allowed": False, "reason": f"Worker '{worker_name}' is disabled.", "requires_confirm": True, "mode": target_worker.get("mode", "disabled")}
        
    if target_worker.get("mode") == "disabled":
        return {"allowed": False, "reason": f"Worker '{worker_name}' mode is disabled.", "requires_confirm": True, "mode": "disabled"}
        
    if target_worker.get("mode") == "manual_cli_only" and mode != "cli":
        return {"allowed": False, "reason": f"Worker '{worker_name}' allows manual CLI execution only.", "requires_confirm": True, "mode": "manual_cli_only"}
        
    if action in target_worker.get("blocked_actions", []):
        return {"allowed": False, "reason": f"Action '{action}' is blocked for worker '{worker_name}'.", "requires_confirm": True, "mode": target_worker.get("mode", "disabled")}
        
    if target_worker.get("allowed_actions") and action not in target_worker.get("allowed_actions", []):
        return {"allowed": False, "reason": f"Action '{action}' is not explicitly allowed for worker '{worker_name}'.", "requires_confirm": True, "mode": target_worker.get("mode", "disabled")}
        
    return {
        "allowed": True,
        "reason": f"Worker '{worker_name}' is allowed to execute '{action}' in '{mode}' mode.",
        "requires_confirm": target_worker.get("requires_confirm", True),
        "mode": target_worker.get("mode", "disabled")
    }
