import json
import datetime
from pathlib import Path

def build_manifest(workspace_id: str, root_path: Path, files_indexed: int, chunks_indexed: int, ignored_count: int, index_path: str, chunks_path: str) -> dict:
    manifest = {
        "version": 1,
        "workspace_id": workspace_id,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "root": str(root_path),
        "files_indexed": files_indexed,
        "chunks_indexed": chunks_indexed,
        "ignored_count": ignored_count,
        "index_path": index_path,
        "chunks_path": chunks_path,
        "warnings": []
    }
    return manifest
