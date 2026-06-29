import json
import os
import subprocess
import datetime
from pathlib import Path
from urllib.parse import quote

SENSITIVE_VALUE_PARTS = (".env", "litellm_master_key", "api_key", "client_secret", "private_key")
SENSITIVE_NAME_PARTS = ("key", "token", "secret", "password", "credential", "private")

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

def _build_search_index(root: Path, branch: str, head: str, out_path: Path):
    docs = []
    
    def add_doc(dtype: str, title: str, path: Path, rel_path: str, snippet: str, terms: list[str]):
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
            "snippet": snippet[:400]
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
    runs_dir = root / ".aiw" / "runs"
    if runs_dir.exists():
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
                add_doc("run", title, summary_path, str(summary_path.relative_to(root)), text[:400].replace("\n", " "), ["run", "summary", run_path.name.lower()])
                
            # index commands.log
            commands_path = run_path / "commands.log"
            if commands_path.is_file():
                text = read_text_safe(commands_path)
                add_doc("run", f"{title} (Commands)", commands_path, str(commands_path.relative_to(root)), text[:400].replace("\n", " "), ["run", "commands", "log"])

            # index tool-traces.jsonl
            traces_path = run_path / "tool-traces.jsonl"
            if traces_path.is_file():
                text = read_text_safe(traces_path)
                add_doc("run", f"{title} (Tools)", traces_path, str(traces_path.relative_to(root)), text[:400].replace("\n", " "), ["run", "tools", "traces"])
                
            # index messages.json
            msgs_path = run_path / "messages.json"
            if msgs_path.is_file():
                text = read_text_safe(msgs_path)
                add_doc("run", f"{title} (Messages)", msgs_path, str(msgs_path.relative_to(root)), text[:400].replace("\n", " "), ["run", "messages", "llm"])

    # patches
    patches_dir = root / ".aiw" / "patches"
    if patches_dir.exists():
        for ppath in patches_dir.glob("*.json"):
            if not ppath.is_file(): continue
            try:
                data = json.loads(read_text_safe(ppath))
                title = f"Patch {ppath.stem}"
                target = data.get("path", "")
                reason = data.get("reason", "")
                diff = data.get("diff", "")
                snip = (reason + " " + diff)[:400].replace("\n", " ")
                add_doc("patch", title, ppath, str(ppath.relative_to(root)), snip, ["patch", target.lower()])
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
        "document_count": len(docs),
        "documents": docs
    }
    
    out_path.write_text(json.dumps(index_data, indent=2, ensure_ascii=False))
    return index_data


def _build_context_pack(root: Path, branch: str, head: str, out_path: Path):
    docs_dir = root / "docs"
    runbooks_dir = docs_dir / "runbooks"
    arch_dir = docs_dir / "architecture"
    runs_dir = root / ".aiw" / "runs"
    patches_dir = root / ".aiw" / "patches"
    
    docs_count = len(list(docs_dir.rglob("*.md"))) if docs_dir.is_dir() else 0
    runbooks_count = len(list(runbooks_dir.glob("*.md"))) if runbooks_dir.is_dir() else 0
    arch_count = len(list(arch_dir.glob("*.md"))) if arch_dir.is_dir() else 0
    runs_count = len([p for p in runs_dir.iterdir() if p.is_dir()]) if runs_dir.is_dir() else 0
    patches_count = len(list(patches_dir.glob("*.json"))) if patches_dir.is_dir() else 0
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

def rebuild_indexes(root_path: Path) -> dict:
    ctx_dir = root_path / ".aiw" / "context"
    ctx_dir.mkdir(parents=True, exist_ok=True)
    
    branch = current_git_branch(root_path)
    head = short_git_head(root_path)
    
    idx_path = ctx_dir / "search-index.json"
    pack_path = ctx_dir / "context-pack.json"
    
    try:
        _build_search_index(root_path, branch, head, idx_path)
        _build_context_pack(root_path, branch, head, pack_path)
        return {"ok": True, "message": "Index and Context Pack rebuilt successfully."}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def get_search_index(root_path: Path) -> dict | None:
    idx_path = root_path / ".aiw" / "context" / "search-index.json"
    if not idx_path.is_file():
        return None
    try:
        return json.loads(idx_path.read_text(encoding="utf-8"))
    except:
        return None

def get_context_pack(root_path: Path) -> dict | None:
    pack_path = root_path / ".aiw" / "context" / "context-pack.json"
    if not pack_path.is_file():
        return None
    try:
        return json.loads(pack_path.read_text(encoding="utf-8"))
    except:
        return None
