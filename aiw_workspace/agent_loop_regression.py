import argparse
import datetime
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from .agent_iterative_loop import read_agent_loop_run
from .capability_policy import POLICY_PROFILE, evaluate_capability_policy
from .path_hygiene import safe_display_path
from .profiles import AIW_ROOT, resolve_workspace


STDIO_PREVIEW_CHARS = 1800
DEFAULT_COCKPIT_PORT = 18766

ISOLATION_BOUNDARY = {
    "profile": "offline_regression_smoke_v1",
    "llm_real_used": False,
    "external_write_used": False,
    "daemon_used": False,
    "network_used": False,
    "github_jira_write_used": False,
    "docker_used": False,
    "background_process_used": False,
    "subprocess_shell": False,
    "allowed_external_io": "localhost-only Cockpit GET when --with-cockpit is set",
    "notes": [
        "Foreground CLI smoke only.",
        "No LLM provider calls.",
        "No GitHub/Jira writes.",
        "No curl/wget/browser automation.",
        "CodeAct execution remains a best-effort host sandbox, not strong isolation.",
    ],
}


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def _truncate(text: str | None) -> str:
    if not text:
        return ""
    if len(text) <= STDIO_PREVIEW_CHARS:
        return text
    return text[:STDIO_PREVIEW_CHARS] + "\n[truncated]"


def _regression_runs_dir(workspace_id: str) -> Path:
    ws = resolve_workspace(workspace_id)
    ws_id = ws["id"] if ws else workspace_id
    return AIW_ROOT / ".aiw" / "workspaces" / ws_id / "agent-loop-regression" / "runs"


def _run_command(args: list[str], timeout: int = 30, env: dict | None = None) -> dict:
    cmd_env = os.environ.copy()
    cmd_env["PYTHONPATH"] = f"{AIW_ROOT}:{cmd_env.get('PYTHONPATH', '')}"
    cmd_env.setdefault("AIW_COCKPIT_OPEN_BROWSER", "0")
    if env:
        cmd_env.update(env)

    started = _now_iso()
    try:
        proc = subprocess.run(
            args,
            cwd=AIW_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            env=cmd_env,
        )
        return {
            "command": args,
            "started_at": started,
            "returncode": proc.returncode,
            "_stdout": proc.stdout,
            "_stderr": proc.stderr,
            "stdout_preview": _truncate(proc.stdout),
            "stderr_preview": _truncate(proc.stderr),
            "timeout": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": args,
            "started_at": started,
            "returncode": None,
            "stdout_preview": _truncate(exc.stdout if isinstance(exc.stdout, str) else ""),
            "stderr_preview": _truncate(exc.stderr if isinstance(exc.stderr, str) else ""),
            "timeout": True,
            "error": "timeout",
        }


def _agent_loop_cmd(*args: str) -> list[str]:
    return ["./scripts/aiw-agent-loop", *args]


def _check(
    checks: list[dict],
    run_dir: Path,
    name: str,
    passed: bool,
    expected: str,
    observed,
    command: list[str] | None = None,
    error: str | None = None,
) -> dict:
    check = {
        "name": name,
        "status": "passed" if passed else "failed",
        "command": command,
        "expected": expected,
        "observed": _strip_private_fields(observed),
        "error": error,
    }
    checks.append(check)
    checks_dir = run_dir / "checks"
    checks_dir.mkdir(parents=True, exist_ok=True)
    path = checks_dir / f"{len(checks):02d}-{name}.json"
    path.write_text(json.dumps(check, indent=2, ensure_ascii=False), encoding="utf-8")
    return check


def _parse_stdout_json(result: dict) -> tuple[dict | None, str | None]:
    try:
        return json.loads(result.get("_stdout") or result.get("stdout_preview") or "{}"), None
    except Exception as exc:
        return None, str(exc)


def _strip_private_fields(value):
    if isinstance(value, dict):
        return {key: _strip_private_fields(item) for key, item in value.items() if not str(key).startswith("_")}
    if isinstance(value, list):
        return [_strip_private_fields(item) for item in value]
    return value


def _contains_home_path(value) -> bool:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return "/home/joao/" in text or "\\\\wsl.localhost" in text


def _has_any_codeact_run_id(run: dict) -> bool:
    return any(item.get("codeact_run_id") for item in run.get("iterations", []))


