import json
import os
import subprocess
import datetime
from pathlib import Path
from urllib.parse import quote

SENSITIVE_VALUE_PARTS = (".env", "litellm_master_key", "api_key", "client_secret", "private_key")
SENSITIVE_NAME_PARTS = ("key", "token", "secret", "password", "credential", "private")


def normalize_workspace_id(workspace_id: str | None = None) -> str:
    value = (workspace_id or os.environ.get("AIW_WORKSPACE_ID") or "aiw").strip()
    if not value:
        return "aiw"
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in value)[:80] or "aiw"


def workspace_base(root: Path, workspace_id: str | None = None) -> Path:
    artifact_root = Path(os.environ.get("AIW_ROOT", root)).resolve()
    return artifact_root / ".aiw" / "workspaces" / normalize_workspace_id(workspace_id)


def workspace_context_dir(root: Path, workspace_id: str | None = None) -> Path:
    return workspace_base(root, workspace_id) / "context"


def workspace_runs_dirs(root: Path, workspace_id: str | None = None) -> list[tuple[str, Path]]:
    ws_id = normalize_workspace_id(workspace_id)
    dirs = [("scoped", workspace_base(root, ws_id) / "runs")]
    if ws_id == "aiw":
        dirs.append(("legacy", root / ".aiw" / "runs"))
    return dirs


def workspace_patches_dirs(root: Path, workspace_id: str | None = None) -> list[tuple[str, Path]]:
    ws_id = normalize_workspace_id(workspace_id)
    dirs = [("scoped", workspace_base(root, ws_id) / "patches")]
    if ws_id == "aiw":
        dirs.append(("legacy", root / ".aiw" / "patches"))
    return dirs


def _first_existing_context_file(root: Path, filename: str, workspace_id: str | None = None) -> Path:
    ws_id = normalize_workspace_id(workspace_id)
    scoped = workspace_context_dir(root, ws_id) / filename
    if scoped.is_file():
        return scoped
    if ws_id == "aiw":
        artifact_root = Path(os.environ.get("AIW_ROOT", root)).resolve()
        return artifact_root / ".aiw" / "context" / filename
    return scoped

def is_sensitive_path(path_str: str) -> bool:
    lower = path_str.lower()
    if ".env" in lower:
        return True
    return any(p in lower for p in SENSITIVE_NAME_PARTS)

def mask_text(text: str, limit: int = 900) -> str:
    if not text:
        return ""
    lower = text.lower()
    if any(p in lower for p in SENSITIVE_VALUE_PARTS):
        return "[masked]"
    if len(text) > limit:
        return text[:limit].rstrip() + "..."
    return text

def short_git_head(root: Path) -> str:
    try:
        proc = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True, text=True, timeout=2)
        return proc.stdout.strip() or "-"
    except Exception:
        return "-"

def current_git_branch(root: Path) -> str:
    try:
        proc = subprocess.run(["git", "branch", "--show-current"], cwd=root, capture_output=True, text=True, timeout=2)
        return proc.stdout.strip() or "-"
    except Exception:
        return "-"

def read_text_safe(path: Path) -> str:
    try:
        if path.stat().st_size > 1024 * 1024:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

