# Context Layer

Part of the Provider-First architecture.

**Role:** Context Providers (RAG, Git history, project docs, external sources) that supply relevant information to the agent.

**Current status (2026-07):** 
- Basic local_rag provider in `providers/context/`.
- Integration starting in agent loop and memory.

See:
- `../providers/context/`
- docs/concepts/provider-first.md
- docs/guides/adding-context-provider.md
- docs/ARCHITECTURE.md