def _has_no_codeact_run_id(run: dict) -> bool:
    return all(not item.get("codeact_run_id") for item in run.get("iterations", []))


def _run_agent_loop_cases(workspace_id: str, checks: list[dict], run_dir: Path) -> list[str]:
    generated_run_ids = []

    help_result = _run_command(_agent_loop_cmd("--help"), timeout=15)
    _check(
        checks,
        run_dir,
        "agent_loop_help",
        help_result["returncode"] == 0 and "--operation" in help_result["stdout_preview"],
        "CLI help exits 0 and documents --operation.",
        help_result,
        command=help_result["command"],
    )

    dry_args = _agent_loop_cmd(
        "--workspace",
        workspace_id,
        "--task",
        "AIW regression smoke dry-run",
        "--once",
        "--dry-run",
        "--max-iterations",
        "3",
    )
    dry_result = _run_command(dry_args, timeout=30)
    dry_json, dry_error = _parse_stdout_json(dry_result)
    dry_run = (dry_json or {}).get("run", {})
    if dry_run.get("run_id"):
        generated_run_ids.append(dry_run["run_id"])
    _check(
        checks,
        run_dir,
        "dry_run_max_iterations_3",
        dry_result["returncode"] == 0
        and (dry_json or {}).get("ok") is True
        and dry_run.get("status") == "dry_run"
        and len(dry_run.get("iterations", [])) == 3,
        "Dry-run with max iterations 3 succeeds and records three iterations.",
        dry_json or dry_result,
        command=dry_args,
        error=dry_error,
    )
    _check(
        checks,
        run_dir,
        "dry_run_has_no_codeact_run_id",
        bool(dry_run) and _has_no_codeact_run_id(dry_run),
        "Dry-run never executes CodeAct and has no codeact_run_id.",
        dry_run.get("iterations", []),
        command=dry_args,
    )

    no_confirm_args = _agent_loop_cmd(
        "--workspace",
        workspace_id,
        "--task",
        "AIW regression smoke execute without confirmation",
        "--once",
        "--execute",
        "--max-iterations",
        "3",
    )
    no_confirm_result = _run_command(no_confirm_args, timeout=30)
    no_confirm_json, no_confirm_error = _parse_stdout_json(no_confirm_result)
    no_confirm_run = (no_confirm_json or {}).get("run", {})
    if no_confirm_run.get("run_id"):
        generated_run_ids.append(no_confirm_run["run_id"])
    _check(
        checks,
        run_dir,
        "execute_without_confirmation_blocks",
        no_confirm_result["returncode"] != 0
        and (no_confirm_json or {}).get("error") == "confirmation_required"
        and no_confirm_run.get("status") == "blocked",
        "Execute without --confirm-agent-loop blocks with confirmation_required.",
        no_confirm_json or no_confirm_result,
        command=no_confirm_args,
        error=no_confirm_error,
    )

    confirmed_args = _agent_loop_cmd(
        "--workspace",
        workspace_id,
        "--task",
        "AIW regression smoke confirmed execute",
        "--once",
        "--execute",
        "--confirm-agent-loop",
        "--max-iterations",
        "3",
    )
    confirmed_result = _run_command(confirmed_args, timeout=30)
    confirmed_json, confirmed_error = _parse_stdout_json(confirmed_result)
    confirmed_run = (confirmed_json or {}).get("run", {})
    if confirmed_run.get("run_id"):
        generated_run_ids.append(confirmed_run["run_id"])
    _check(
        checks,
        run_dir,
        "execute_confirmed_generates_codeact_run_id",
        confirmed_result["returncode"] == 0
        and (confirmed_json or {}).get("ok") is True
        and confirmed_run.get("status") == "completed"
        and _has_any_codeact_run_id(confirmed_run),
        "Confirmed offline execute completes and records a codeact_run_id.",
        confirmed_json or confirmed_result,
        command=confirmed_args,
        error=confirmed_error,
    )

    max_args = _agent_loop_cmd(
        "--workspace",
        workspace_id,
        "--task",
        "AIW regression smoke max guard",
        "--once",
        "--dry-run",
        "--max-iterations",
        "99",
    )
    max_result = _run_command(max_args, timeout=20)
    max_json, max_error = _parse_stdout_json(max_result)
    _check(
        checks,
        run_dir,
        "max_iterations_99_blocks",
        max_result["returncode"] != 0
        and (max_json or {}).get("error") == "max_iterations_must_be_between_1_and_3",
        "max_iterations above 3 blocks.",
        max_json or max_result,
        command=max_args,
        error=max_error,
    )

    missing_args = _agent_loop_cmd(
        "--workspace",
        workspace_id,
        "--task",
        "AIW regression smoke missing capability",
        "--once",
        "--dry-run",
        "--capability",
        "missing_capability_for_regression",
    )
    missing_result = _run_command(missing_args, timeout=20)
    missing_json, missing_error = _parse_stdout_json(missing_result)
    missing_run = (missing_json or {}).get("run", {})
    if missing_run.get("run_id"):
        generated_run_ids.append(missing_run["run_id"])
    _check(
        checks,
        run_dir,
        "missing_capability_blocks",
        missing_result["returncode"] != 0 and (missing_json or {}).get("error") == "capability_missing",
        "Missing capability blocks with capability_missing.",
        missing_json or missing_result,
        command=missing_args,
        error=missing_error,
    )

    unknown_op_args = _agent_loop_cmd(
        "--workspace",
        workspace_id,
        "--task",
        "AIW regression smoke unknown operation",
        "--once",
        "--dry-run",
        "--operation",
        "unknown_operation_for_regression",
    )
    unknown_op_result = _run_command(unknown_op_args, timeout=20)
    unknown_op_json, unknown_op_error = _parse_stdout_json(unknown_op_result)
    unknown_op_run = (unknown_op_json or {}).get("run", {})
    if unknown_op_run.get("run_id"):
        generated_run_ids.append(unknown_op_run["run_id"])
    _check(
        checks,
        run_dir,
        "unknown_operation_blocks",
        unknown_op_result["returncode"] != 0 and (unknown_op_json or {}).get("error") == "unknown_operation",
        "Unknown operation blocks with unknown_operation.",
        unknown_op_json or unknown_op_result,
        command=unknown_op_args,
        error=unknown_op_error,
    )

    return generated_run_ids


