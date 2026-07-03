import datetime
import json
import re
import uuid
from pathlib import Path

from .capability_registry import get_capability, validate_capability_definition
from .codeact_sandbox import run_codeact_action
from .profiles import AIW_ROOT, resolve_workspace


MAX_ITERATIONS_V1 = 3
SAFE_RUN_ID_RE = re.compile(r"^ail-[0-9a-f]{8}$")


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def _loop_runs_dir(workspace_id: str) -> Path:
    ws = resolve_workspace(workspace_id)
    ws_id = ws["id"] if ws else workspace_id
    return AIW_ROOT / ".aiw" / "workspaces" / ws_id / "agent-iterative-loop" / "runs"


def _loop_run_dir(workspace_id: str, run_id: str) -> Path:
    return _loop_runs_dir(workspace_id) / run_id


def _safe_run_json_path(workspace_id: str, run_id: str) -> Path | None:
    if not run_id or "/" in run_id or "\\" in run_id or ".." in run_id:
        return None
    if Path(run_id).is_absolute() or not SAFE_RUN_ID_RE.fullmatch(run_id):
        return None

    base = _loop_runs_dir(workspace_id).resolve()
    run_json = (base / run_id / "run.json").resolve()
    try:
        run_json.relative_to(base)
    except ValueError:
        return None
    return run_json


def _context_chunks_path(workspace_id: str) -> Path:
    return AIW_ROOT / ".aiw" / "workspaces" / workspace_id / "context" / "chunks.jsonl"


def _context_index_available(workspace_id: str) -> bool:
    chunks_path = _context_chunks_path(workspace_id)
    return chunks_path.is_file() and chunks_path.stat().st_size > 0


def _create_run(workspace_id: str, task: str, mode: str, max_iterations: int, task_source: str) -> dict:
    run_id = f"ail-{uuid.uuid4().hex[:8]}"
    run_dir = _loop_run_dir(workspace_id, run_id)
    (run_dir / "iterations").mkdir(parents=True, exist_ok=True)
    run = {
        "run_id": run_id,
        "workspace_id": workspace_id,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "mode": mode,
        "status": "created",
        "planner": "mock",
        "max_iterations": max_iterations,
        "task": task,
        "task_source": task_source,
        "plan_path": "plan.json",
        "capabilities_checked": [],
        "context_pack_id": None,
        "context_mode": None,
        "context_note": None,
        "iterations": [],
        "blocked_reason": None,
        "run_dir": str(run_dir),
    }
    _save_run(run)
    return run


def build_mock_plan(task: str, max_iterations: int) -> dict:
    """Builds a deterministic offline plan. It never turns task text into code."""
    capped = max(1, min(MAX_ITERATIONS_V1, int(max_iterations or 1)))
    templates = [
        {
            "step": 1,
            "kind": "inspect_context",
            "title": "Inspect available context",
            "uses_codeact": False,
        },
        {
            "step": 2,
            "kind": "codeact_python_eval",
            "title": "Run safe offline CodeAct check",
            "uses_codeact": True,
        },
        {
            "step": 3,
            "kind": "summarize",
            "title": "Summarize offline result",
            "uses_codeact": False,
        },
    ]
    return {
        "planner": "mock",
        "task": task,
        "max_iterations": capped,
        "steps": templates[:capped],
    }


def _save_plan(run: dict, plan: dict) -> None:
    run_dir = _loop_run_dir(run["workspace_id"], run["run_id"])
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")


def _save_run(run: dict) -> None:
    run["updated_at"] = _now_iso()
    run_dir = _loop_run_dir(run["workspace_id"], run["run_id"])
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "summary.md").write_text(_render_summary(run), encoding="utf-8")


def _save_iteration(run: dict, iteration: dict) -> None:
    run_dir = _loop_run_dir(run["workspace_id"], run["run_id"])
    iter_path = run_dir / "iterations" / f"iter-{iteration['iteration']:03d}.json"
    iter_path.parent.mkdir(parents=True, exist_ok=True)
    iter_path.write_text(json.dumps(iteration, indent=2, ensure_ascii=False), encoding="utf-8")
    run["iterations"].append({
        "iteration": iteration["iteration"],
        "status": iteration["status"],
        "artifact": str(iter_path),
    })
    _save_run(run)


