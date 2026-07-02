import hashlib
import json
from pathlib import Path

def chunk_text(text: str, path: str, max_chars: int = 4000, overlap: int = 200) -> list[dict]:
    """
    Splits text into chunks by characters, respecting line boundaries where possible.
    Returns a list of chunk dictionaries.
    """
    if not text:
        return []

    lines = text.splitlines(keepends=True)
    chunks = []
    
    current_chunk = []
    current_length = 0
    start_line = 1
    current_line = 1
    
    for line in lines:
        line_len = len(line)
        if current_length + line_len > max_chars and current_length > 0:
            # Finalize current chunk
            chunk_text = "".join(current_chunk)
            chunk_id = hashlib.sha256(chunk_text.encode('utf-8')).hexdigest()[:12]
            
            chunks.append({
                "chunk_id": chunk_id,
                "path": path,
                "start_line": start_line,
                "end_line": current_line - 1,
                "text": chunk_text,
                "token_estimate": len(chunk_text) // 4,
                "sha256": chunk_id
            })
            
            # Start new chunk with overlap (if overlap is feasible based on lines)
            overlap_length = 0
            overlap_lines = []
            for ol in reversed(current_chunk):
                if overlap_length + len(ol) > overlap:
                    break
                overlap_lines.insert(0, ol)
                overlap_length += len(ol)
                
            current_chunk = overlap_lines + [line]
            current_length = sum(len(l) for l in current_chunk)
            start_line = current_line - len(overlap_lines)
        else:
            current_chunk.append(line)
            current_length += line_len
            
        current_line += 1
        
    # Add remainder
    if current_chunk:
        chunk_text = "".join(current_chunk)
        chunk_id = hashlib.sha256(chunk_text.encode('utf-8')).hexdigest()[:12]
        chunks.append({
            "chunk_id": chunk_id,
            "path": path,
            "start_line": start_line,
            "end_line": current_line - 1,
            "text": chunk_text,
            "token_estimate": len(chunk_text) // 4,
            "sha256": chunk_id
        })
        
    return chunks