def _build_search_index(root: Path, branch: str, head: str, out_path: Path, workspace_id: str | None = None):
    docs = []
    ws_id = normalize_workspace_id(workspace_id)

    def add_doc(dtype: str, title: str, path: Path, rel_path: str, snippet: str, terms: list[str], scope: str = "repo"):
        if is_sensitive_path(rel_path) or is_sensitive_path(title):
            return
        # Basic check for sensitive values in snippet before caching
        if any(p in snippet.lower() for p in SENSITIVE_VALUE_PARTS):
            snippet = "[masked]"

        try:
            stat = path.stat()
            mtime = int(stat.st_mtime)
            size = stat.st_size
        except:
            mtime = 0
            size = 0

        docs.append({
            "id": rel_path,
            "type": dtype,
            "title": title,
            "path": rel_path,
            "mtime": mtime,
            "size": size,
            "terms": terms,
            "snippet": snippet[:400],
            "workspace_id": ws_id,
            "scope": scope
        })

    # README
    readme = root / "README.md"
    if readme.is_file():
        text = read_text_safe(readme)
        add_doc("doc", "README.md", readme, "README.md", text[:400].replace("\n", " "), ["readme", "root", "doc"])

    # docs
    docs_dir = root / "docs"
    if docs_dir.exists():
        for dpath in docs_dir.rglob("*"):
            if not dpath.is_file() or dpath.suffix not in (".md", ".txt"): continue
            rel = str(dpath.relative_to(root))
            text = read_text_safe(dpath)
            add_doc("doc", dpath.name, dpath, rel, text[:400].replace("\n", " "), [dpath.stem.lower()])

    # runs
    for scope, runs_dir in workspace_runs_dirs(root, ws_id):
        if not runs_dir.exists():
            continue
        for run_path in runs_dir.iterdir():
            if not run_path.is_dir(): continue
            rel_run = str(run_path.relative_to(root))
            title = run_path.name
            task_md = run_path / "task.md"
            if task_md.exists():
                text = read_text_safe(task_md)
                for line in text.splitlines():
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break

            # index run summary
            summary_path = run_path / "summary.md"
            if summary_path.is_file():
                text = read_text_safe(summary_path)
                add_doc("run", title, summary_path, str(summary_path.relative_to(root)), text[:400].replace("\n", " "), ["run", "summary", run_path.name.lower()], scope)

            # index commands.log
            commands_path = run_path / "commands.log"
            if commands_path.is_file():
                text = read_text_safe(commands_path)
                add_doc("run", f"{title} (Commands)", commands_path, str(commands_path.relative_to(root)), text[:400].replace("\n", " "), ["run", "commands", "log"], scope)

            # index tool-traces.jsonl
            traces_path = run_path / "tool-traces.jsonl"
            if traces_path.is_file():
                text = read_text_safe(traces_path)
                add_doc("run", f"{title} (Tools)", traces_path, str(traces_path.relative_to(root)), text[:400].replace("\n", " "), ["run", "tools", "traces"], scope)

            # index messages.json
            msgs_path = run_path / "messages.json"
            if msgs_path.is_file():
                text = read_text_safe(msgs_path)
                add_doc("run", f"{title} (Messages)", msgs_path, str(msgs_path.relative_to(root)), text[:400].replace("\n", " "), ["run", "messages", "llm"], scope)

    # patches
    for scope, patches_dir in workspace_patches_dirs(root, ws_id):
        if not patches_dir.exists():
            continue
        for ppath in patches_dir.glob("*.json"):
            if not ppath.is_file(): continue
            try:
                data = json.loads(read_text_safe(ppath))
                title = f"Patch {ppath.stem}"
                target = data.get("path", "")
                reason = data.get("reason", "")
                diff = data.get("diff", "")
                snip = (reason + " " + diff)[:400].replace("\n", " ")
                add_doc("patch", title, ppath, str(ppath.relative_to(root)), snip, ["patch", target.lower()], scope)
            except: pass

    # tasks
    tasks_dir = root / "reports" / "aiw-cockpit" / "tasks"
    if tasks_dir.exists():
        for tpath in tasks_dir.rglob("*.md"):
            if not tpath.is_file(): continue
            text = read_text_safe(tpath)
            add_doc("task", tpath.name, tpath, str(tpath.relative_to(root)), text[:400].replace("\n", " "), ["task", "report"])

    # internal tasks (.aiw/tasks)
    aiw_tasks = root / ".aiw" / "tasks"
    if aiw_tasks.exists():
        for tpath in aiw_tasks.rglob("*.md"):
            if not tpath.is_file(): continue
            text = read_text_safe(tpath)
            add_doc("task", tpath.name, tpath, str(tpath.relative_to(root)), text[:400].replace("\n", " "), ["task"])

    index_data = {
        "version": 1,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "repo_head": head,
        "branch": branch,
        "workspace_id": ws_id,
        "artifact_scope": "scoped",
        "document_count": len(docs),
        "documents": docs
    }

    out_path.write_text(json.dumps(index_data, indent=2, ensure_ascii=False))
    return index_data


def _build_context_pack(root: Path, branch: str, head: str, out_path: Path, workspace_id: str | None = None):
    ws_id = normalize_workspace_id(workspace_id)
    docs_dir = root / "docs"
    runbooks_dir = docs_dir / "runbooks"
    arch_dir = docs_dir / "architecture"

    docs_count = len(list(docs_dir.rglob("*.md"))) if docs_dir.is_dir() else 0
    runbooks_count = len(list(runbooks_dir.glob("*.md"))) if runbooks_dir.is_dir() else 0
    arch_count = len(list(arch_dir.glob("*.md"))) if arch_dir.is_dir() else 0
    runs_count = sum(len([p for p in d.iterdir() if p.is_dir()]) for _, d in workspace_runs_dirs(root, ws_id) if d.is_dir())
    patches_count = sum(len(list(d.glob("*.json"))) for _, d in workspace_patches_dirs(root, ws_id) if d.is_dir())
    readme_ok = (root / "README.md").is_file()

    sources = []
    if readme_ok:
        text = read_text_safe(root / "README.md")
        sources.append({"type": "readme", "path": "README.md", "title": "README", "summary": text[:100].replace("\n", " ")})

    if runbooks_dir.is_dir():
        for p in runbooks_dir.glob("*.md"):
            text = read_text_safe(p)
            sources.append({"type": "runbook", "path": str(p.relative_to(root)), "title": p.name, "summary": text[:100].replace("\n", " ")})

    if arch_dir.is_dir():
        for p in arch_dir.glob("*.md"):
            text = read_text_safe(p)
            sources.append({"type": "architecture", "path": str(p.relative_to(root)), "title": p.name, "summary": text[:100].replace("\n", " ")})

    if docs_count > 0 and readme_ok:
        health_status = "good"
    elif readme_ok or docs_count > 0:
        health_status = "incomplete"
    else:
        health_status = "needs_attention"

    pack_data = {
        "version": 1,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "workspace_id": ws_id,
        "artifact_scope": "scoped",
        "repo": {
            "branch": branch,
            "head": head
        },
        "coverage": {
            "readme": readme_ok,
            "docs_count": docs_count,
            "runbooks_count": runbooks_count,
            "architecture_docs_count": arch_count,
            "runs_count": runs_count,
            "patches_count": patches_count
        },
        "sources": sources,
        "health": {
            "status": health_status,
            "notes": []
        }
    }

    out_path.write_text(json.dumps(pack_data, indent=2, ensure_ascii=False))
    return pack_data

