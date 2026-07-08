import os
import argparse
import json
import subprocess
import time
import shutil
import uuid
import difflib
from pathlib import Path
import re
import shlex
from .policy import validate_path, validate_write_path, validate_project_patch_path, validate_shell_command, get_root, get_aiw_root


def _workspace_id() -> str:
    value = os.environ.get("AIW_WORKSPACE_ID", "aiw").strip() or "aiw"
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in value)[:80] or "aiw"


def _patches_dir() -> Path:
    return get_aiw_root() / ".aiw" / "workspaces" / _workspace_id() / "patches"


def _legacy_patches_dir() -> Path:
    return get_aiw_root() / ".aiw" / "patches"


def _patch_file_for_read(patch_id: str) -> Path:
    scoped = _patches_dir() / f"{patch_id}.json"
    if scoped.exists():
        return scoped
    return _legacy_patches_dir() / f"{patch_id}.json"


def directory_list(path: str = ".", max_depth: int = 2, limit: int = 100):
    try:
        resolved_path = validate_path(path)
        if not resolved_path.is_dir():
            return {"ok": False, "tool": "directory_list", "error": "Not a directory"}

        ignored = {".git", ".venv", "node_modules", "vendor", "__pycache__"}

        entries = []
        start_depth = len(resolved_path.parts)

        for root, dirs, files in os.walk(resolved_path):
            current_depth = len(Path(root).parts) - start_depth
            if current_depth >= max_depth:
                dirs.clear() # don't go deeper
                continue

            # Filter ignored dirs
            dirs[:] = [d for d in dirs if d not in ignored]

            for d in dirs:
                if len(entries) >= limit:
                    break
                rel = str(Path(root) / d)
                rel = rel.replace(str(resolved_path), "").lstrip(os.sep)
                entries.append({"name": rel or d, "type": "dir"})

            if len(entries) >= limit:
                break

            for f in files:
                if len(entries) >= limit:
                    break
                rel = str(Path(root) / f)
                rel = rel.replace(str(resolved_path), "").lstrip(os.sep)
                entries.append({"name": rel or f, "type": "file"})

            if len(entries) >= limit:
                break

        return {"ok": True, "tool": "directory_list", "entries": entries[:limit]}
    except Exception as e:
        return {"ok": False, "tool": "directory_list", "error": str(e)}

def file_read(path: str, max_bytes: int = 8000):
    try:
        resolved_path = validate_path(path)
        if not resolved_path.is_file():
            return {"ok": False, "tool": "file_read", "error": "Not a file or does not exist"}

        stat = resolved_path.stat()
        truncated = stat.st_size > max_bytes

        with open(resolved_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_bytes)

        return {
            "ok": True,
            "tool": "file_read",
            "content": content,
            "truncated": truncated
        }
    except Exception as e:
        return {"ok": False, "tool": "file_read", "error": str(e)}

