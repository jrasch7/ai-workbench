import json
import uuid
import datetime
import subprocess
import os
import re
from pathlib import Path
from .profiles import resolve_workspace, AIW_ROOT

BAD_PATTERNS = [
    ".env", "config/litellm.yaml", "litellm.yaml", "agents.md",
    "import socket", "import requests", "urllib", "http.client",
    "subprocess", "os.system", "popen", "pty", "shutil.rmtree",
    "path.home", "expanduser", "open(", "socket.", "requests.",
    "git push", "git clone", "gh pr", "curl", "wget", "nc ", "ncat",
    "ssh", "scp"
]

SAFE_RUN_ID_RE = re.compile(r"^ca-[0-9a-f]{8}$")

def _codeact_dir(workspace_id: str) -> Path:
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
    return rf

def create_codeact_run(workspace_id: str, action: dict) -> dict:
    run_id = f"ca-{uuid.uuid4().hex[:8]}"
    base = _codeact_dir(workspace_id)
    run_dir = base / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    
    (run_dir / "action.json").write_text(json.dumps(action, indent=2))
    
    run_data = {
        "run_id": run_id,
        "workspace_id": workspace_id,
        "status": "created",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    (run_dir / "run.json").write_text(json.dumps(run_data, indent=2))
    return run_data

def run_codeact_action(workspace_id: str, action: dict, confirm: bool = False) -> dict:
    if not confirm:
        return {"status": "blocked", "reason": "confirmation_required"}
        
    val = validate_codeact_action(action)
    if val["status"] != "ok":
        return val
        
    run_data = create_codeact_run(workspace_id, action)
    run_id = run_data["run_id"]
    run_dir = _codeact_dir(workspace_id) / run_id
    
    code = action.get("code", "")
    timeout = action.get("timeout_seconds", 10)
    max_out = action.get("max_stdout_chars", 12000)
    max_err = action.get("max_stderr_chars", 12000)
    
    script_path = run_dir / "script.py"
    script_path.write_text(code, encoding="utf-8")
    
    run_data["started_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    run_data["status"] = "running"
    
    # minimal env
    env = {"PATH": os.environ.get("PATH", ""), "PYTHONPATH": str(AIW_ROOT)}
    
    try:
        proc = subprocess.run(
            ["python3", "-I", str(script_path)],
            cwd=str(run_dir),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            shell=False
        )
        
        stdout = proc.stdout[:max_out]
        stderr = proc.stderr[:max_err]
        
        status = "succeeded" if proc.returncode == 0 else "failed"
        run_data["status"] = status
        run_data["returncode"] = proc.returncode
        
        (run_dir / "stdout.txt").write_text(stdout, encoding="utf-8")
        (run_dir / "stderr.txt").write_text(stderr, encoding="utf-8")
        
        run_data["stdout"] = stdout
        run_data["stderr"] = stderr
        
    except subprocess.TimeoutExpired:
        run_data["status"] = "timeout"
        run_data["error"] = "timeout_expired"
    except Exception as e:
        run_data["status"] = "failed"
        run_data["error"] = str(e)
        
    run_data["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (run_dir / "run.json").write_text(json.dumps(run_data, indent=2))
    
    summary = render_codeact_summary(run_data)
    (run_dir / "summary.md").write_text(summary, encoding="utf-8")
    
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