def _render_summary(run: dict) -> str:
    lines = [
        f"# Agent Iterative Loop Run: {run.get('run_id')}",
        "",
        f"- Workspace: {run.get('workspace_id')}",
        f"- Status: {run.get('status')}",
        f"- Mode: {run.get('mode')}",
        f"- Planner: {run.get('planner')}",
        f"- Task source: {run.get('task_source')}",
        f"- Max iterations: {run.get('max_iterations')}",
        f"- Plan: {run.get('plan_path')}",
        f"- Context mode: {run.get('context_mode')}",
        f"- Context pack: {run.get('context_pack_id')}",
        f"- Blocked reason: {run.get('blocked_reason')}",
        "",
        "## Task",
        "",
        run.get("task", ""),
        "",
        "## Iterations",
        "",
    ]
    if not run.get("iterations"):
        lines.append("- No iterations recorded yet.")
    for item in run.get("iterations", []):
        lines.append(f"- Iteration {item.get('iteration')}: {item.get('status')} ({item.get('artifact')})")
    lines.extend([
        "",
        "## Safety",
        "",
        "- Offline/manual v1.",
        "- No LLM call.",
        "- No GitHub/Jira write.",
        "- No patch apply, commit, or push.",
        "- CodeAct remains a best-effort host sandbox, not strong isolation.",
    ])
    return "\n".join(lines)


def _check_codeact_capability() -> dict:
    cap = get_capability("codeact_sandbox")
    if not cap:
        return {"name": "codeact_sandbox", "status": "missing", "valid": False}
    return {
        "name": "codeact_sandbox",
        "status": cap.get("status"),
        "risk": cap.get("risk"),
        "requires_confirmation": cap.get("requires_confirmation"),
        "blocked_by_default": cap.get("blocked_by_default"),
        "valid": validate_capability_definition(cap),
    }


def _prepare_context(workspace_id: str, task: str, run: dict, dry_run: bool) -> dict:
    if not _context_index_available(workspace_id):
        return {
            "context_pack_id": None,
            "mode": "minimal",
            "note": "Context index not found; v1 did not rebuild/index the repository automatically.",
            "written": None,
        }

    if dry_run:
        return {
            "context_pack_id": None,
            "mode": "would_build_context_pack",
            "note": "Context index exists; dry-run did not write a context pack.",
            "written": None,
        }

    from aiw_context.context_pack import build_context_pack_from_text, write_context_pack

    pack = build_context_pack_from_text(
        workspace_id=workspace_id,
        title="Agent Iterative Loop Offline v1",
        body=task,
        source_id=run["run_id"],
        max_chunks=3,
        max_chars=4000,
    )
    written = write_context_pack(workspace_id, pack)
    return {
        "context_pack_id": pack["pack_id"],
        "mode": "context_pack",
        "note": "Context pack built from existing local index.",
        "written": written,
    }