def _run_policy_checks(workspace_id: str, checks: list[dict], run_dir: Path) -> None:
    scenarios = [
        (
            "policy_dry_run_simulation_allowed",
            dict(mode="dry-run", confirmed=False, fixed_code=True),
            True,
            "dry_run_simulation",
            {"simulation_only": True, "capability_not_executed": True},
        ),
        (
            "policy_offline_without_confirmation_blocks",
            dict(mode="offline", confirmed=False, fixed_code=True),
            False,
            "confirmation_required",
            {},
        ),
        (
            "policy_offline_confirmed_allowed",
            dict(mode="offline", confirmed=True, fixed_code=True),
            True,
            "offline_confirmed_fixed_codeact_eval",
            {"capability_not_executed": False},
        ),
        (
            "policy_llm_mode_blocks",
            dict(mode="llm", confirmed=True, fixed_code=True),
            False,
            "llm_mode_blocked",
            {},
        ),
        (
            "policy_unknown_operation_blocks",
            dict(mode="offline", operation="unknown_operation_for_regression", confirmed=True, fixed_code=True),
            False,
            "unknown_operation",
            {},
        ),
    ]

    for name, kwargs, expected_allowed, expected_reason, extra in scenarios:
        decision = evaluate_capability_policy(
            workspace_id=workspace_id,
            capability_name="codeact_sandbox",
            operation=kwargs.pop("operation", "python_eval_fixed"),
            local_execution=True,
            tracked=True,
            **kwargs,
        )
        passed = (
            decision.get("allowed") is expected_allowed
            and decision.get("reason") == expected_reason
            and decision.get("policy_profile") == POLICY_PROFILE
        )
        for key, expected_value in extra.items():
            passed = passed and decision.get(key) is expected_value
        _check(
            checks,
            run_dir,
            name,
            passed,
            f"Policy returns allowed={expected_allowed}, reason={expected_reason}.",
            decision,
        )


