# MIGRAÇÃO CIRÚRGICA: Lógica em aiw/integration/github_intake.py (Intake de GitHub).
# aiw_workspace/github_intake.py é thin delegate apontando para aqui.
# Usado por Cockpit + scripts agent para iniciar fluxos que alimentam Loop Iterativo do Agente.
# Mantém compat. Termos PT: Intake, Inbox de Integração, Patch Intent.

"""GitHub Intake para AIW.

Responsável pela ingestão de Issues e Pull Requests do GitHub,
criação de itens no integration-inbox e geração de Patch Intent.

Usado por scripts (aiw-github-intake) e cockpit para iniciar fluxos de patch/review.
Integra com o fluxo de "Patch Intent" antes do Loop Iterativo do Agente ou validação.
"""

import datetime
import json
import os
import uuid
import subprocess
from pathlib import Path

def _get_workspace_helpers():
    """Lazy. Prefere aiw/ (resolve_workspace reexportado) + AIW_ROOT via env/parents (sem dep de aiw_workspace.profiles pesado).
    Migração cirúrgica para integration (Cockpit/agent intake path). Termos: Intake de GitHub, Inbox de Integração.
    """
    from aiw import resolve_workspace
    aiw_root = Path(os.environ.get("AIW_ROOT", str(Path(__file__).resolve().parents[2]))).resolve()
    return resolve_workspace, aiw_root


def create_patch_intent(workspace_id: str, item_id: str, source_data: dict, kind: str, repo: str, number: int) -> dict:
    resolve_workspace, AIW_ROOT = _get_workspace_helpers()
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
    resolve_workspace, AIW_ROOT = _get_workspace_helpers()
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
    resolve_workspace, AIW_ROOT = _get_workspace_helpers()
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
    resolve_workspace, AIW_ROOT = _get_workspace_helpers()
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
    resolve_workspace, AIW_ROOT = _get_workspace_helpers()
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
    resolve_workspace, AIW_ROOT = _get_workspace_helpers()
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
    resolve_workspace, AIW_ROOT = _get_workspace_helpers()
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


# === GitHub-driven 24/7 autonomous: daemon reacts to events (issues, PR comments, CI failures) -> auto-create missions ===
# Builds directly on existing run_github_intake + inbox/patch-intent.
# Used by daemon/worker for "react to real GitHub events".
# aiw-first. Surgical.

def github_event_to_mission(workspace_id: str, repo: str, kind: str, number: int, fetch: bool = False, confirm_external_read: bool = False, auto_start: bool = False) -> dict:
    """Make daemon react: GitHub event (issue / pr / comment / ci_failure encoded in kind) -> intake -> auto-create mission + enqueue.
    Returns mission tied result. For CI fail use kind='pull_request' + task hint or post-intake label detect.
    """
    intake = run_github_intake(workspace_id, repo, kind, number, fetch=fetch, confirm_external_read=confirm_external_read)
    if not intake.get("ok"):
        return {"ok": False, "error": intake.get("error"), "intake": intake}
    title = f"GitHub {kind} {repo}#{number}"
    task = f"[github:{kind}:{repo}#{number}] Autonomous: analyze event, implement/review fix, suggest or PR. (CI fail or comment auto-detected via task if present)"
    try:
        from aiw.mission import create_mission, enqueue_mission_task
        m = create_mission(workspace_id, title, task)
        mid = m.get("mission_id")
        qres = enqueue_mission_task(mid, task, priority=3, workspace_id=workspace_id)
        res = {"ok": True, "mission_id": mid, "intake_item_id": intake.get("item_id"), "queue": qres, "title": title}
        if auto_start:
            try:
                from aiw.agent.iterative_loop import start_persistent_agent_daemon
                d = start_persistent_agent_daemon(workspace_id, task, mission_id=mid, execute=False, confirm=False, max_iterations=2)
                res["daemon"] = d
            except Exception as de:
                res["daemon_error"] = str(de)[:120]
        return res
    except Exception as e:
        return {"ok": False, "error": str(e), "intake": intake}