def run_agent_iterative_loop_once(
    workspace_id: str,
    task: str,
    dry_run: bool = True,
    execute: bool = False,
    confirm_agent_loop: bool = False,
    max_iterations: int = 1,
    task_source: str = "cli",
) -> dict:
    if dry_run and execute:
        return {"ok": False, "error": "choose_dry_run_or_execute"}
    if max_iterations < 1 or max_iterations > MAX_ITERATIONS_V1:
        return {"ok": False, "error": "max_iterations_must_be_between_1_and_3"}

    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
    ws_id = ws["id"]

    mode = "dry-run" if dry_run or not execute else "offline"
    run = _create_run(ws_id, task, mode, max_iterations, task_source)
    plan = build_mock_plan(task, max_iterations)
    _save_plan(run, plan)
    _save_run(run)

    cap_check = _check_codeact_capability()
    run["capabilities_checked"].append(cap_check)
    if not cap_check.get("valid"):
        run["status"] = "blocked"
        run["blocked_reason"] = "codeact_sandbox_capability_invalid"
        _save_run(run)
        return {"ok": False, "error": run["blocked_reason"], "run": run}

    if execute and not confirm_agent_loop:
        run["status"] = "blocked"
        run["blocked_reason"] = "execute_requires_confirm_agent_loop"
        _save_run(run)
        return {"ok": False, "error": run["blocked_reason"], "run": run}

    context = _prepare_context(ws_id, task, run, dry_run=(mode == "dry-run"))
    run["context_pack_id"] = context.get("context_pack_id")
    run["context_mode"] = context.get("mode")
    run["context_note"] = context.get("note")
    _save_run(run)

    failed = False
    for step in plan["steps"]:
        iteration_num = step["step"]
        iteration = {
            "iteration": iteration_num,
            "step_kind": step["kind"],
            "step_title": step["title"],
            "status": "dry_run" if mode == "dry-run" else "running",
            "uses_codeact": bool(step["uses_codeact"]),
            "capability": "codeact_sandbox",
            "context_pack_id": run.get("context_pack_id"),
            "codeact_run_id": None,
            "stdout_preview": "",
            "stderr_preview": "",
            "error": None,
        }

        if mode == "dry-run":
            if step["uses_codeact"]:
                iteration["stdout_preview"] = "Would execute fixed safe offline CodeAct action."
            else:
                iteration["stdout_preview"] = f"Would complete mock planner step: {step['kind']}."
            _save_iteration(run, iteration)
            continue

        if not step["uses_codeact"]:
            iteration["status"] = "completed"
            iteration["stdout_preview"] = f"Completed mock planner step: {step['kind']}."
            _save_iteration(run, iteration)
            continue

        action = {
            "kind": "python_eval",
            "title": "AIW Agent Iterative Loop Mock Planner Step",
            "code": "print('AIW_AGENT_ITERATIVE_LOOP_STEP_OK')",
            "timeout_seconds": 5,
            "max_stdout_chars": 2000,
            "max_stderr_chars": 2000,
        }
        codeact = run_codeact_action(ws_id, action, confirm=True)
        iteration["codeact_run_id"] = codeact.get("run_id")
        iteration["stdout_preview"] = (codeact.get("stdout") or "")[:500]
        iteration["stderr_preview"] = (codeact.get("stderr") or "")[:500]
        if codeact.get("status") == "succeeded":
            iteration["status"] = "completed"
            _save_iteration(run, iteration)
            continue
        iteration["status"] = "failed"
        iteration["error"] = codeact.get("error") or codeact.get("reason") or codeact.get("status")
        _save_iteration(run, iteration)
        failed = True
        break

    if mode == "dry-run":
        run["status"] = "dry_run"
    elif failed:
        run["status"] = "failed"
    elif len(run.get("iterations", [])) == len(plan["steps"]):
        run["status"] = "completed"
    else:
        run["status"] = "partial"
    _save_run(run)
    return {"ok": run["status"] in {"dry_run", "completed"}, "run": run}


def list_agent_loop_runs(workspace_id: str, limit: int = 20) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}

    runs_dir = _loop_runs_dir(ws["id"])
    if not runs_dir.is_dir():
        return {"ok": True, "runs": []}

    runs = []
    for d in sorted(runs_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if not d.is_dir():
            continue
        run_json = d / "run.json"
        if run_json.is_file():
            try:
                runs.append(json.loads(run_json.read_text(encoding="utf-8")))
            except Exception:
                pass
        if len(runs) >= limit:
            break
    return {"ok": True, "runs": runs}


def read_agent_loop_run(workspace_id: str, run_id: str) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}

    run_json = _safe_run_json_path(ws["id"], run_id)
    if run_json is None:
        return {"ok": False, "error": "invalid_run_id"}
    if not run_json.is_file():
        return {"ok": False, "error": "run_not_found"}

    try:
        run = json.loads(run_json.read_text(encoding="utf-8"))
        iterations = []
        iter_dir = run_json.parent / "iterations"
        if iter_dir.is_dir():
            for f in sorted(iter_dir.glob("iter-*.json")):
                iterations.append(json.loads(f.read_text(encoding="utf-8")))
        return {"ok": True, "run": run, "iterations": iterations}
    except Exception as e:
        return {"ok": False, "error": str(e)}