def _run_path_hygiene_checks(workspace_id: str, generated_run_ids: list[str], checks: list[dict], run_dir: Path) -> None:
    observations = []
    leaked = False
    missing_relative_artifact = False
    for run_id in generated_run_ids:
        endpoint_like = read_agent_loop_run(workspace_id, run_id)
        observations.append({"run_id": run_id, "endpoint_like": endpoint_like})
        if _contains_home_path(endpoint_like):
            leaked = True

        run_json = AIW_ROOT / ".aiw" / "workspaces" / workspace_id / "agent-iterative-loop" / "runs" / run_id / "run.json"
        if run_json.is_file():
            stored = json.loads(run_json.read_text(encoding="utf-8"))
            observations[-1]["stored_run_dir"] = stored.get("run_dir")
            if _contains_home_path(stored):
                leaked = True
            if not str(stored.get("run_dir", "")).startswith(".aiw/workspaces/"):
                missing_relative_artifact = True

    _check(
        checks,
        run_dir,
        "path_hygiene_run_json_and_read_output",
        bool(generated_run_ids) and not leaked and not missing_relative_artifact,
        "New run artifacts and endpoint-like output avoid /home/joao paths and use relative artifact paths.",
        observations,
    )

    traversal_cases = ["../x", "/tmp/x", "ail-12345678/../../x", "..%2Fx", "%2Ftmp%2Fx", ""]
    traversal_observed = []
    traversal_passed = True
    for bad_run_id in traversal_cases:
        res = read_agent_loop_run(workspace_id, bad_run_id)
        traversal_observed.append({"run_id": bad_run_id, "result": res})
        if res.get("ok") is not False or res.get("error") != "invalid_run_id":
            traversal_passed = False
    _check(
        checks,
        run_dir,
        "path_traversal_read_run_blocks",
        traversal_passed,
        "Traversal-like run IDs are rejected before path resolution.",
        traversal_observed,
    )


def _run_cockpit_check(workspace_id: str, checks: list[dict], run_dir: Path, port: int) -> None:
    env = {
        "AIW_COCKPIT_OPEN_BROWSER": "0",
        "AIW_COCKPIT_PORT": str(port),
        "AIW_COCKPIT_HOST": "127.0.0.1",
        "AIW_LLM_ENABLED": "1",
        "AIW_MODEL": "dev-coder",
        "PYTHONPATH": f"{AIW_ROOT}:{os.environ.get('PYTHONPATH', '')}",
    }
    proc = subprocess.Popen(
        ["./scripts/aiw-cockpit"],
        cwd=AIW_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=False,
        env={**os.environ.copy(), **env},
    )
    observed = {"port": port, "pid": proc.pid}
    try:
        base = f"http://127.0.0.1:{port}"
        html_text = ""
        list_text = ""
        detail_text = ""
        for _ in range(12):
            if proc.poll() is not None:
                break
            try:
                with urllib.request.urlopen(
                    base + f"/api/workspaces/{workspace_id}/agent-iterative-loop/runs",
                    timeout=8,
                ) as response:
                    list_text = response.read().decode("utf-8", errors="replace")
                list_json = json.loads(list_text)
                runs = list_json.get("runs", [])
                if runs:
                    run_id = runs[0].get("run_id")
                    with urllib.request.urlopen(
                        base + f"/api/workspaces/{workspace_id}/agent-iterative-loop/runs/{run_id}",
                        timeout=8,
                    ) as response:
                        detail_text = response.read().decode("utf-8", errors="replace")
                try:
                    with urllib.request.urlopen(base + "/", timeout=2) as response:
                        html_text = response.read().decode("utf-8", errors="replace")
                except (OSError, urllib.error.URLError):
                    html_text = ""
                break
            except (OSError, urllib.error.URLError, json.JSONDecodeError):
                time.sleep(1)
        stdout_preview = ""
        stderr_preview = ""
        if proc.poll() is not None:
            stdout, stderr = proc.communicate(timeout=1)
            stdout_preview = _truncate(stdout)
            stderr_preview = _truncate(stderr)
        observed.update({
            "html_preview": _truncate(html_text),
            "list_preview": _truncate(list_text),
            "detail_preview": _truncate(detail_text),
            "returncode": proc.poll(),
            "stdout_preview": stdout_preview,
            "stderr_preview": stderr_preview,
        })
        html_lower = html_text.lower()
        has_agent_execute_form = (
            "confirm-agent-loop" in html_lower
            or "agent-loop-execute" in html_lower
            or 'action="/api/workspaces/' in html_lower and "/agent-iterative-loop/execute" in html_lower
        )
        passed = (
            list_text
            and detail_text
            and not has_agent_execute_form
            and '"ok": true' in list_text
            and '"ok": true' in detail_text
        )
        _check(
            checks,
            run_dir,
            "cockpit_read_only_gets",
            bool(passed),
            "Cockpit starts in controlled foreground, exposes read-only list/detail GETs, and does not render an execute form when HTML responds.",
            observed,
            command=["./scripts/aiw-cockpit"],
        )
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)


