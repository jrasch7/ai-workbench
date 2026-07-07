# Documentation Structure (Current)

Clean, target-aligned layout for the Provider-First AI Engineering Harness (Manus/Devin-inspired, self-hosted, full control).

## Core Living Documents
- `ARCHITECTURE.md` — Product vision + full target architecture
- `MIGRATION.md` — Current state vs target + progress
- `INDEX.md` — Navigation

## Target-Aligned Sections
- `concepts/` — Provider-First, Model Router, Agent Profiles, etc.
- `interfaces/` — Public contracts (ModelProvider, ExecutionProvider, etc.)
- `guides/` — How to add providers, profiles, experiment with the system
- `components/` — Layer descriptions (agent-runtime, provider-layer, etc.)
- `architecture/` — (mostly historical now)

## Operational
- `runbooks/` — Current operational runbooks (see historical/ subfolder for previous iterations)

## Historical / Previous Visions
Everything from earlier experiments (Hermes, Paperclip, Ralph, heavy Obsidian-centric, old monolith flows) is under `historical/` subdirectories.

**Current focus**: Provider-First (Model / Execution / Context providers), profiles, router, LLM planning + gated execution, Experiment Lab, memory, clean `aiw/` packages.

New documentation must reference the current vision in `ARCHITECTURE.md`.