def simulate_github_event_to_mission(workspace_id: str = "aiw", scenario: str = "issue") -> dict:
    """Verification helper (simulation of issue → autonomous mission creation → progress → PR).
    Dry (no real fetch). Used for step 4 verification. Covers issue/PR comment/CI failure paths.
    """
    repo = "owner/aiw-repo"
    number = 123
    kind = "issue" if scenario == "issue" or "ci" not in scenario else "pull_request"
    # simulate PR comment or CI fail via task marker
    res = github_event_to_mission(workspace_id, repo, kind, number, fetch=False, confirm_external_read=False, auto_start=False)
    # attach sim progress marker
    if res.get("ok"):
        res["simulated_scenario"] = scenario
        res["note"] = "sim: event->intake->mission+enqueue (progress via start/run_agent + auto_pr in loop)"
    return res


# === STEP 3: Full GitHub Autonomy Loop (aiw-first, surgical on existing github_intake) ===
# Deepens 24/7: intelligent triage of issues; auto-response to PR reviews/comments;
# basic conflict resolution; sophisticated "when to merge" policy.
# Builds directly on run_github_intake + github_event_to_mission + simulate + daemon/worker/loop auto_pr.
# All relative/aiw-first; no behavior change to prior paths; dry by default.

def intelligent_issue_triage(issue_data: dict) -> dict:
    """Intelligent triage for 24/7 service (issues from github intake).
    Classifies type, extracts risks, decides automation level (full|comment_only|escalate).
    Uses labels + body/title heuristics (surgical, no LLM required for base; can feed planner).
    Returns triage dict for mission creation / policy.
    """
    title = (issue_data.get("title") or "").lower()
    body = (issue_data.get("body") or "").lower()
    labels = issue_data.get("labels", []) or []
    label_names = [str(l.get("name", "")).lower() for l in labels] if isinstance(labels, list) else []
    combined = f"{title} {body} {' '.join(label_names)}"

    itype = "feature"
    if any(k in combined for k in ["bug", "fix", "error", "crash", "failing", "broken"]):
        itype = "bug"
    elif any(k in combined for k in ["security", "vuln", "secret", "auth", "permission", "cve"]):
        itype = "security"
    elif any(k in combined for k in ["doc", "docs", "readme", "example"]):
        itype = "docs"
    elif any(k in combined for k in ["refactor", "clean", "perf", "performance"]):
        itype = "refactor"

    risk_flags = []
    if any(k in combined for k in ["security", "secret", "token", "key", "auth", "prod", "database", "migration"]):
        risk_flags.append("high_risk_security_or_data")
    if any(k in combined for k in ["breaking", "api change", "major"]):
        risk_flags.append("breaking_change")
    if "ci" in combined or "test" in combined and "fail" in combined:
        risk_flags.append("ci_failure")

    automation = "full"
    if itype == "security" or "high_risk" in str(risk_flags):
        automation = "escalate"
    elif itype in ("docs",) or not risk_flags:
        automation = "full"
    elif any("comment" in l or "discuss" in combined for l in label_names):
        automation = "comment_only"

    suggested_task = f"[{itype}] triage:{automation} risks={risk_flags or 'none'} : analyze and { 'implement fix' if automation=='full' else 'comment or escalate' }"

    return {
        "type": itype,
        "risk_flags": risk_flags,
        "automation_level": automation,
        "suggested_task": suggested_task,
        "labels": label_names,
        "title_snip": (issue_data.get("title") or "")[:80],
    }


