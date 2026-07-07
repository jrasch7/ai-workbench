# AIW — Target Package Structure

This directory contains the **future structure** of the AI Workbench platform.

See [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) for the complete design.

## Current Goal
Migrate from the legacy monolith toward a clean **Provider-First** architecture (inspired by Manus/Devin autonomy + full self-hosted control).

## Layout (Target)

- `providers/`
  - `model/` — OpenRouter, litellm, future
  - `execution/` — CodeAct (primary), Docker, Devcontainer (stubs + wiring)
  - `context/` — local_rag + future
- `router/` + `profiles/` — intelligent selection + agent personalities
- `agent/` + `planner/` — Iterative loop with LLM planning
- `policy/` — Gates (capability, isolation, runtime)
- `memory/` — Short/Long term (in progress)
- `experiment/` — Bench + Arena
- `queue/`, `context/`, `core/`, etc. — layers with status READMEs

See root `README.md`, `docs/ARCHITECTURE.md` and `docs/MIGRATION.md` for vision and progress.

The structure is actively being cleaned. Legacy lives in `aiw_workspace/` only as bridge. Continuação da migração: worker_loop, agent_queue thinned; CodeAct fully in aiw/. Ver docs/MIGRATION.md.