def _render_summary(run: dict, checks: list[dict]) -> str:
    lines = [
        f"# Agent Loop Regression Smoke: {run['run_id']}",
        "",
        f"- Workspace: {run['workspace_id']}",
        f"- Status: {run['status']}",
        f"- Created: {run['created_at']}",
        f"- Checks: {run['checks_passed']}/{run['checks_total']} passed",
        f"- Cockpit check: {'enabled' if run.get('with_cockpit') else 'skipped'}",
        f"- Run dir: {run['run_dir']}",
        "",
        "## Isolation Boundary",
        "",
        "- LLM real used: false",
        "- External write used: false",
        "- Daemon used: false",
        "- subprocess shell: false",
        "- Network: none by default; localhost-only GETs when --with-cockpit is set.",
        "",
        "## Checks",
        "",
    ]
    for item in checks:
        lines.append(f"- {item['status']}: {item['name']}")
    return "\n".join(lines) + "\n"


def run_regression_smoke(workspace_id: str, with_cockpit: bool = False, cockpit_port: int = DEFAULT_COCKPIT_PORT) -> dict:
    ws = resolve_workspace(workspace_id)
    if not ws:
        return {"ok": False, "error": "workspace_not_found"}
    ws_id = ws["id"]

    run_id = f"alr-{uuid.uuid4().hex[:8]}"
    run_dir = _regression_runs_dir(ws_id) / run_id
    (run_dir / "checks").mkdir(parents=True, exist_ok=True)

    checks: list[dict] = []
    generated_run_ids = _run_agent_loop_cases(ws_id, checks, run_dir)
    _run_policy_checks(ws_id, checks, run_dir)
    _run_path_hygiene_checks(ws_id, generated_run_ids, checks, run_dir)
    if with_cockpit:
        _run_cockpit_check(ws_id, checks, run_dir, cockpit_port)

    checks_total = len(checks)
    checks_failed = len([item for item in checks if item["status"] == "failed"])
    checks_passed = checks_total - checks_failed
    run = {
        "run_id": run_id,
        "workspace_id": ws_id,
        "created_at": _now_iso(),
        "status": "passed" if checks_failed == 0 else "failed",
        "checks_total": checks_total,
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "llm_real_used": False,
        "external_write_used": False,
        "daemon_used": False,
        "generated_agent_loop_runs": generated_run_ids,
        "with_cockpit": bool(with_cockpit),
        "isolation_boundary": ISOLATION_BOUNDARY,
        "run_dir": safe_display_path(run_dir),
        "checks_dir": safe_display_path(run_dir / "checks"),
        "summary_md": safe_display_path(run_dir / "summary.md"),
    }
    (run_dir / "run.json").write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "summary.md").write_text(_render_summary(run, checks), encoding="utf-8")
    return {"ok": checks_failed == 0, "run": run, "checks": checks}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AIW Agent Loop offline regression smoke")
    parser.add_argument("--workspace", required=True, help="Workspace ID")
    cockpit = parser.add_mutually_exclusive_group()
    cockpit.add_argument("--with-cockpit", action="store_true", help="Run optional Cockpit read-only localhost GET check")
    cockpit.add_argument("--skip-cockpit", action="store_true", help="Skip Cockpit check; default")
    parser.add_argument("--cockpit-port", type=int, default=DEFAULT_COCKPIT_PORT, help="Localhost port for --with-cockpit")
    args = parser.parse_args(argv)

    result = run_regression_smoke(
        workspace_id=args.workspace,
        with_cockpit=bool(args.with_cockpit and not args.skip_cockpit),
        cockpit_port=args.cockpit_port,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