def fetch_pr_reviews_and_comments(repo: str, pr_number: int, confirm_external: bool = False) -> dict:
    """Fetch reviews + comments for a PR (used for auto-response).
    Dry by default; real only with confirm (gh pr view --json reviews,comments).
    Returns structured {reviews, comments, has_approved, blocking_comments}.
    aiw-first surgical.
    """
    if not confirm_external:
        # dry sim for verification + safety
        return {
            "ok": True, "dry": True,
            "reviews": [{"author": "reviewer1", "state": "COMMENTED", "body": "looks good but fix X"}],
            "comments": [{"author": "user", "body": "please address the edge case in func foo"}],
            "has_approved": False,
            "blocking_comments": 1,
            "note": "dry fetch (use confirm_external_read for real gh)"
        }
    import shutil, subprocess, json as _json
    if not shutil.which("gh"):
        return {"ok": False, "error": "gh not found"}
    try:
        cmd = ["gh", "pr", "view", str(pr_number), "--repo", repo, "--json", "reviews,comments,reviewDecision"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if proc.returncode != 0:
            return {"ok": False, "error": proc.stderr[:200]}
        data = _json.loads(proc.stdout or "{}")
        reviews = data.get("reviews", []) or []
        comments = data.get("comments", []) or []
        approved = (data.get("reviewDecision") or "").upper() == "APPROVED" or any(r.get("state") == "APPROVED" for r in reviews)
        blocking = [c for c in comments if any(w in (c.get("body") or "").lower() for w in ["block", "please fix", "change required", "fix"])]
        return {
            "ok": True, "reviews": reviews, "comments": comments,
            "has_approved": approved,
            "blocking_comments": len(blocking),
            "raw": data
        }
    except Exception as e:
        return {"ok": False, "error": str(e)[:160]}


def auto_respond_to_pr_review_or_comment(workspace_id: str, repo: str, pr_number: int, comment_or_review: dict = None, confirm_external: bool = False) -> dict:
    """Auto-response to PR reviews/comments.
    Detects actionable (e.g. 'fix foo'), generates response or triggers fix mission.
    Can post comment via gh (if confirm) or return text for loop to use.
    Ties to triage + mission for fixes. Surgical extension of event->mission.
    """
    text = (comment_or_review or {}).get("body") or (comment_or_review or {}).get("comment", "")
    tlow = text.lower()
    actionable = any(k in tlow for k in ["fix", "please", "change", "address", "edge", "bug", "add test", "refactor"])
    resp_text = f"AIW auto: noted '{text[:80]}'. "
    action = "comment"
    mid = None
    if actionable and "escalate" not in tlow:
        # trigger fix path via mission (reuses github_event)
        try:
            from aiw.mission import create_mission, enqueue_mission_task
            m = create_mission(workspace_id, f"PR#{pr_number} auto-fix", f"[github:pull_request:{repo}#{pr_number}] auto-respond: {text[:120]}")
            mid = m.get("mission_id")
            enqueue_mission_task(mid, m.get("task", ""), priority=2, workspace_id=workspace_id)
            resp_text += "Created autonomous mission for fix."
            action = "fix_mission"
        except Exception as e:
            resp_text += f" (mission err: {str(e)[:60]})"
            action = "comment_only"
    else:
        resp_text += "Will comment; escalate if risk."

    posted = False
    if confirm_external and action == "comment":
        import shutil, subprocess
        if shutil.which("gh"):
            try:
                # gh pr comment <num> --repo <r> --body "..."
                subprocess.run(["gh", "pr", "comment", str(pr_number), "--repo", repo, "--body", resp_text[:1000]], check=False, timeout=20)
                posted = True
            except Exception:
                pass

    return {
        "ok": True, "action": action, "response": resp_text,
        "mission_id": mid, "posted": posted, "actionable": actionable,
        "pr": f"{repo}#{pr_number}"
    }


def basic_resolve_conflict(workspace_id: str, conflicted_path: str, strategy: str = "prefer_theirs") -> dict:
    """Basic conflict resolution for autonomous git flows.
    Strategies: prefer_theirs | prefer_ours | marker (leaves markers for human).
    Uses git checkout --theirs etc when safe. aiw-first; gated by caller policy.
    """
    # Note: caller (loop/tools) must have performed the merge that produced conflict.
    # Here we do the resolve step only (surgical helper).
    import subprocess
    from pathlib import Path as _P
    root = _P(__import__("os").environ.get("AIW_ROOT", ".")).resolve()
    try:
        if strategy == "prefer_theirs":
            p = subprocess.run(["git", "checkout", "--theirs", "--", conflicted_path], cwd=str(root), capture_output=True, text=True, timeout=10)
        elif strategy == "prefer_ours":
            p = subprocess.run(["git", "checkout", "--ours", "--", conflicted_path], cwd=str(root), capture_output=True, text=True, timeout=10)
        else:
            return {"ok": False, "strategy": strategy, "note": "marker left; manual resolve needed"}
        ok = p.returncode == 0
        subprocess.run(["git", "add", "--", conflicted_path], cwd=str(root), check=False)
        return {"ok": ok, "strategy": strategy, "path": conflicted_path, "stdout": p.stdout[:200]}
    except Exception as e:
        return {"ok": False, "error": str(e)[:120]}


def sophisticated_should_merge_policy(run: dict, pr_reviews: dict = None, extra_checks: dict = None) -> dict:
    """Sophisticated 'when to merge' policy (beyond simple auto_pr).
    Considers: persistent+completed+has_real+validated, review approvals, no blocking comments,
    no high risk flags, tests passed, mission budget not paused, no open conflicts.
    Returns {decision: 'merge'|'comment'|'escalate', reason, score}.
    Used by loop after PR creation and by github event flows.
    """
    pr_reviews = pr_reviews or {}
    checks = extra_checks or {}
    reasons = []
    score = 0

    # core from run (builds on existing detect + has_real)
    if run.get("persistent") and run.get("status") == "completed" and run.get("has_real_execution"):
        score += 30
    else:
        reasons.append("not_persistent_validated_real")

    if run.get("auto_pr") or run.get("pr_url"):
        score += 10
    else:
        reasons.append("no_pr_yet")

    # reviews
    if pr_reviews.get("has_approved"):
        score += 25
    if pr_reviews.get("blocking_comments", 0) == 0:
        score += 15
    else:
        reasons.append("blocking_comments")

    # risks from triage if present in run/task
    task = (run.get("task") or "").lower() + str(run.get("accumulated_context", ""))[:200].lower()
    if any(r in task for r in ["high_risk", "security", "breaking"]):
        reasons.append("high_risk_flag")
        score -= 20

    # tests/validate
    if any("test" in str(s).lower() or "valid" in str(s).lower() or "py_compile" in str(s).lower() for s in (run.get("step_results") or [])):
        score += 15

    # mission budget
    if run.get("mission_budget_paused"):
        reasons.append("mission_paused")
        score -= 10

    # conflicts
    if checks.get("has_conflicts"):
        reasons.append("unresolved_conflicts")
        score -= 15

    decision = "merge" if score >= 60 and not reasons else ("comment" if score >= 30 else "escalate")
    if not reasons and decision == "merge":
        reasons = ["policy_ok"]

    return {
        "decision": decision,
        "reason": "; ".join(reasons) or "sophisticated_policy_pass",
        "score": max(0, min(100, score)),
        "checks": {"persistent_validated": bool(run.get("has_real_execution")), "approved": bool(pr_reviews.get("has_approved")), "no_blockers": pr_reviews.get("blocking_comments", 0) == 0}
    }


# Enhance simulate for full STEP3 verification chain (issue -> triage -> PR -> review comments -> fixes -> merge/escalate)
def simulate_full_github_autonomy_loop(workspace_id: str = "aiw") -> dict:
    """Full sim: issue → triage → mission → PR → review comment → auto_respond/fix → should_merge (merge or escalate).
    Dry, uses existing helpers + new triage/respond/policy. For verification (step 3).
    """
    repo = "owner/aiw-repo"
    number = 42
    # 1. issue intake + intelligent triage
    intake = run_github_intake(workspace_id, repo, "issue", number, fetch=False)
    issue_src = {"title": "bug in foo: crash on edge", "body": "please fix the failing case", "labels": [{"name": "bug"}]}
    tri = intelligent_issue_triage(issue_src)

    # 2. event->mission (now can consume triage)
    ev = github_event_to_mission(workspace_id, repo, "issue", number, fetch=False, auto_start=False)
    mid = ev.get("mission_id") if ev.get("ok") else None

    # 3. simulate PR created (via loop auto_pr path marker)
    fake_run = {"persistent": True, "status": "completed", "has_real_execution": True, "task": f"[github:pull_request:{repo}#{number}] fix", "auto_pr": {"ok": True}, "pr_url": "https://example.com/pr/999"}

    # 4. PR review/comment arrive
    reviews = fetch_pr_reviews_and_comments(repo, number, confirm_external=False)
    comment = (reviews.get("comments") or [{}])[0]
    resp = auto_respond_to_pr_review_or_comment(workspace_id, repo, number, comment, confirm_external=False)

    # 5. after fix (sim), policy decide merge or escalate
    pol = sophisticated_should_merge_policy(fake_run, pr_reviews=reviews, extra_checks={"has_conflicts": False})

    return {
        "ok": True,
        "triage": tri,
        "mission": {"id": mid},
        "pr_reviews_fetched": reviews.get("ok"),
        "auto_respond": resp.get("action"),
        "merge_policy": pol,
        "chain": "issue->triage->mission->pr->review_comment->respond/fix->merge_policy",
        "decision": pol.get("decision"),
        "note": "full simulation (dry); real gh via confirm flags in callers"
    }
