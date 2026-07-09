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

# Usa aiw_runtime equiv para evitar dependência legada de aiw_workspace (reduz legacy deps)
from aiw_runtime.policy import get_aiw_root

# _codeact_dir agora usa namespace simples por workspace_id sob .aiw (sem precisar de resolve_workspace legada)
# Isso suporta melhor a Execução Real via Provedor de Execução (codeact).

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
    """Retorna dir para runs do CodeAct usando aiw_runtime.get_aiw_root() + namespace por workspace_id.
    Evita aiw_workspace legacy. Suporta Provedor de Execução para Loop Iterativo do Agente.
    """
    root = get_aiw_root()
    safe_id = "".join(c for c in (workspace_id or "default") if c.isalnum() or c in "-_")[:64] or "default"
    return root / ".aiw" / "workspaces" / safe_id / "codeact" / "runs"


def _worktrees_dir(workspace_id: str) -> Path:
    """Base dir for git worktrees: .aiw/workspaces/{ws}/worktrees/ used for isolated CodeAct runs."""
    root = get_aiw_root()
    safe_id = "".join(c for c in (workspace_id or "default") if c.isalnum() or c in "-_")[:64] or "default"
    return root / ".aiw" / "workspaces" / safe_id / "worktrees"


def _worktree_dir(workspace_id: str, run_id: str) -> Path:
    """Worktree path for a run: .aiw/workspaces/{ws}/worktrees/{run_id}/ ; cd here for isolated safe edits."""
    return _worktrees_dir(workspace_id) / (run_id or "wt")


def validate_codeact_action(action: dict, profile: dict | None = None) -> dict:
    if action.get("kind") != "python_eval":
        return {"status": "blocked", "reason": "unsupported_kind"}
        
    code = action.get("code", "")
    normalized_code = " ".join(code.lower().split())
    for pattern in BAD_PATTERNS:
        if pattern in normalized_code:
            return {"status": "blocked", "reason": "blocked_pattern", "pattern": pattern}
            
    res = {"status": "ok"}
    # Derive worktree/isolated flag from action (preferred) or profile (default off for compat).
    # Enabled for tasks/actions with 'worktree', 'isolated', or sandbox='worktree'.
    wt = None
    if isinstance(action, dict):
        wt = action.get("worktree")
        if wt is None:
            if action.get("isolated") or action.get("sandbox") in ("worktree", "isolated"):
                wt = True
    if wt is None and isinstance(profile, dict):
        wt = profile.get("worktree") or profile.get("isolated") or profile.get("sandbox") in ("worktree", "isolated")
    if wt:
        res["worktree"] = True
    return res

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

