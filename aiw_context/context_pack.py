import json
import uuid
import datetime
from pathlib import Path
import os
from .search import search_context
from .indexer import workspace_context_dir, normalize_workspace_id

def _context_pack_dir(workspace_id: str) -> Path:
    ws_id = normalize_workspace_id(workspace_id)
    root = Path(os.environ.get("AIW_ROOT", ".")).resolve()
    return root / ".aiw" / "workspaces" / ws_id / "context-packs"

def build_context_pack(
    workspace_id: str,
    query: str,
    source_id: str | None = None,
    max_chunks: int = 12,
    max_chars: int = 24000,
    source_kind: str = "query"
) -> dict:
    """
    Builds a context pack by querying the local RAG index and selecting chunks 
    within the budget constraints.
    """
    # Fetch results from search
    # We ask for a bit more than max_chunks in case we need to filter or truncate
    search_res = search_context(workspace_id, query, limit=max_chunks * 2)
    results = search_res.get("results", [])
    
    pack_id = f"ctx-{uuid.uuid4().hex[:8]}"
    
    selected_chunks = []
    used_chunks = 0
    used_chars = 0
    
    for r in results:
        if used_chunks >= max_chunks:
            break
            
        text = r.get("snippet", "")
        if "text" in r:
            text = r["text"] # full text if available
            
        # truncate if this chunk alone is too big
        if len(text) > max_chars:
            text = text[:max_chars]
            
        # check if adding this chunk exceeds budget
        if used_chars + len(text) > max_chars:
            break
            
        chunk_info = {
            "chunk_id": r.get("chunk_id", ""),
            "path": r.get("path", ""),
            "score": r.get("score", 0.0),
            "start_line": r.get("start_line", 0),
            "end_line": r.get("end_line", 0),
            "char_count": len(text),
            "snippet": text[:500] + ("..." if len(text) > 500 else ""),
            "text": text
        }
        
        selected_chunks.append(chunk_info)
        used_chunks += 1
        used_chars += len(text)
        
    return {
        "version": 1,
        "workspace_id": normalize_workspace_id(workspace_id),
        "pack_id": pack_id,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": {
            "kind": source_kind,
            "source_id": source_id or pack_id,
            "query": query
        },
        "budget": {
            "max_chunks": max_chunks,
            "max_chars": max_chars,
            "used_chunks": used_chunks,
            "used_chars": used_chars,
            "estimated_tokens": used_chars // 4
        },
        "selection": {
            "strategy": "lexical_score_v1",
            "results_considered": len(results),
            "results_selected": used_chunks
        },
        "chunks": selected_chunks,
        "warnings": []
    }

def build_context_pack_from_text(
    workspace_id: str,
    title: str,
    body: str,
    source_id: str | None = None,
    max_chunks: int = 12,
    max_chars: int = 24000,
) -> dict:
    """Builds a context pack by using text title + body as the query."""
    query = f"{title} {body}"
    return build_context_pack(
        workspace_id=workspace_id,
        query=query[:2000],  # cap query length for search
        source_id=source_id,
        max_chunks=max_chunks,
        max_chars=max_chars,
        source_kind="text"
    )

def write_context_pack(workspace_id: str, context_pack: dict) -> dict:
    """
    Saves the context pack to artifacts.
    """
    pack_id = context_pack["pack_id"]
    base_dir = _context_pack_dir(workspace_id)
    pack_dir = base_dir / pack_id
    pack_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = pack_dir / "context-pack.json"
    md_path = pack_dir / "context-pack.md"
    
    # Write JSON
    json_path.write_text(json.dumps(context_pack, indent=2, ensure_ascii=False))
    
    # Write Markdown
    md_lines = [
        "# AIW Context Pack\n",
        "## Source\n",
        f"**Kind:** {context_pack['source']['kind']}\n",
        f"**Query/Text:** {context_pack['source']['query'][:200]}...\n",
        "## Budget\n",
        f"- Used chunks: {context_pack['budget']['used_chunks']} / {context_pack['budget']['max_chunks']}",
        f"- Used chars: {context_pack['budget']['used_chars']} / {context_pack['budget']['max_chars']}",
        f"- Estimated tokens: {context_pack['budget']['estimated_tokens']}\n",
        "## Selected Context\n"
    ]
    
    for i, chunk in enumerate(context_pack.get("chunks", []), 1):
        md_lines.append(f"### {i}. {chunk['path']}:L{chunk['start_line']}-L{chunk['end_line']}\n")
        md_lines.append("```text")
        md_lines.append(chunk.get("text", ""))
        md_lines.append("```\n")
        
    if context_pack.get("warnings"):
        md_lines.append("## Warnings\n")
        for w in context_pack["warnings"]:
            md_lines.append(f"- {w}")
            
    md_path.write_text("\n".join(md_lines))
    
    return {
        "pack_dir": str(pack_dir),
        "json_path": str(json_path),
        "markdown_path": str(md_path)
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build context pack")
    parser.add_argument("--workspace", default="aiw", help="Workspace ID")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--max-chunks", type=int, default=8, help="Max chunks")
    parser.add_argument("--max-chars", type=int, default=24000, help="Max chars")
    args = parser.parse_args()
    
    pack = build_context_pack(args.workspace, args.query, max_chunks=args.max_chunks, max_chars=args.max_chars)
    written = write_context_pack(args.workspace, pack)
    print(f"Context Pack created: {pack['pack_id']}")
    print(f"JSON: {written['json_path']}")
    print(f"MD: {written['markdown_path']}")