def shell_exec(command: str, timeout: int = 20):
    try:
        if timeout > 30:
            timeout = 30

        parts = validate_shell_command(command)

        result = subprocess.run(
            parts,
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(validate_path("."))
        )

        return {
            "ok": True,
            "tool": "shell_exec",
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired as e:
        return {"ok": False, "tool": "shell_exec", "error": "Timeout expired", "stdout": e.stdout.decode('utf-8', 'replace') if e.stdout else ""}
    except Exception as e:
        return {"ok": False, "tool": "shell_exec", "error": str(e)}

def _create_backup(resolved_path: Path) -> str:
    if not resolved_path.exists():
        return None
    root = get_root()
    rel = resolved_path.relative_to(root)
    timestamp = time.strftime("%Y%m%dT%H%M%SZ")
    backup_path = get_aiw_root() / ".aiw" / "backups" / _workspace_id() / timestamp / rel
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(resolved_path, backup_path)
    return str(backup_path.relative_to(get_aiw_root()))

def file_write(path: str, content: str, overwrite: bool = False):
    try:
        resolved_path = validate_write_path(path)

        exists = resolved_path.exists()
        if exists and not overwrite:
            return {"ok": False, "tool": "file_write", "error": "Arquivo já existe. Defina overwrite=true se desejar sobrescrever."}

        backup_path = _create_backup(resolved_path) if exists else None

        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_path.write_text(content, encoding="utf-8")

        return {
            "ok": True,
            "tool": "file_write",
            "path": str(resolved_path.relative_to(get_root())),
            "bytes_written": len(content.encode("utf-8")),
            "created": not exists,
            "overwritten": exists,
            "backup_path": backup_path
        }
    except Exception as e:
        return {"ok": False, "tool": "file_write", "error": str(e)}

def file_patch(path: str, old_text: str, new_text: str, expected_replacements: int = 1):
    try:
        resolved_path = validate_write_path(path)

        if not resolved_path.exists():
            return {"ok": False, "tool": "file_patch", "error": "Arquivo não existe."}

        content = resolved_path.read_text(encoding="utf-8")
        occurrences = content.count(old_text)

        if occurrences != expected_replacements:
            return {
                "ok": False,
                "tool": "file_patch",
                "error": f"Encontradas {occurrences} ocorrências de old_text, mas esperado {expected_replacements}. Substituição abortada."
            }

        backup_path = _create_backup(resolved_path)
        new_content = content.replace(old_text, new_text)
        resolved_path.write_text(new_content, encoding="utf-8")

        return {
            "ok": True,
            "tool": "file_patch",
            "path": str(resolved_path.relative_to(get_root())),
            "replacements": occurrences,
            "backup_path": backup_path,
            "bytes_written": len(new_content.encode("utf-8"))
        }
    except Exception as e:
        return {"ok": False, "tool": "file_patch", "error": str(e)}

def project_patch_preview(path: str, old_text: str, new_text: str, expected_replacements: int = 1, reason: str = ""):
    try:
        resolved_path = validate_project_patch_path(path)

        if not resolved_path.exists():
            return {"ok": False, "tool": "project_patch_preview", "error": "Arquivo não existe."}

        content = resolved_path.read_text(encoding="utf-8")
        occurrences = content.count(old_text)

        if occurrences != expected_replacements:
            return {
                "ok": False,
                "tool": "project_patch_preview",
                "error": f"Encontradas {occurrences} ocorrências de old_text, mas esperado {expected_replacements}. Substituição abortada."
            }

        new_content = content.replace(old_text, new_text)

        # Generate unified diff
        diff_lines = list(difflib.unified_diff(
            content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=path,
            tofile=path,
            n=3
        ))
        diff_text = "".join(diff_lines)

        # Parse diff lines
        added_lines = []
        removed_lines = []
        current_line = 0

        for dline in diff_lines:
            if dline.startswith("@@"):
                # Parse header @@ -old_start,old_count +new_start,new_count @@
                import re
                match = re.search(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", dline)
                if match:
                    current_line = int(match.group(2))
            elif dline.startswith("+") and not dline.startswith("+++"):
                added_lines.append(current_line)
                current_line += 1
            elif dline.startswith("-") and not dline.startswith("---"):
                removed_lines.append(current_line) # Contextually, this isn't strictly mapping to new file line numbers, but we just track it.
            elif not dline.startswith("\\") and not dline.startswith("---") and not dline.startswith("+++"):
                current_line += 1

        patch_id = time.strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:8]
        patches_dir = _patches_dir()
        patches_dir.mkdir(parents=True, exist_ok=True)

        patch_data = {
            "patch_id": patch_id,
            "path": str(resolved_path.relative_to(get_root())),
            "changed_files": [str(resolved_path.relative_to(get_root()))],
            "old_text": old_text,
            "new_text": new_text,
            "reason": reason,
            "diff": diff_text,
            "changed_lines": [
                {
                    "file": str(resolved_path.relative_to(get_root())),
                    "added_lines": added_lines,
                    "removed_lines": removed_lines
                }
            ],
            "replacements": occurrences,
            "status": "preview",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "workspace_id": _workspace_id(),
            "artifact_scope": "scoped",
            "suggested_tests": []
        }

        patch_file = patches_dir / f"{patch_id}.json"
        patch_file.write_text(json.dumps(patch_data, indent=2, ensure_ascii=False), encoding="utf-8")

        return {
            "ok": True,
            "tool": "project_patch_preview",
            "patch_id": patch_id,
            "path": patch_data["path"],
            "changed_files": patch_data["changed_files"],
            "replacements": occurrences,
            "diff": diff_text,
            "status": "preview"
        }
    except Exception as e:
        return {"ok": False, "tool": "project_patch_preview", "error": str(e)}

def project_patch_apply(patch_id: str):
    try:
        if _workspace_id() != "aiw":
            return {"ok": False, "tool": "project_patch_apply", "error": "Auto-apply bloqueado para workspace externo."}
        patch_file = _patch_file_for_read(patch_id)
        if not patch_file.exists():
            return {"ok": False, "tool": "project_patch_apply", "error": "Patch não encontrado."}

        patch_data = json.loads(patch_file.read_text(encoding="utf-8"))
        if patch_data.get("status") != "preview":
            return {"ok": False, "tool": "project_patch_apply", "error": f"Patch status inválido: {patch_data.get('status')}"}

        path_str = patch_data["path"]
        resolved_path = validate_project_patch_path(path_str)

        content = resolved_path.read_text(encoding="utf-8")
        old_text = patch_data["old_text"]
        new_text = patch_data["new_text"]

        occurrences = content.count(old_text)
        if occurrences != patch_data["replacements"]:
            return {"ok": False, "tool": "project_patch_apply", "error": "Conteúdo original mudou. Rollback virtual de patch abortado."}

        backup_path = _create_backup(resolved_path)
        new_content = content.replace(old_text, new_text)
        resolved_path.write_text(new_content, encoding="utf-8")

        patch_data["status"] = "applied"
        patch_data["backup_path"] = backup_path
        patch_data["applied_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        patch_file.write_text(json.dumps(patch_data, indent=2, ensure_ascii=False), encoding="utf-8")

        return {
            "ok": True,
            "tool": "project_patch_apply",
            "patch_id": patch_id,
            "path": path_str,
            "backup_path": backup_path,
            "status": "applied"
        }
    except Exception as e:
        return {"ok": False, "tool": "project_patch_apply", "error": str(e)}

def project_patch_rollback(patch_id: str):
    try:
        patch_file = _patch_file_for_read(patch_id)
        if not patch_file.exists():
            return {"ok": False, "tool": "project_patch_rollback", "error": "Patch não encontrado."}

        patch_data = json.loads(patch_file.read_text(encoding="utf-8"))
        if patch_data.get("status") != "applied":
            return {"ok": False, "tool": "project_patch_rollback", "error": f"Patch não está aplicado. Status atual: {patch_data.get('status')}"}

        path_str = patch_data["path"]
        resolved_path = validate_project_patch_path(path_str)

        backup_str = patch_data.get("backup_path")
        if not backup_str:
            return {"ok": False, "tool": "project_patch_rollback", "error": "Nenhum backup encontrado para este patch."}

        backup_path = get_aiw_root() / backup_str
        if not backup_path.exists():
            return {"ok": False, "tool": "project_patch_rollback", "error": "Arquivo de backup não encontrado fisicamente."}

        shutil.copy2(backup_path, resolved_path)

        patch_data["status"] = "rolled_back"
        patch_data["rolled_back_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        patch_file.write_text(json.dumps(patch_data, indent=2, ensure_ascii=False), encoding="utf-8")

        return {
            "ok": True,
            "tool": "project_patch_rollback",
            "patch_id": patch_id,
            "path": path_str,
            "status": "rolled_back"
        }
    except Exception as e:
        return {"ok": False, "tool": "project_patch_rollback", "error": str(e)}


# === Step 2: Safe git write tools + PR creation (gated strongly) ===
# - Default block: require explicit confirm=True
# - Only aiw workspace initially for auto side effects (like project_patch_apply)
# - Use validate_shell_command where possible + direct safe subprocess list
# - Path allowlists via validate_project_patch_path / validate_write_path
# - Backups via _create_backup before mutating ops
# - Never break existing read-only git_log/git_diff/shell git reads
# - integrate with aiw/patch + aiw/integration (e.g. create_outbox after)

def _git_ws_gate(confirm: bool = False, autonomous_persistent: bool = False) -> tuple[bool, dict | None]:
    """Common gate for git writes: confirm + aiw ws (initially).
    Trusted ws exception: for ws=="aiw" + autonomous_persistent=True (from persistent validated success context),
    allow commit/push/PR without extra confirm (still use policy gate upstream; non-aiw ws remain gated).
    Builds on autonomous-for-persistent comments.
    """
    if autonomous_persistent and _workspace_id() == "aiw":
        return True, None  # trusted aiw ws in persistent validated path
    if not confirm:
        return False, {"ok": False, "error": "confirmation_required", "note": "use confirm=True (or --confirm true in cli) for git writes"}
    if _workspace_id() != "aiw":
        return False, {"ok": False, "error": "git_write_blocked_for_external_ws", "note": "git writes + create_pr only for aiw workspace initially"}
    return True, None

def _safe_branch_name(name: str) -> str:
    name = (name or "").strip()
    if not name or not re.match(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,79}$", name):
        raise ValueError("invalid_branch_name")
    if ".." in name or name.endswith("/") or "@{" in name:
        raise ValueError("invalid_branch_name")
    return name

def git_create_branch(branch: str, base: str = "HEAD", confirm: bool = False, autonomous_persistent: bool = False):
    """Safe branch creation. Uses validate_shell_command + direct git. Gated.
    Supports autonomous_persistent for aiw ws trusted path (no extra confirm needed when flag set).
    """
    import subprocess
    try:
        allowed, err = _git_ws_gate(confirm, autonomous_persistent)
        if not allowed:
            return err
        b = _safe_branch_name(branch)
        base = base or "HEAD"
        # Use validate to enforce policy on cmd (now allows checkout)
        cmd_str = f"git checkout -b {b}"
        parts = validate_shell_command(cmd_str)
        cwd = str(validate_path("."))
        # backup current state lightly (no full tree, git handles)
        proc = subprocess.run(parts, cwd=cwd, capture_output=True, text=True, timeout=30)
        return {
            "ok": proc.returncode == 0,
            "tool": "git_create_branch",
            "branch": b,
            "base": base,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "confirmed": confirm,
            "workspace": _workspace_id()
        }
    except Exception as e:
        return {"ok": False, "tool": "git_create_branch", "error": str(e)}

def git_commit(message: str, paths: list[str] | None = None, confirm: bool = False, autonomous_persistent: bool = False, push: bool = False):
    """Safe commit on allowed paths only. Creates backups, uses validate, gates.
    Supports autonomous_persistent=True to relax confirm for aiw ws in persistent validated runs (policy still applies).
    Extended to support push=True for auto push after commit in success path (safely, only when gate passed).
    """
    import subprocess
    try:
        allowed, err = _git_ws_gate(confirm, autonomous_persistent)
        if not allowed:
            return err
        msg = (message or "aiw: safe agent edit").strip()
        if not msg or len(msg) > 300:
            return {"ok": False, "tool": "git_commit", "error": "invalid_commit_message"}
        cwd = str(validate_path("."))
        # determine files to commit: if paths given validate them; else use porcelain changed
        to_commit = []
        if paths:
            for p in paths:
                if not p or ".." in p or p.startswith("/"):
                    return {"ok": False, "tool": "git_commit", "error": f"invalid_path:{p}"}
                rp = validate_project_patch_path(p)  # or validate_write_path; project allows source_roots
                rel = str(rp.relative_to(get_root()))
                to_commit.append(rel)
        else:
            # fallback: all modified per git status (but still filter forbidden)
            try:
                st = subprocess.check_output(["git", "status", "--porcelain"], cwd=cwd, text=True, timeout=10)
                for line in st.splitlines():
                    if not line: continue
                    fp = line[3:].strip() if len(line)>3 else line.strip()
                    if fp and not any(x in fp.lower() for x in [".env", "secret", "token"]):
                        # quick check
                        try:
                            validate_project_patch_path(fp)
                            to_commit.append(fp)
                        except Exception:
                            pass
            except Exception:
                pass
        if not to_commit:
            return {"ok": False, "tool": "git_commit", "error": "no_allowed_files_to_commit"}
        # backups for changed files
        backups = []
        for f in to_commit:
            try:
                rp = get_root() / f
                bp = _create_backup(rp)
                if bp: backups.append(bp)
            except Exception:
                pass
        # use validated cmds
        add_cmd = ["git", "add", "--"] + to_commit
        # validate would allow if constructed, but use list directly for safety
        add_proc = subprocess.run(add_cmd, cwd=cwd, capture_output=True, text=True, timeout=20)
        if add_proc.returncode != 0:
            return {"ok": False, "tool": "git_commit", "error": "git_add_failed", "stderr": add_proc.stderr}
        commit_proc = subprocess.run(["git", "commit", "-m", msg], cwd=cwd, capture_output=True, text=True, timeout=30)
        result = {
            "ok": commit_proc.returncode == 0,
            "tool": "git_commit",
            "message": msg,
            "files": to_commit,
            "backups": backups,
            "stdout": commit_proc.stdout,
            "stderr": commit_proc.stderr,
            "confirmed": confirm,
            "autonomous_persistent": autonomous_persistent
        }
        # Extend to push if requested (safely, only after successful commit + gate passed).
        # Used for auto push in aiw ws persistent validated success path.
        if push and commit_proc.returncode == 0:
            try:
                cur = subprocess.check_output(["git", "branch", "--show-current"], cwd=cwd, text=True, timeout=5).strip() or "HEAD"
                if cur and cur != "HEAD":
                    push_proc = subprocess.run(["git", "push", "-u", "origin", cur], cwd=cwd, capture_output=True, text=True, timeout=60)
                    result["pushed"] = push_proc.returncode == 0
                    if push_proc.stderr:
                        result["push_stderr"] = push_proc.stderr[:300]
            except Exception as pe:
                result["pushed"] = False
                result["push_error"] = str(pe)[:120]
        return result
    except Exception as e:
        return {"ok": False, "tool": "git_commit", "error": str(e)}

def git_diff_for_pr(base_ref: str = "main", head_ref: str = "HEAD"):
    """Read-only diff suitable for PR description (base..head). Safe, no gate needed."""
    import subprocess
    try:
        cwd = str(validate_path("."))
        out = subprocess.check_output(
            ["git", "diff", f"{base_ref}..{head_ref}", "--stat", "--"],  # stat first safe
            cwd=cwd, text=True, stderr=subprocess.DEVNULL, timeout=15
        )
        full = subprocess.check_output(
            ["git", "diff", f"{base_ref}..{head_ref}", "--"], cwd=cwd, text=True, stderr=subprocess.DEVNULL, timeout=15
        )
        return {"ok": True, "tool": "git_diff_for_pr", "base": base_ref, "head": head_ref, "stat": out[:2000], "diff": full[:16000]}
    except Exception as e:
        return {"ok": False, "tool": "git_diff_for_pr", "error": str(e)}

# New basic browser research tool (safe fetch for external context/research, e.g. docs, APIs)
# Respects network policy via runtime gate in loop. GATED: requires network_access cap (see aiw/policy/capabilities.py
# web_fetch entry: network_access=True, requires_confirmation in manual; aiw/policy/runtime_gate.py blocks external_io/network
# unless allowed runtime/profile; called via python_eval in _build_rich_action under _check_capability).
# Enhanced for interactive browser: ALWAYS attempt playwright FIRST for render_js=True *or* research=True (make optional
# gracefully - catch ImportError + browser-not-installed errors like "Executable doesn't exist", launch failures etc).
# Basic 'actions' param supported (step 5 browser polish): e.g. ['follow', 'extract', 'extract:code'] executed simple (stdlib + graceful).
# - follow: manual redirect follow (limited hops) using urllib (urlopen follows but explicit support here).
# - extract: regex extract code blocks (```), title, h1/paragraph/content (no selector lib, stdlib re).
# Returns better structured for agent: title (parsed), links_summary, actions_executed, content (post-extract if applied).
# Callable from loop actions via python_eval wrapper. Keep minimal: text only, timeouts, no arbitrary scripts.
# Still gated (network_access checked before exec in loop/policy).
def web_fetch(url: str, max_bytes: int = 8000, render_js: bool = False, research: bool = False, actions: list | None = None):
    """Enhanced web_fetch with basic actions support (follow, extract).
    actions: list of simple ops e.g. ["follow", "extract:code"] (stdlib + graceful).
    Still fully gated by network_access policy.
    """
    if not url.startswith(("http://", "https://")):
        return {"ok": False, "tool": "web_fetch", "error": "only http/https allowed", "url": url}
    actions = actions or []
    attempt_playwright = bool(render_js or research)
    fallback_note = None

    # 1. Always attempt playwright first when render_js or research detected (graceful optional: no hard dep, catch install errs)
    if attempt_playwright:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(8000)
                page.goto(url, wait_until="domcontentloaded")
                # get rendered content (better for interactive/JS docs, complex sites)
                content = page.content() or ""
                ctype = "text/html"
                # extract title from page for better agent struct (no extra calls needed)
                try:
                    page_title = page.title() or ""
                except Exception:
                    page_title = ""
                if len(content) > max_bytes:
                    content = content[:max_bytes]
                    truncated = True
                else:
                    truncated = False
                browser.close()
                title, links = _extract_web_metadata(content, ctype)
                if not title:
                    title = page_title[:200]
                return {
                    "ok": True,
                    "tool": "web_fetch",
                    "url": url,
                    "content_type": ctype,
                    "content": content[:max_bytes],
                    "bytes": min(len(content), max_bytes),
                    "truncated": truncated,
                    "title": title or "",
                    "links_summary": links,
                    "actions": actions,
                    "note": "Playwright rendered fetch (interactive browser for JS/docs). Gated by network_access cap + optional dep.",
                    "engine": "playwright",
                    "research_mode": research,
                }
        except ImportError:
            fallback_note = "playwright not installed; using urllib"
        except Exception as pw_e:
            # catch more errors gracefully e.g. browser not installed ("Executable doesn't exist"), launch, timeout etc.
            fallback_note = f"playwright_err:{str(pw_e)[:100]}; using urllib (graceful)"

    # 2. Surgical urllib fallback (stdlib; used when !render_js or pw failed/graceful)
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "AIW/1.0 (safe research fetch)"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw = resp.read(max_bytes + 1)
            truncated = len(raw) > max_bytes
            data = raw[:max_bytes]
            ctype = resp.headers.get("Content-Type", "")
            text = data.decode("utf-8", errors="replace")
            note = "Basic fetch for research/docs (urllib). For interactive/JS use render_js=True (or research=True) + playwright."
            if fallback_note:
                note = fallback_note + "; " + note
            title, links = _extract_web_metadata(text, ctype)
            return {
                "ok": True,
                "tool": "web_fetch",
                "url": url,
                "content_type": ctype,
                "content": text,
                "bytes": len(data),
                "truncated": truncated,
                "title": title or "",
                "links_summary": links,
                "actions": actions,
                "note": note,
                "engine": "urllib",
                "research_mode": research,
            }
    except Exception as e:
        return {"ok": False, "tool": "web_fetch", "url": url, "error": str(e)[:200]}

    # Basic actions (post-fetch, stdlib only; gated elsewhere)
    result = {"ok": True, "tool": "web_fetch", "url": url, "content": text[:max_bytes] if 'text' in locals() else "", "actions_performed": []}
    if actions:
        for act in (actions or []):
            try:
                if act == "follow" or (isinstance(act, str) and act.startswith("follow")):
                    # simple urllib follow (already done in main, note it)
                    result["actions_performed"].append({"action": "follow", "note": "followed redirects (urllib)"})
                elif isinstance(act, str) and act.startswith("extract:"):
                    kind = act.split(":", 1)[1]
                    if kind == "code":
                        codes = re.findall(r'```(?:\w+)?\n(.*?)\n```', text, re.DOTALL) if 'text' in locals() else []
                        result["extracted_code"] = codes[:3]
                        result["actions_performed"].append({"action": act, "count": len(codes)})
                    else:
                        result["actions_performed"].append({"action": act, "note": "extract not implemented for kind"})
            except Exception as ae:
                result["actions_performed"].append({"action": act, "error": str(ae)[:60]})
    if actions:
        result["actions"] = actions
    return result if actions else {"ok": True, "tool": "web_fetch", "url": url, "content_type": ctype, "content": text, "bytes": len(data), "truncated": truncated, "title": title or "", "links_summary": links, "note": note, "engine": "urllib", "research_mode": research}


def _extract_web_metadata(text: str, ctype: str) -> tuple[str, list]:
    """Crude stdlib-only parse for title + top links summary (no bs4/deps). For agent structure."""
    title = ""
    links: list = []
    try:
        if "html" in (ctype or "").lower() or "<title" in text.lower()[:2000]:
            m = re.search(r"<title[^>]*>([^<]+)</title>", text, re.IGNORECASE | re.DOTALL)
            if m:
                title = m.group(1).strip()[:200]
        # extract up to 5 links (href + text) for summary
        for m in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]{0,80})</a>', text[:8000], re.IGNORECASE):
            href = (m.group(1) or "").strip()[:300]
            txt = (m.group(2) or "").strip()[:80] or href
            if href and (href.startswith(("http", "/", "#", ".")) or "://" in href[:10]):
                links.append({"href": href, "text": txt})
            if len(links) >= 5:
                break
    except Exception:
        pass
    return title, links

def create_pr(title: str, body: str = "", base: str = "main", head: str | None = None, confirm: bool = False, use_integration: bool = True, patch_id: str | None = None, run_id: str | None = None, test_results: str | None = None, autonomous_persistent: bool = False, evidence: str | None = None):
    """
    High-level safe PR creation (gated).
    - Full flow on confirm: git checkout -b (if needed/derived from patch), git add/commit via git_commit, push, gh pr create.
    - Uses patch context if patch_id provided (from previous project_patch_apply or trace).
    - Computes PR diff via git_diff_for_pr.
    - Uses evidence_bundle or create_outbox (list/read payload) for PR payload/body when patch_id present.
    - Executes gh pr create only with confirm + aiw ws (may be no-op if no remote/gh).
    - Always returns preview + suggested command for manual if blocked.
    - Supports autonomous for persistent runs: pass run_id/test_results/evidence for body with evidence + test results + link to run. Gated by policy (see evaluate) + _git_ws_gate.
    - For aiw ws + autonomous_persistent (persistent validated success): relax confirm (trusted exception), still policy gate; git_commit+push auto.
    Integrates with aiw/integration (create_outbox) + aiw/patch flows.
    Builds surgically on existing "autonomous for persistent" comments.
    """
    import shutil
    try:
        cwd = str(validate_path("."))
        ws_id = _workspace_id()

        # Policy gate for create_pr (for safety; autonomous persistent calls use confirmed after loop policy check)
        # Still enforce policy; for autonomous_persistent on aiw, use offline/confirmed=True semantics.
        confirmed_for_pol = bool(confirm) or bool(autonomous_persistent)
        try:
            from aiw.policy.registry import get_policy_engine
            engine = get_policy_engine()
            pol_dec = engine.evaluate_capability(
                ws_id, "create_pr", mode=("offline" if confirmed_for_pol else "dry-run"),
                operation="create_pr", confirmed=bool(confirmed_for_pol),
                fixed_code=True, local_execution=True, tracked=True
            )
            if not pol_dec.get("allowed"):
                # still allow preview path; caller (loop auto) will have pre-checked
                if not confirmed_for_pol:
                    ret = {"ok": False, "error": "policy_denied_create_pr", "policy": pol_dec}
                    ret["run_id"] = run_id
                    ret["test_results"] = test_results
                    return ret
        except Exception:
            pass  # best effort; fallthrough to git gate

        allowed, err = _git_ws_gate(confirm, autonomous_persistent)
        if not allowed:
            # still return preview even on gate fail (for UI "show diff, require confirm")
            try:
                d = git_diff_for_pr(base, head or "HEAD")
                err["preview_diff"] = d.get("diff") or d.get("stat")
            except Exception:
                pass
            err.setdefault("run_id", run_id)
            err.setdefault("test_results", test_results)
            return err

        # load patch context if provided (from previous apply/trace)
        patch_ctx = None
        changed_files = None
        if patch_id:
            try:
                pf = _patch_file_for_read(patch_id)
                if pf.exists():
                    patch_ctx = json.loads(pf.read_text(encoding="utf-8"))
                    changed_files = patch_ctx.get("changed_files") or ([patch_ctx.get("path")] if patch_ctx.get("path") else None)
                    if not title or title in ("", "AIW agent change"):
                        title = f"aiw: {patch_ctx.get('reason', 'patch change')} [{patch_id[:12]}]"
            except Exception:
                pass

        # derive head from patch if not set
        target_head = head
        if not target_head or target_head == "HEAD":
            if patch_id:
                target_head = f"aiw/patch-{patch_id[:8]}"
            else:
                target_head = "aiw/pr-" + time.strftime("%Y%m%d%H%M")
        head = target_head

        # prepare PR payload using evidence_bundle or create_outbox if patch context
        pr_payload_body = body or ""
        run_link = f"Link to run: .aiw/workspaces/{ws_id}/agent-iterative-loop/runs/{run_id}" if run_id else ""
        if run_link:
            pr_payload_body = (pr_payload_body + "\n\n" + run_link).strip()
        if test_results:
            pr_payload_body = (pr_payload_body + "\n\nTest results / validation:\n" + str(test_results)[:2000]).strip()

        if use_integration and patch_id and not pr_payload_body:
            used_payload_src = None
            try:
                # prefer outbox payload.md (pr_summary)
                from aiw.integration.integration_outbox import list_outbox_items, resolve_outbox_item_file
                ob_res = list_outbox_items(ws_id, patch_id)
                for itm in (ob_res.get("items") or []):
                    if itm.get("kind") == "pr_summary" and itm.get("item_id"):
                        fpath = resolve_outbox_item_file(ws_id, itm["item_id"], "payload.md")
                        if fpath and fpath.exists():
                            pr_payload_body = fpath.read_text(encoding="utf-8")[:4500]
                            used_payload_src = "outbox:" + itm["item_id"]
                            break
            except Exception:
                pass
            if not pr_payload_body:
                try:
                    # fallback to evidence bundle info for payload
                    from aiw.patch.evidence_bundle import list_evidence_bundles
                    eb_res = list_evidence_bundles(ws_id, patch_id)
                    if eb_res.get("bundles"):
                        b = eb_res["bundles"][0]
                        pr_payload_body = f"AIW Patch {patch_id}\n\nEvidence Bundle: {b.get('bundle_id')}\nDecision: {b.get('decision_record',{}).get('decision')}\nRisk: {b.get('risk_summary',{}).get('level')}\n\nSee attached evidence for full validation."
                        used_payload_src = "evidence_bundle"
                except Exception:
                    pass
            if not pr_payload_body:
                try:
                    # last attempt: create_outbox_item (will use latest export if present)
                    from aiw.integration.integration_outbox import create_outbox_item
                    ob_create = create_outbox_item(ws_id, patch_id, "github_pr", "pr_summary")
                    if ob_create.get("ok") and ob_create.get("item"):
                        # re-list to resolve payload file
                        ob_res2 = list_outbox_items(ws_id, patch_id)
                        for itm in (ob_res2.get("items") or []):
                            fpath = resolve_outbox_item_file(ws_id, itm["item_id"], "payload.md")
                            if fpath and fpath.exists():
                                pr_payload_body = fpath.read_text(encoding="utf-8")[:4500]
                                used_payload_src = "outbox_created:" + itm["item_id"]
                                break
                except Exception as ie:
                    pass
        # Always ensure run link + test/evidence for autonomous persistent PRs (even without patch_id)
        if run_id and run_link not in (pr_payload_body or ""):
            pr_payload_body = ((pr_payload_body or "") + "\n\n" + run_link).strip()
        if test_results and "Test results" not in (pr_payload_body or ""):
            pr_payload_body = ((pr_payload_body or "") + "\n\nTest results / validation (from persistent run):\n" + str(test_results)[:1800]).strip()
        if evidence:
            pr_payload_body = ((pr_payload_body or "") + "\n\nEvidence:\n" + str(evidence)[:2000]).strip()

        # Full flow: checkout -b if needed (on confirm gate passed)
        # For autonomous_persistent on aiw ws: flags passed so git_commit + push auto in trusted persistent validated success.
        did_branch = False
        try:
            cur_branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=cwd, text=True, timeout=5).strip() or "HEAD"
            if head and head != cur_branch and head != "HEAD":
                br_res = git_create_branch(head, base="HEAD", confirm=confirm, autonomous_persistent=autonomous_persistent)
                did_branch = bool(br_res.get("ok"))
        except Exception:
            pass

        # commit via git_commit (uses patch changed_files if avail); push via extension in git_commit for auto
        did_commit = False
        if changed_files or True:  # allow auto-detect in git_commit
            try:
                cmsg = title or "aiw: change via create_pr"
                c_res = git_commit(cmsg, paths=changed_files, confirm=confirm, autonomous_persistent=autonomous_persistent, push=bool(autonomous_persistent))
                did_commit = bool(c_res.get("ok"))
            except Exception:
                pass

        # compute diff now on (new) head
        diff_res = git_diff_for_pr(base, head)
        pr_diff = diff_res.get("diff") or diff_res.get("stat", "")

        # push (kept for create_pr orchestration; git_commit push also fires for autonomous)
        pushed = False
        try:
            push_proc = subprocess.run(["git", "push", "-u", "origin", head], cwd=cwd, capture_output=True, text=True, timeout=60)
            pushed = push_proc.returncode == 0
        except Exception:
            pass

        # gh pr create (gated already)
        gh_cmd = ["gh", "pr", "create", "--base", base, "--head", head, "--title", title, "--body", (pr_payload_body or body or pr_diff[:4000])]
        pr_url = None
        if shutil.which("gh"):
            try:
                gh_proc = subprocess.run(gh_cmd, cwd=cwd, capture_output=True, text=True, timeout=60)
                if gh_proc.returncode == 0:
                    out = (gh_proc.stdout or gh_proc.stderr or "").strip()
                    pr_url = out.splitlines()[-1] if out else None
            except Exception:
                pass

        # prepare integration outbox note (or use if already)
        outbox_res = {"note": "used payload from evidence/outbox" if pr_payload_body else "integration available; use exports for full pr_summary"}
        if use_integration and patch_id:
            try:
                from aiw.integration.integration_outbox import list_outbox_items
                ob_final = list_outbox_items(ws_id, patch_id)
                outbox_res = {"items": len(ob_final.get("items", [])), "latest": (ob_final.get("items") or [{}])[0].get("item_id")}
            except Exception as ie:
                outbox_res = {"note": f"outbox note: {str(ie)[:60]}"}

        # Fallback: create a pr-proposal artifact (like patch) for review
        pr_id = time.strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:6] + "-pr"
        pr_dir = _patches_dir() / "pr-proposals"
        pr_dir.mkdir(parents=True, exist_ok=True)
        (pr_dir / f"{pr_id}.json").write_text(json.dumps({
            "pr_id": pr_id,
            "title": title,
            "body": pr_payload_body or body,
            "base": base,
            "head": head,
            "diff": pr_diff[:8000],
            "pushed": pushed,
            "pr_url": pr_url,
            "patch_id": patch_id,
            "run_id": run_id,
            "test_results": (test_results or "")[:500] if test_results else None,
            "outbox": outbox_res,
            "did_branch": did_branch,
            "did_commit": did_commit,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "workspace": ws_id,
            "confirmed": confirm,
            "autonomous": bool(run_id),
            "autonomous_persistent": bool(autonomous_persistent),
            "evidence": (evidence or "")[:300] if evidence else None
        }, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "tool": "create_pr",
            "pr_id": pr_id,
            "title": title,
            "head": head,
            "base": base,
            "diff_preview": pr_diff[:1200],
            "pushed": pushed,
            "pr_url": pr_url,
            "patch_id": patch_id,
            "run_id": run_id,
            "integration": outbox_res,
            "did_branch": did_branch,
            "did_commit": did_commit,
            "autonomous_persistent": bool(autonomous_persistent),
            "proposal_file": f".aiw/.../patches/pr-proposals/{pr_id}.json",
            "note": "Full flow executed (branch+commit+push+gh for confirm or autonomous_persistent on aiw trusted). PR proposal created. Uses evidence_bundle/create_outbox for payload when patch_id. Includes run link + tests + evidence for autonomous persistent validated."
        }
    except Exception as e:
        return {"ok": False, "tool": "create_pr", "error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", choices=[
        "directory_list", "file_read", "shell_exec", "file_write", "file_patch",
        "project_patch_preview", "project_patch_apply", "project_patch_rollback",
        "git_create_branch", "git_commit", "git_diff_for_pr", "create_pr",
        "web_fetch"
    ])
    parser.add_argument("--path", type=str)
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--max-bytes", type=int, default=8000)
    parser.add_argument("--command", type=str)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--content", type=str)

    # Handle boolean flag appropriately
    parser.add_argument("--overwrite", type=str, default="false")

    parser.add_argument("--old-text", type=str)
    parser.add_argument("--new-text", type=str)
    parser.add_argument("--expected-replacements", type=int, default=1)
    parser.add_argument("--reason", type=str, default="")
    parser.add_argument("--patch-id", type=str)
    # For new safe git write tools
    parser.add_argument("--branch", type=str)
    parser.add_argument("--message", type=str)
    parser.add_argument("--title", type=str)
    parser.add_argument("--confirm", type=str, default="false")
    # basic support for web_fetch interactive
    parser.add_argument("--render-js", type=str, default="false")
    parser.add_argument("--research", type=str, default="false")

    args = parser.parse_args()

    if args.tool == "directory_list":
        print(json.dumps(directory_list(args.path or ".", args.max_depth, args.limit), indent=2))
    elif args.tool == "file_read":
        print(json.dumps(file_read(args.path, args.max_bytes), indent=2))
    elif args.tool == "shell_exec":
        print(json.dumps(shell_exec(args.command, args.timeout), indent=2))
    elif args.tool == "file_write":
        overwrite_bool = args.overwrite.lower() in ("true", "1", "yes")
        print(json.dumps(file_write(args.path, args.content, overwrite_bool), indent=2))
    elif args.tool == "file_patch":
        print(json.dumps(file_patch(args.path, args.old_text, args.new_text, args.expected_replacements), indent=2))
    elif args.tool == "project_patch_preview":
        print(json.dumps(project_patch_preview(args.path, args.old_text, args.new_text, args.expected_replacements, args.reason), indent=2))
    elif args.tool == "project_patch_apply":
        print(json.dumps(project_patch_apply(args.patch_id), indent=2))
    elif args.tool == "project_patch_rollback":
        print(json.dumps(project_patch_rollback(args.patch_id), indent=2))
    elif args.tool == "git_create_branch":
        print(json.dumps(git_create_branch(args.branch or args.path or "aiw/safe-edit", confirm=(args.confirm or "false").lower() in ("true","1","yes")), indent=2))
    elif args.tool == "git_commit":
        print(json.dumps(git_commit(args.message or "aiw safe edit", paths=(args.path or "").split() if args.path else None, confirm=(args.confirm or "false").lower() in ("true","1","yes")), indent=2))
    elif args.tool == "git_diff_for_pr":
        print(json.dumps(git_diff_for_pr(args.old_text or "main", args.new_text or "HEAD"), indent=2))
    elif args.tool == "create_pr":
        pid = getattr(args, "patch_id", None) or getattr(args, "patch-id", None)
        print(json.dumps(create_pr(args.title or "AIW agent change", body=args.reason or "", patch_id=pid, confirm=(args.confirm or "false").lower() in ("true","1","yes")), indent=2))
    elif args.tool == "web_fetch":
        rjs = (getattr(args, "render_js", "false") or "false").lower() in ("true", "1", "yes")
        rsr = (getattr(args, "research", "false") or "false").lower() in ("true", "1", "yes")
        print(json.dumps(web_fetch(args.path or "", args.max_bytes, render_js=rjs, research=rsr), indent=2))
    elif args.tool == "web_search":
        print(json.dumps(web_search(args.query or ""), indent=2))
    elif args.tool == "git_log":
        print(json.dumps(git_log(args.path or "."), indent=2))
    elif args.tool == "git_diff":
        print(json.dumps(git_diff(args.old_text or "HEAD~1", args.new_text or "HEAD"), indent=2))


# Round 2 - 6. Mais tools (stubs + integration with capabilities + context)
def web_search(query: str, max_results: int = 5):
    # Improved tool (4): tries simple urllib if available, else informative stub.
    # Respects policy (network_access).
    try:
        import urllib.request
        import urllib.parse
        # Very basic - in practice would use a proper search API
        q = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={q}"
        req = urllib.request.Request(url, headers={"User-Agent": "AIW/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode("utf-8", errors="ignore")[:2000]
            # Naive extraction
            results = [{"title": f"Search result for {query}", "url": "https://duckduckgo.com", "snippet": html[:300]}]
            return {"ok": True, "tool": "web_search", "query": query, "results": results[:max_results], "note": "Basic live search attempt"}
    except Exception as e:
        return {
            "ok": True,
            "tool": "web_search",
            "query": query,
            "results": [{"title": f"Simulated: {query}", "url": "https://example.com", "snippet": "No net or blocked - using stub."}],
            "note": f"Stub (error: {str(e)[:100]}). Real search requires network + policy allow."
        }

def git_log(path: str = ".", max_entries: int = 10):
    try:
        import subprocess
        out = subprocess.check_output(["git", "log", f"-{max_entries}", "--oneline", "--", path], cwd=".", text=True, stderr=subprocess.DEVNULL)
        return {"ok": True, "tool": "git_log", "entries": [l.strip() for l in out.strip().splitlines()]}
    except Exception as e:
        return {"ok": False, "tool": "git_log", "error": str(e)}

def git_diff(ref_a: str = "HEAD~1", ref_b: str = "HEAD", path: str = "."):
    try:
        import subprocess
        out = subprocess.check_output(["git", "diff", ref_a, ref_b, "--", path], cwd=".", text=True, stderr=subprocess.DEVNULL)
        return {"ok": True, "tool": "git_diff", "diff": out[:8000]}
    except Exception as e:
        return {"ok": False, "tool": "git_diff", "error": str(e)}

# From step1 subagent: run_tests for structured pytest output in auto-correction
def _parse_pytest_output(stdout: str, stderr: str) -> dict:
    combined = (stdout or "") + "\n" + (stderr or "")
    failed = []
    passed = 0
    errors = []
    for line in combined.splitlines():
        if "FAILED" in line or "::" in line and "FAILED" in line:
            failed.append(line.strip()[:200])
        if line.strip().startswith("E   "):
            errors.append(line.strip()[:200])
        if "passed" in line and "failed" in line:
            import re
            m = re.search(r"(\d+) passed", line)
            if m: passed = int(m.group(1))
    return {
        "passed_count": passed,
        "failed_count": len(failed),
        "failed_tests": failed[:5],
        "error_summary": "\n".join(errors[:3]) or (failed[0] if failed else "")
    }

def run_tests(target: str = ".", pytest_args: str = "-q --tb=short", timeout: int = 60):
    try:
        resolved = validate_path(target)
        cmd = ["python3", "-m", "pytest", str(resolved), *shlex.split(pytest_args)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(get_root()))
        parsed = _parse_pytest_output(proc.stdout, proc.stderr)
        return {
            "ok": proc.returncode == 0,
            "tool": "run_tests",
            "passed_count": parsed["passed_count"],
            "failed_count": parsed["failed_count"],
            "failed_tests": parsed["failed_tests"],
            "error_summary": parsed["error_summary"],
            "stdout": proc.stdout[-2000:],
            "stderr": proc.stderr[-500:],
            "returncode": proc.returncode
        }
    except Exception as e:
        return {"ok": False, "tool": "run_tests", "error": str(e)}