def run_codeact_action(workspace_id: str, action: dict, confirm: bool = False, worktree: bool | None = None, profile: dict | None = None) -> dict:
    """Executa ação CodeAct de forma segura (migrado). Suporta 'worktree' mode (opt-in) para isolated git worktree sandbox.

    - worktree flag from: explicit param, action['worktree'|'isolated'|'sandbox'], or profile.
    - Default: off (full compat).
    - When on: creates git worktree at .aiw/workspaces/{ws}/worktrees/{run_id}/ , cds into it for subprocess,
      integrates _git_ws_gate (confirm + aiw ws) + policy concepts for sandbox/worktree, cleans up after.
    - All safety kept: BAD_PATTERNS, validate, confirm required.
    """
    validation = validate_codeact_action(action, profile=profile)
    if validation["status"] != "ok":
        return validation

    if not confirm:
        return {"status": "blocked", "reason": "confirmation_required"}

    run_id = f"ca-{uuid.uuid4().hex[:8]}"
    base_dir = _codeact_dir(workspace_id) / run_id
    base_dir.mkdir(parents=True, exist_ok=True)

    # Resolve worktree: explicit > action > profile (keeps optional/default-off)
    if worktree is None:
        if isinstance(action, dict):
            if action.get("worktree") is not None:
                worktree = bool(action.get("worktree"))
            elif action.get("isolated") or action.get("sandbox") in ("worktree", "isolated"):
                worktree = True
        if worktree is None and isinstance(profile, dict):
            worktree = bool(
                profile.get("worktree") or profile.get("isolated") or profile.get("sandbox") in ("worktree", "isolated")
            )
    use_worktree = bool(worktree)

    run_data = {
        "run_id": run_id,
        "workspace_id": workspace_id,
        "action": action,
        "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "running",
        "worktree": use_worktree,
    }

    code = action.get("code", "")
    timeout = action.get("timeout_seconds", 30)
    max_stdout = action.get("max_stdout_chars", 10000)
    root = get_aiw_root()

    exec_cwd = str(root)
    wt_path: Path | None = None
    if use_worktree:
        # Integrate with existing _git_ws_gate or policy for 'sandbox' / 'worktree'.
        # worktree creation is a git mutation, so gate applies (requires confirm + aiw ws initially).
        try:
            from aiw_runtime.tools import _git_ws_gate
            allowed, err = _git_ws_gate(confirm=confirm)
            if not allowed:
                run_data.update({
                    "status": "blocked",
                    "reason": "worktree_git_gate_failed",
                    "gate": err,
                })
                (base_dir / "run.json").write_text(json.dumps(run_data, indent=2, ensure_ascii=False))
                return run_data
        except Exception as gate_e:
            run_data.update({
                "status": "blocked",
                "reason": "worktree_gate_unavailable",
                "error": str(gate_e)[:200],
            })
            (base_dir / "run.json").write_text(json.dumps(run_data, indent=2, ensure_ascii=False))
            return run_data

        wt_path = _worktree_dir(workspace_id, run_id)
        try:
            wt_path.parent.mkdir(parents=True, exist_ok=True)
            # Create detached worktree (isolated checkout of current HEAD) for safe edits.
            # cd into it so get_root()/tools inside executed code target the worktree (isolated).
            add_proc = subprocess.run(
                ["git", "worktree", "add", "--detach", str(wt_path)],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=30,
            )
            if add_proc.returncode != 0:
                run_data.update({
                    "status": "blocked",
                    "reason": "worktree_create_failed",
                    "stderr": ((add_proc.stderr or add_proc.stdout) or "")[:500],
                })
                (base_dir / "run.json").write_text(json.dumps(run_data, indent=2, ensure_ascii=False))
                return run_data
            exec_cwd = str(wt_path)
            run_data["worktree_path"] = str(wt_path)
        except Exception as e:
            run_data.update({
                "status": "blocked",
                "reason": "worktree_setup_error",
                "error": str(e)[:200],
            })
            (base_dir / "run.json").write_text(json.dumps(run_data, indent=2, ensure_ascii=False))
            return run_data

    try:
        proc = subprocess.run(
            ["python3", "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=exec_cwd
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
        if use_worktree:
            run_data["executed_in_worktree"] = True
    except subprocess.TimeoutExpired as e:
        stdout_val = (e.stdout or b"").decode("utf-8", errors="replace")[:max_stdout] if isinstance(e.stdout, (bytes, bytearray)) else (e.stdout or "")[:max_stdout]
        run_data.update({
            "status": "timeout",
            "stdout": stdout_val,
            "stderr": "Timeout expired",
            "returncode": -1
        })
    except Exception as e:
        run_data.update({
            "status": "error",
            "stderr": str(e),
            "returncode": -1
        })

    # Cleanup worktree after execution (or block). Always remove to avoid leaks.
    if use_worktree and wt_path is not None:
        try:
            cleanup_proc = subprocess.run(
                ["git", "worktree", "remove", "--force", str(wt_path)],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=30,
            )
            run_data["worktree_cleanup"] = {
                "returncode": cleanup_proc.returncode,
                "stderr": (cleanup_proc.stderr or "")[:200],
            }
            if wt_path.exists():
                # Trusted impl code only (not subject to user BAD_PATTERNS); git remove should suffice.
                import shutil
                shutil.rmtree(str(wt_path), ignore_errors=True)
        except Exception as ce:
            run_data["worktree_cleanup_error"] = str(ce)[:200]

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


# === Simple regression test / note for worktree sandbox support (in-file, no side effects) ===
def _test_worktree_flag_support() -> dict:
    """Regression test helper for worktree mode (called via python -c smoke).

    - Validates flag acceptance in validate_codeact_action (from action + profile).
    - Does NOT create worktrees or run code (requires explicit confirm + git for full path).
    - Note: worktree enabled via action={'worktree':True} or profile={'isolated':True} or 'sandbox':'worktree'.
    - Full flow uses run_codeact_action(..., worktree=True, confirm=True) inside git repo (gated).
    - Keeps BAD_PATTERNS/validate/confirm; integrates _git_ws_gate for worktree.
    """
    try:
        v1 = validate_codeact_action({"kind": "python_eval", "code": "print('hi')", "worktree": True})
        v2 = validate_codeact_action({"kind": "python_eval", "code": "print(42)"}, profile={"isolated": True})
        v3 = validate_codeact_action({"kind": "python_eval", "code": "print(1)", "sandbox": "worktree"})
        v4 = validate_codeact_action({"kind": "python_eval", "code": "print(0)"})
        ok = (
            v1.get("status") == "ok" and v1.get("worktree") is True and
            v2.get("status") == "ok" and v2.get("worktree") is True and
            v3.get("status") == "ok" and v3.get("worktree") is True and
            v4.get("status") == "ok" and "worktree" not in v4
        )
        return {
            "ok": bool(ok),
            "worktree_flag": True,
            "note": "worktree support added (optional, default off); see run_codeact_action + _worktree_dir",
            "paths_example": ".aiw/workspaces/{ws}/worktrees/{run_id}/",
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


# Reexports for compatibility
__all__ = [
    "validate_codeact_action",
    "run_codeact_action",
    "_codeact_dir",
    "_worktrees_dir",
    "_worktree_dir",
    "_safe_run_json_path",
    "list_codeact_runs",
    "read_codeact_run",
    "render_codeact_summary",
]
