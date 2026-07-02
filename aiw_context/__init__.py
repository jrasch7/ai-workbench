"""
AIW Context Pack module.
Handles creation and reading of context pack and search index cache.
"""
from .indexer import (
    rebuild_indexes,
    get_search_index,
    get_context_pack,
    build_agent_context,
    best_effort_rebuild,
    normalize_workspace_id,
    workspace_context_dir,
    workspace_runs_dirs,
    workspace_patches_dirs,
    build_context_index,
)
from .search import search_context

__all__ = [
    "rebuild_indexes",
    "get_search_index",
    "get_context_pack",
    "build_agent_context",
    "best_effort_rebuild",
    "normalize_workspace_id",
    "workspace_context_dir",
    "workspace_runs_dirs",
    "workspace_patches_dirs",
    "build_context_index",
    "search_context",
]
