"""Local RAG Context Provider (bridge to existing aiw_context + basic code symbol indexing via AST).

Adds repo-aware retrieval: lexical chunks + Python AST parsed symbols (functions, classes, imports, methods, assigns)
for precise queries like "onde é usada a função Y", "refatorar X", etc.
Returns structured chunks usable as 'relevant_code_snippets' by planner/loop.
Hybrid scoring (lexical + symbol + embed boost) + robust persist with mtime + version.
Always-inject friendly: richer symbols/scores for plan/replan/failure across ALL runs.
"""

import ast
import json
import os
import re
import math
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from aiw.interfaces.context_provider import ContextProvider

# Robust persist version for embed index (bump on schema changes to force rebuild)
RAG_INDEX_VERSION = "rag-v2-hybrid-symbols"


def _get_workspace_root() -> Path:
    return Path(os.environ.get("AIW_ROOT", ".")).resolve()


IGNORE_DIRS = {".git", ".aiw", "__pycache__", "node_modules", "vendor", ".venv", "venv", "site-packages", "build", "dist", ".cache"}
IGNORE_FILE_PATTERNS = {".pyc", ".pyo", ".so", ".egg"}


def _is_ignored_path(rel: str) -> bool:
    parts = Path(rel).parts
    if any(p in IGNORE_DIRS for p in parts):
        return True
    if any(rel.endswith(pat) for pat in IGNORE_FILE_PATTERNS):
        return True
    if rel.startswith(".aiw/") or "/.aiw/" in rel:
        return True
    return False


def _get_rag_embed_path(workspace_id: str) -> Path:
    """Stdlib path for persisted embed index under .aiw/workspaces/{ws}/rag/ (surgical)."""
    root = _get_workspace_root()
    ws_id = workspace_id or "aiw"
    return root / ".aiw" / "workspaces" / ws_id / "rag" / "embed_index.json"


