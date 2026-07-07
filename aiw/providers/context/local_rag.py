"""Local RAG Context Provider (bridge to existing aiw_context)."""

from aiw.interfaces.context_provider import ContextProvider
from typing import Any, Dict, List


class LocalRAGContextProvider(ContextProvider):
    """Adapter for current context pack / indexer logic."""

    def name(self) -> str:
        return "local_rag"

    def retrieve(self, query: str, workspace_id: str, **kwargs) -> List[Dict[str, Any]]:
        # Bridge to existing
        try:
            from aiw_context.search import search_context
            results = search_context(workspace_id, query, **kwargs)
            return results.get("results", []) if isinstance(results, dict) else []
        except Exception:
            return []

    def describe(self) -> Dict[str, Any]:
        return {
            "name": self.name(),
            "type": "local_filesystem_rag",
            "description": "Uses existing context index and packs",
        }
