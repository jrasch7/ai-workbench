import json
import os
from pathlib import Path

def get_chunks_path(workspace_id: str) -> Path:
    from .indexer import workspace_context_dir
    root = Path(os.environ.get("AIW_ROOT", ".")).resolve()
    return workspace_context_dir(root, workspace_id) / "chunks.jsonl"

def search_context(workspace_id: str, query: str, limit: int = 10) -> dict:
    """
    Performs a simple lexical search over the local RAG index (chunks).
    """
    chunks_file = get_chunks_path(workspace_id)
    if not chunks_file.exists():
        return {"query": query, "results": []}

    query_terms = [t.lower() for t in query.split() if len(t) > 2]
    if not query_terms:
        # Fallback if query is too short
        query_terms = [query.lower()]

    scored_results = []
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                chunk = json.loads(line)
            except:
                continue
                
            text = chunk.get("text", "").lower()
            path = chunk.get("path", "").lower()
            
            score = 0.0
            
            # Simple scoring
            for term in query_terms:
                if term in text:
                    score += 1.0 + (text.count(term) * 0.1)
                if term in path:
                    score += 2.0  # Bonus for path match
                    
            if score > 0:
                chunk_result = {
                    "chunk_id": chunk.get("chunk_id"),
                    "path": chunk.get("path"),
                    "score": score,
                    "start_line": chunk.get("start_line"),
                    "end_line": chunk.get("end_line"),
                    "snippet": chunk.get("text")[:500] + ("..." if len(chunk.get("text", "")) > 500 else "")
                }
                scored_results.append(chunk_result)
                
    # Sort by score descending
    scored_results.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "query": query,
        "results": scored_results[:limit]
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Search local RAG index")
    parser.add_argument("--workspace", default="aiw", help="Workspace ID")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--limit", type=int, default=10, help="Max results")
    args = parser.parse_args()
    
    res = search_context(args.workspace, args.query, args.limit)
    print(json.dumps(res, indent=2, ensure_ascii=False))
