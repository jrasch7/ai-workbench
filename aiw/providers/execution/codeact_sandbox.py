"""CodeAct Sandbox migrado para estrutura atualizada (aiw/providers/execution).

Lógica original de aiw_workspace/codeact_sandbox.py movida aqui como parte da migração para Provider-First.

Mantém toda a segurança e validação.
"""

import json
import uuid
import datetime
import subprocess
import os
import re
from pathlib import Path

# Nota: para compatibilidade durante migração, alguns helpers de workspace ainda são usados via lazy
# Em futuro, mover para aiw/workspace ou providers.

BAD_PATTERNS = [
    ".env", "config/litellm.yaml", "litellm.yaml", "agents.md",
    "import socket", "import requests", "urllib", "http.client",
    "subprocess", "os.system", "popen", "pty", "shutil.rmtree",
    "path.home", "expanduser", "open(", "socket.", "requests.",
    "git push", "git clone", "gh pr", "curl", "wget", "nc ", "ncat",
    "ssh", "scp"
]

SAFE_RUN_ID_RE = re.compile(r"^ca-[0-9a-f]{8}$")

def _get_workspace_helpers():
    from aiw_workspace.profiles import AIW_ROOT, resolve_workspace
    return AIW_ROOT, resolve_workspace

def _codeact_dir(workspace_id: str) -> Path:
    AIW_ROOT, resolve_workspace = _get_workspace_helpers()
    ws = resolve_workspace(workspace_id)
    if not ws:
        return AIW_ROOT / ".aiw" / "workspaces" / workspace_id / "codeact" / "runs"
    return AIW_ROOT / ".aiw" / "workspaces" / ws["id"] / "codeact" / "runs"

def validate_codeact_action(action: dict) -> dict:
    if action.get("kind") != "python_eval":
        return {"status": "blocked", "reason": "unsupported_kind"}
        
    code = action.get("code", "")
    normalized_code = " ".join(code.lower().split())
    for pattern in BAD_PATTERNS:
        if pattern in normalized_code:
            return {"status": "blocked", "reason": "blocked_pattern", "pattern": pattern}
            
    return {"status": "ok"}

def _safe_run_json_path(workspace_id: str, run_id: str) -> Path | None:
    if not run_id or "/" in run_id or "\\" in run_id or ".." in run_id:
        return None
    if Path(run_id).is_absolute() or not SAFE_RUN_ID_RE.fullmatch(run_id):
        return None

    base = _codeact_dir(workspace_id).resolve()
    rf = (base / run_id / "run.json").resolve()
    try:
        rf.relative_to(base)
    except ValueError:
        return None

def run_codeact_action(workspace_id: str, action: dict, confirm: bool = False) -> dict:
    """Executa ação CodeAct de forma segura (migrado)."""
    validation = validate_codeact_action(action)
    if validation["status"] != "ok":
        return validation

    if not confirm:
        return {"status": "blocked", "reason": "confirmation_required"}

    run_id = f"ca-{uuid.uuid4().hex[:8]}"
    base_dir = _codeact_dir(workspace_id) / run_id
    base_dir.mkdir(parents=True, exist_ok=True)

    run_data = {
        "run_id": run_id,
        "workspace_id": workspace_id,
        "action": action,
        "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "running"
    }

    code = action.get("code", "")
    timeout = action.get("timeout_seconds", 30)
    max_stdout = action.get("max_stdout_chars", 10000)

    try:
        proc = subprocess.run(
            ["python3", "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(AIW_ROOT)  # from lazy, but safe
        )
        stdout = proc.stdout[:max_stdout]
        stderr = proc.stderr[:max_stdout]

        run_data.update({
            "status": "completed",
            "stdout": stdout,
            "stderr": stderr,
            "returncode": proc.returncode,
            "completed_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
    except subprocess.TimeoutExpired as e:
        run_data.update({
            "status": "timeout",
            "stdout": e.stdout.decode()[:max_stdout] if e.stdout else "",
            "stderr": "Timeout expired",
            "returncode": -1
        })
    except Exception as e:
        run_data.update({
            "status": "error",
            "stderr": str(e),
            "returncode": -1
        })

    (base_dir / "run.json").write_text(json.dumps(run_data, indent=2, ensure_ascii=False))
    return run_data

def list_codeact_runs(workspace_id: str, limit: int = 20) -> dict:
    base = _codeact_dir(workspace_id)
    if not base.exists():
        return {"runs": []}
    runs = []
    for d in sorted(base.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if not d.is_dir(): continue
        rf = d / "run.json"
        if rf.exists():
            try:
                runs.append(json.loads(rf.read_text()))
            except:
                pass
        if len(runs) >= limit:
            break
    return {"runs": runs}

def read_codeact_run(workspace_id: str, run_id: str) -> dict:
    rf = _safe_run_json_path(workspace_id, run_id)
    if rf is None:
        return {"status": "blocked", "reason": "invalid_run_id"}
    if not rf.exists():
        return {}
    return json.loads(rf.read_text())

def render_codeact_summary(run: dict) -> str:
    lines = [
        f"# CodeAct Run: {run.get('run_id')}",
        f"**Status:** {run.get('status')}",
        f"**Started:** {run.get('started_at')}",
        f"**Finished:** {run.get('finished_at')}",
        f"**Return Code:** {run.get('returncode')}",
        ""
    ]
    if run.get("stdout"):
        lines.append("## STDOUT")
        lines.append("```")
        lines.append(run.get("stdout"))
        lines.append("```")
    if run.get("stderr"):
        lines.append("## STDERR")
        lines.append("```")
        lines.append(run.get("stderr"))
        lines.append("```")
    return "\n".join(lines)

# Reexports for compatibility
__all__ = ["validate_codeact_action", "run_codeact_action", "_codeact_dir", "_safe_run_json_path", "list_codeact_runs", "read_codeact_run", "render_codeact_summary"]