def rebuild_indexes(root_path: Path, workspace_id: str | None = None) -> dict:
    ws_id = normalize_workspace_id(workspace_id)
    ctx_dir = workspace_context_dir(root_path, ws_id)
    ctx_dir.mkdir(parents=True, exist_ok=True)

    branch = current_git_branch(root_path)
    head = short_git_head(root_path)

    idx_path = ctx_dir / "search-index.json"
    pack_path = ctx_dir / "context-pack.json"

    try:
        _build_search_index(root_path, branch, head, idx_path, ws_id)
        _build_context_pack(root_path, branch, head, pack_path, ws_id)
        return {
            "ok": True,
            "message": "Index and Context Pack rebuilt successfully.",
            "workspace_id": ws_id,
            "artifact_scope": "scoped",
            "context_dir": str(ctx_dir),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}

def get_search_index(root_path: Path, workspace_id: str | None = None) -> dict | None:
    idx_path = _first_existing_context_file(root_path, "search-index.json", workspace_id)
    if not idx_path.is_file():
        return None
    try:
        return json.loads(idx_path.read_text(encoding="utf-8"))
    except:
        return None

def get_context_pack(root_path: Path, workspace_id: str | None = None) -> dict | None:
    pack_path = _first_existing_context_file(root_path, "context-pack.json", workspace_id)
    if not pack_path.is_file():
        return None
    try:
        return json.loads(pack_path.read_text(encoding="utf-8"))
    except:
        return None


def build_agent_context(root_path: Path, workspace_id: str | None = None) -> dict:
    ws_id = normalize_workspace_id(workspace_id)
    pack = get_context_pack(root_path, ws_id)
    if not pack:
        res = rebuild_indexes(root_path, ws_id)
        pack = get_context_pack(root_path, ws_id)

    if not pack:
        return {'enabled': False, 'text': '', 'json': {}, 'md': ''}

    sources = []
    text_blocks = []

    def add_source(spath, reason):
        p = root_path / spath
        if p.is_file():
            text = read_text_safe(p)
            sources.append({
                "type": "doc",
                "path": spath,
                "title": p.name,
                "reason": reason
            })
            text_blocks.append(f"--- File: {spath} ---\n{text[:2000]}")

    add_source("README.md", "Main project documentation")

    if (root_path / "docs" / "MODEL_STRATEGY.md").is_file():
        add_source("docs/MODEL_STRATEGY.md", "Model strategy")

    runbooks_dir = root_path / "docs" / "runbooks"
    if runbooks_dir.is_dir():
        for rb in sorted(runbooks_dir.glob("*.md"))[:3]:
            add_source(str(rb.relative_to(root_path)), "Runbook reference")

    arch_dir = root_path / "docs" / "architecture"
    if arch_dir.is_dir():
        for ar in sorted(arch_dir.glob("*.md"))[:2]:
            add_source(str(ar.relative_to(root_path)), "Architecture reference")

    context_json = {
        "enabled": True,
        "source": "context-pack",
        "workspace_id": ws_id,
        "pack_created_at": pack.get("created_at"),
        "repo_head": pack.get("repo", {}).get("head", ""),
        "sources": sources
    }

    md_lines = ["# Contexto usado\n\n## Fontes\n"]
    for s in sources:
        md_lines.append(f"- {s['path']}")
    md_lines.append("\n## Observações\nContexto injetado via best-effort selection.")

    final_text = "== CONTEXT PACK ==\nThe following files are provided as project context:\n\n" + "\n\n".join(text_blocks) + "\n== END CONTEXT PACK ==\n"

    return {
        "enabled": True,
        "text": final_text,
        "json": context_json,
        "md": "\n".join(md_lines)
    }

def best_effort_rebuild(root_path: Path, run_dir: Path, workspace_id: str | None = None):
    try:
        res = rebuild_indexes(root_path, workspace_id)
        status = "succeeded" if res.get("ok") else "failed"
        log = f"Context index rebuild: {status}\n{res}"
    except Exception as e:
        log = f"Context index rebuild: failed\n{e}"

    if run_dir and run_dir.exists():
        (run_dir / "context_rebuild.log").write_text(log)