class LocalRAGContextProvider(ContextProvider):
    """Adapter for current context pack / indexer logic + code-aware AST indexing."""

    def __init__(self):
        self._symbol_index: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        self._file_symbols: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        self._embed_index: Dict[str, List[Dict[str, Any]]] = {}  # for simple BOW embeddings (chunks+symbols)
        # Load on init if persisted embed index exists (for default ws; per-ws loaded on demand)
        try:
            self._load_embed_index("aiw")
        except Exception:
            pass

    def name(self) -> str:
        return "local_rag"

    # --- Simple stdlib-only local embeddings (bag-of-words + cosine) for deeper RAG ---
    # Token-based over chunks + symbols. Indexed on build(). No external deps.
    def _tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        # alphanum + _ identifiers, min len 3 chars for signal
        return re.findall(r'[a-zA-Z_][a-zA-Z0-9_]{2,}', text.lower())

    def _counter_from_text(self, text: str) -> Counter:
        return Counter(self._tokenize(text))

    def _cosine(self, c1: Counter, c2: Counter) -> float:
        if not c1 or not c2:
            return 0.0
        inter = set(c1.keys()) & set(c2.keys())
        dot = sum(c1[t] * c2[t] for t in inter)
        n1 = math.sqrt(sum(v * v for v in c1.values()))
        n2 = math.sqrt(sum(v * v for v in c2.values()))
        if n1 == 0.0 or n2 == 0.0:
            return 0.0
        return dot / (n1 * n2)

    def _save_embed_index(self, workspace_id: str) -> None:
        """Persist simple BOW embed index (vec as dict for json) to .aiw/.../rag/embed_index.json. Stdlib only.
        Robust: stores meta with source chunks_mtime for auto-rebuild detection on change/missing."""
        ws_id = workspace_id or "aiw"
        if ws_id not in self._embed_index or not self._embed_index.get(ws_id):
            return
        p = _get_rag_embed_path(ws_id)
        p.parent.mkdir(parents=True, exist_ok=True)
        serial = []
        for e in self._embed_index[ws_id]:
            serial.append({
                "vec": dict(e.get("vec", {})),
                "text": e.get("text", ""),
                "meta": e.get("meta", {}),
            })
        # compute source sig for change detection (chunks mtime)
        chunks_mtime = 0.0
        try:
            from aiw_context.search import get_chunks_path
            cp = get_chunks_path(ws_id)
            if cp.exists():
                chunks_mtime = cp.stat().st_mtime
        except Exception:
            pass
        payload = {
            "meta": {
                "chunks_mtime": chunks_mtime,
                "entry_count": len(serial),
                "saved_at": __import__("time").time(),
                "version": RAG_INDEX_VERSION,
            },
            "entries": serial,
        }
        try:
            p.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass  # best-effort persist

    def _load_embed_index(self, workspace_id: str) -> bool:
        """Load persisted embed index if file exists (on init or before build/retrieve). Reload on demand."""
        ws_id = workspace_id or "aiw"
        p = _get_rag_embed_path(ws_id)
        if not p.exists():
            return False
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, list):
                # backward compat with prior step3 persist format
                entries_data = data or []
                meta = {}
            else:
                entries_data = data.get("entries", []) or []
                meta = data.get("meta", {}) or {}
            # version check for robust: if mismatch force stale rebuild on next use
            if meta.get("version") and meta.get("version") != RAG_INDEX_VERSION:
                meta["_version_mismatch"] = True
            entries = []
            for s in entries_data:
                vec = Counter(s.get("vec", {}))
                entries.append({
                    "vec": vec,
                    "text": s.get("text", ""),
                    "meta": s.get("meta", {}),
                })
            self._embed_index[ws_id] = entries
            if not hasattr(self, "_embed_meta"):
                self._embed_meta = {}
            self._embed_meta[ws_id] = meta
            return True
        except Exception:
            return False

    def _get_chunks_mtime(self, workspace_id: str) -> float:
        """Helper for change detection: mtime of source chunks (if present)."""
        try:
            from aiw_context.search import get_chunks_path
            cp = get_chunks_path(workspace_id or "aiw")
            if cp.exists():
                return cp.stat().st_mtime
        except Exception:
            pass
        return 0.0

    def _is_embed_stale_or_missing(self, workspace_id: str) -> bool:
        """Auto-rebuild trigger: missing index, no in-mem, or chunks source changed since last persist.
        Robust: also version mismatch forces rebuild (persist mtime + version)."""
        ws_id = workspace_id or "aiw"
        p = _get_rag_embed_path(ws_id)
        if not p.exists() or ws_id not in self._embed_index or not self._embed_index.get(ws_id):
            return True
        try:
            cur = self._get_chunks_mtime(ws_id)
            stored_meta = getattr(self, "_embed_meta", {}).get(ws_id, {}) or {}
            stored = stored_meta.get("chunks_mtime", 0.0)
            if cur > stored + 1e-6:
                return True
            if stored_meta.get("_version_mismatch") or (stored_meta.get("version") and stored_meta.get("version") != RAG_INDEX_VERSION):
                return True
        except Exception:
            # on any sig error treat as stale -> rebuild
            return True
        return False

    def _build_embedding_index(self, workspace_id: str) -> int:
        """Build lightweight BOW embedding index over symbols (already parsed) + chunks.jsonl.
        Called from index() / build path. Bounded to keep surgical + fast."""
        ws_id = workspace_id or "aiw"
        root = _get_workspace_root()
        entries: List[Dict[str, Any]] = []

        # From AST symbols (rich for code queries: funcs w/ sig, classes, methods qualified, assigns)
        if ws_id in self._file_symbols:
            for rel, syms in self._file_symbols.get(ws_id, {}).items():
                for s in syms:
                    sig = s.get("sig", "")
                    txt = f"{s.get('kind','')} {s.get('name','')} {sig} {s.get('docstring','')} path:{s.get('path','')}"
                    vec = self._counter_from_text(txt)
                    m = {
                        "path": s.get("path"),
                        "kind": s.get("kind"),
                        "symbol": s.get("name"),
                        "line": s.get("line"),
                        "source": "symbol_bow",
                    }
                    if sig:
                        m["sig"] = sig
                    if s.get("class"):
                        m["class"] = s.get("class")
                    m["rag_version"] = RAG_INDEX_VERSION
                    entries.append({
                        "vec": vec,
                        "text": txt[:350],
                        "meta": m,
                    })

        # From existing lexical chunks (general file content chunks for broader context)
        try:
            from aiw_context.search import get_chunks_path
            cp = get_chunks_path(ws_id)
            if cp.exists():
                import json as _json
                with open(cp, "r", encoding="utf-8", errors="replace") as f:
                    for i, line in enumerate(f):
                        if i > 400:  # surgical bound for demo/index perf (no heavy)
                            break
                        if not line.strip():
                            continue
                        try:
                            ch = _json.loads(line)
                            txt = (ch.get("text") or "")[:600]
                            if not txt.strip():
                                continue
                            vec = self._counter_from_text(txt)
                            m = {
                                "path": ch.get("path"),
                                "start_line": ch.get("start_line"),
                                "end_line": ch.get("end_line"),
                                "chunk_id": ch.get("chunk_id"),
                                "source": "chunk_bow",
                                "rag_version": RAG_INDEX_VERSION,
                            }
                            entries.append({
                                "vec": vec,
                                "text": txt[:400],
                                "meta": m,
                            })
                        except Exception:
                            continue
        except Exception:
            pass

        self._embed_index[ws_id] = entries
        try:
            self._save_embed_index(ws_id)
        except Exception:
            pass
        return len(entries)

    def _retrieve_with_embeddings(self, query: str, workspace_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Pure embedding retrieval using BOW cosine over indexed chunks+symbols.
        Auto-reloads from persist or rebuilds if missing/changed (robust persist+reload)."""
        ws_id = workspace_id or "aiw"
        if self._is_embed_stale_or_missing(ws_id):
            if not self._load_embed_index(ws_id) or self._is_embed_stale_or_missing(ws_id):
                self._build_embedding_index(ws_id)
        qvec = self._counter_from_text(query or "")
        scored: List[Dict[str, Any]] = []
        for e in self._embed_index.get(ws_id, []):
            sim = self._cosine(qvec, e.get("vec", Counter()))
            if sim > 0.005:
                m = dict(e.get("meta", {}))
                # hybrid: base embed score + boost for symbols
                base = round(8.0 * sim, 3)
                is_sym = "symbol" in str(m.get("source", "")) or m.get("kind") in ("function", "class", "method")
                hyb = base + (1.5 if is_sym else 0.0)
                m["score"] = round(hyb, 3)
                m["embedding_score"] = round(sim, 4)
                m["hybrid_score"] = round(sim * (1.2 if is_sym else 1.0), 4)
                m["snippet"] = e.get("text", "")[:450]
                m["content"] = m["snippet"]
                m["source"] = m.get("source", "bow_embed")
                scored.append(m)
        scored.sort(key=lambda x: float(x.get("score", 0)), reverse=True)
        return scored[:limit]

    def _build_symbol_index(self, workspace_id: str) -> Dict[str, Any]:
        """Improved code indexing: stdlib ast for funcs (w/ sig), classes, methods (qualified), imports, top assigns.
        Better symbols for hybrid RAG + precise planner injection."""
        root = _get_workspace_root()
        ws_id = workspace_id or "aiw"
        sym_index: Dict[str, List[Dict[str, Any]]] = {}
        file_syms: Dict[str, List[Dict[str, Any]]] = {}

        py_files = 0
        for py_path in root.rglob("*.py"):
            try:
                rel = str(py_path.relative_to(root)).replace("\\", "/")
            except Exception:
                continue
            if _is_ignored_path(rel):
                continue
            try:
                src = py_path.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(src, filename=rel)
                symbols: List[Dict[str, Any]] = []
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        doc = ast.get_docstring(node) or ""
                        args = [a.arg for a in getattr(node.args, "args", [])]
                        sig = f"({', '.join(args)})" if args else "()"
                        symbols.append({
                            "kind": "function",
                            "name": node.name,
                            "sig": sig,
                            "line": getattr(node, "lineno", 0),
                            "end_line": getattr(node, "end_lineno", getattr(node, "lineno", 0)),
                            "path": rel,
                            "docstring": doc[:200] if doc else "",
                        })
                    elif isinstance(node, ast.ClassDef):
                        doc = ast.get_docstring(node) or ""
                        symbols.append({
                            "kind": "class",
                            "name": node.name,
                            "line": getattr(node, "lineno", 0),
                            "end_line": getattr(node, "end_lineno", getattr(node, "lineno", 0)),
                            "path": rel,
                            "docstring": doc[:200] if doc else "",
                        })
                        # methods inside class -> qualified for richer symbol use
                        for b in getattr(node, "body", []):
                            if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                mdoc = ast.get_docstring(b) or ""
                                margs = [a.arg for a in getattr(b.args, "args", [])]
                                msig = f"({', '.join(margs)})" if margs else "()"
                                qname = f"{node.name}.{b.name}"
                                symbols.append({
                                    "kind": "method",
                                    "name": qname,
                                    "sig": msig,
                                    "line": getattr(b, "lineno", 0),
                                    "end_line": getattr(b, "end_lineno", getattr(b, "lineno", 0)),
                                    "path": rel,
                                    "docstring": mdoc[:200] if mdoc else "",
                                    "class": node.name,
                                })
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            symbols.append({
                                "kind": "import",
                                "name": alias.name,
                                "line": getattr(node, "lineno", 0),
                                "path": rel,
                            })
                    elif isinstance(node, ast.ImportFrom):
                        mod = node.module or ""
                        for alias in node.names:
                            symbols.append({
                                "kind": "import",
                                "name": alias.name,
                                "module": mod,
                                "line": getattr(node, "lineno", 0),
                                "path": rel,
                            })
                    elif isinstance(node, ast.Assign):
                        # top-level assigns for richer symbols (consts, vars)
                        for t in node.targets:
                            if isinstance(t, ast.Name):
                                symbols.append({
                                    "kind": "assign",
                                    "name": t.id,
                                    "line": getattr(node, "lineno", 0),
                                    "path": rel,
                                })
                if symbols:
                    file_syms[rel] = symbols
                    for s in symbols:
                        if s["kind"] in ("function", "class", "method"):
                            sym_index.setdefault(s["name"], []).append(s)
                py_files += 1
            except Exception:
                continue

        self._symbol_index[ws_id] = sym_index
        self._file_symbols[ws_id] = file_syms
        # also (re)build simple embed index when symbols built (index-on-build)
        try:
            self._build_embedding_index(ws_id)
        except Exception:
            pass
        return {"files_scanned": py_files, "unique_symbols": len(sym_index)}

    def _retrieve_code_aware(self, query: str, workspace_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Symbol + usage retrieval for code queries (e.g. 'onde é usada a função foo')."""
        ws_id = workspace_id or "aiw"
        if ws_id not in self._symbol_index:
            self._build_symbol_index(ws_id)

        idx = self._symbol_index.get(ws_id, {})
        q = (query or "").lower()
        results: List[Dict[str, Any]] = []

        # Extract candidate identifiers from query (PT/EN aware)
        candidates: List[str] = []
        for m in re.finditer(r'(?:função|function|def |class |método|method|usada|used|chama|call)\s+([A-Za-z_][A-Za-z0-9_]*)', q):
            candidates.append(m.group(1))
        for w in re.findall(r'[A-Za-z_][A-Za-z0-9_]{2,}', q):
            if len(w) > 2 and w not in candidates:
                candidates.append(w)

        root = _get_workspace_root()
        seen = set()

        for cand in candidates[:8]:
            locs = idx.get(cand, [])
            for loc in locs[:2]:
                key = (loc.get("path"), loc.get("name"), loc.get("line"))
                if key in seen:
                    continue
                seen.add(key)
                # fetch snippet around definition
                snippet = loc.get("docstring", "")
                try:
                    p = root / loc["path"]
                    lines = p.read_text(encoding="utf-8", errors="replace").splitlines(keepends=False)
                    ln = max(0, int(loc.get("line", 1)) - 1)
                    start = max(0, ln - 1)
                    end = min(len(lines), ln + 6)
                    snippet = "\n".join(lines[start:end])
                except Exception:
                    pass
                results.append({
                    "path": loc.get("path"),
                    "score": 12.0,
                    "kind": loc.get("kind"),
                    "symbol": cand,
                    "line": loc.get("line"),
                    "snippet": snippet[:650],
                    "content": snippet[:650],
                    "source": "code_symbol_ast",
                })

        # For usage queries ("onde", "usada", "where used", "calls"), add call/reference sites via simple scan
        is_usage_q = any(x in q for x in ["onde", "usada", "usos", "used", "reference", "chama", "calls", "call site", "invoc"])
        if is_usage_q and candidates:
            for cand in candidates[:3]:
                try:
                    for py_path in list(root.rglob("*.py"))[:80]:  # bounded scan for surgical perf
                        rel = str(py_path.relative_to(root)).replace("\\", "/")
                        if _is_ignored_path(rel):
                            continue
                        txt = py_path.read_text(encoding="utf-8", errors="replace")
                        if cand not in txt:
                            continue
                        # skip pure defs (already covered by symbol)
                        lines = txt.splitlines(keepends=False)
                        match_lines = []
                        for i, ln in enumerate(lines):
                            if cand in ln and "def " + cand not in ln and "class " + cand not in ln:
                                match_lines.append(i + 1)
                        if match_lines:
                            key = (rel, cand, "usage")
                            if key in seen:
                                continue
                            seen.add(key)
                            m = match_lines[0]
                            start = max(0, m - 2)
                            end = min(len(lines), m + 2)
                            snip = "\n".join(lines[start:end])
                            results.append({
                                "path": rel,
                                "score": 6.0,
                                "kind": "usage",
                                "symbol": cand,
                                "line": m,
                                "lines": match_lines[:3],
                                "snippet": snip[:450],
                                "content": snip[:450],
                                "source": "code_usage_scan",
                            })
                            if len(results) > limit + 3:
                                break
                except Exception:
                    continue
                if len(results) > limit + 3:
                    break

        # dedup + limit
        uniq = []
        seen2 = set()
        for r in results:
            k = (r.get("path"), r.get("symbol"), r.get("kind"), r.get("line"))
            if k not in seen2:
                seen2.add(k)
                uniq.append(r)
        uniq.sort(key=lambda x: x.get("score", 0), reverse=True)
        return uniq[:limit]

    def retrieve(self, query: str, workspace_id: str, **kwargs) -> List[Dict[str, Any]]:
        """Hybrid retrieve: lexical chunks + AST symbols (improved w/ sigs/methods) + BOW embeddings (combined).
        ALWAYS uses embeddings (use_embeddings default True) + hybrid scoring (lexical+symbol+embed+hybrid_score).
        Richer for planner/loop injection in plan/replan/failure for ALL runs.
        """
        limit = int(kwargs.get("limit", kwargs.get("max_results", 8)))
        # Always prefer embeddings + hybrid (remove partial; explicit False to disable rare)
        use_embed = kwargs.get("use_embeddings", None)
        if use_embed is None:
            use_embed = kwargs.get("embedding_support", True)
        use_embed = bool(use_embed)
        persist = bool(kwargs.get("persist", False))
        results: List[Dict[str, Any]] = []

        # 1. Lexical from existing chunks (general + code text)
        try:
            from aiw_context.search import search_context
            sres = search_context(workspace_id, query, limit=limit)
            for r in (sres.get("results", []) if isinstance(sres, dict) else []):
                r2 = dict(r)
                r2.setdefault("source", "lexical_chunks")
                if "content" not in r2 and "snippet" in r2:
                    r2["content"] = r2["snippet"]
                results.append(r2)
        except Exception:
            pass

        # 2. Code-aware AST symbols + usages (key for repo-aware refactors; now richer)
        try:
            code_res = self._retrieve_code_aware(query, workspace_id, limit=max(3, limit // 2))
            results.extend(code_res)
        except Exception:
            pass

        # 3. Embedding layer (BOW+cosine + hybrid) - ALWAYS combined for deeper context (unless explicit disable)
        if use_embed:
            try:
                embed_res = self._retrieve_with_embeddings(query, workspace_id, limit=max(3, limit // 3))
                results.extend(embed_res)
            except Exception:
                pass

        # Combine: lexical + embedding similarity (boost scores for overlap, prefer hybrid)
        # Dedup by (path, symbol/line-ish) and compute combined + hybrid_score
        merged: Dict[tuple, Dict[str, Any]] = {}
        for r in results:
            p = r.get("path") or ""
            key_sym = r.get("symbol") or r.get("chunk_id") or ""
            key_ln = r.get("line") or r.get("start_line") or ""
            k = (p, key_sym, key_ln)
            if k not in merged:
                merged[k] = dict(r)
            else:
                ex = merged[k]
                # richer hybrid combine: lexical base + embed + hybrid boost
                ls = float(ex.get("score", 0.0))
                es = float(r.get("embedding_score", 0.0)) or float(r.get("score", 0.0)) * 0.1
                hs = float(r.get("hybrid_score", 0.0))
                comb = ls + (es * 6.0 if "embedding_score" in r or "bow" in str(r.get("source", "")) else es)
                if hs:
                    comb = max(comb, hs * 9.0)
                ex["score"] = round(comb, 3)
                if r.get("embedding_score"):
                    ex["embedding_score"] = r.get("embedding_score")
                if r.get("hybrid_score"):
                    ex["hybrid_score"] = r.get("hybrid_score")
                ex_src = str(ex.get("source", ""))
                r_src = str(r.get("source", ""))
                if "embed" in r_src or "bow" in r_src:
                    ex["source"] = (ex_src + "+embed") if ex_src and "embed" not in ex_src else (r_src if not ex_src else ex_src)
        results = list(merged.values())
        # sort + trim (now with embedding boost + hybrid in richer scoring)
        results.sort(key=lambda x: float(x.get("score", 0.0)), reverse=True)
        if persist and use_embed:
            try:
                self._save_embed_index(workspace_id or "aiw")
            except Exception:
                pass
        return results[:limit]

    def index(self, workspace_id: str, **kwargs) -> Dict[str, Any]:
        """(Re)build symbol index (richer: sigs/methods/assigns) + embed index + delegate to chunks. Persists with mtime+version robust. Always for planner/loop use."""
        try:
            persist = kwargs.get("persist", True)
            stats = self._build_symbol_index(workspace_id)
            embed_count = len(self._embed_index.get(workspace_id or "aiw", []))
            chunk_stats = {}
            try:
                from aiw_context.indexer import build_context_index
                chunk_stats = build_context_index(workspace_id) or {}
            except Exception:
                pass
            if persist:
                try:
                    self._save_embed_index(workspace_id or "aiw")
                except Exception:
                    pass
            return {
                "ok": True,
                "provider": self.name(),
                "symbol_stats": stats,
                "embed_count": embed_count,
                "embedding": "simple_bow_stdlib_counter_cosine",
                "chunk_stats": chunk_stats,
                "workspace_id": workspace_id,
                "persisted": bool(persist),
            }
        except Exception as e:
            return {"ok": False, "error": str(e), "provider": self.name()}

    def describe(self) -> Dict[str, Any]:
        return {
            "name": self.name(),
            "type": "local_filesystem_rag",
            "description": "Richer: improved AST symbols (funcs w/sig, methods qualified, assigns) + lexical + BOW hybrid scoring (hybrid_score). Robust persist mtime+version (RAG_INDEX_VERSION) auto-rebuild. Chunks/symbols ALWAYS injected in plan/replan/failure for ALL runs (no gates). Richer embed scores (min/max/avg, hybrid) used in planner/loop.",
            "features": ["lexical_chunks", "ast_python_symbols_improved", "usage_search", "simple_bow_embeddings", "hybrid_lexical_embed_symbol", "hybrid_score", "on_disk_persist_mtime_version", "auto_rebuild_on_change_version", "always_use_embeddings", "embed_score_failure_replan_all_runs"],
            "embedding": "token_bag_of_words + cosine (stdlib collections+math, index-on-build, persisted w/ version, auto-rebuild stale)",
            "code_indexing": "stdlib ast improved (funcs sigs, class methods qualified, assigns; no external deps)",
            "persist": ".aiw/workspaces/{ws}/rag/embed_index.json (json+meta for mtime+version, stdlib)",
            "index_version": RAG_INDEX_VERSION,
        }
