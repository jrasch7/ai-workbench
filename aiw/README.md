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
  - `queue/`: AgentQueue (disk-backed for durability) + PersistentAgentWorker for 24/7 daemon (bg threads, queue intake, checkpoint recovery for persistent runs). Reexports start_daemon_worker etc. See __init__.py for usage.

See root `README.md`, `docs/ARCHITECTURE.md` and `docs/MIGRATION.md` for vision and progress.

The structure is actively being cleaned. Legacy lives in `aiw_workspace/` only as bridge. Continuação da migração: worker_loop, agent_queue thinned; CodeAct fully in aiw/. Ver docs/MIGRATION.md.

Daemon 24/7: use cockpit "Start Daemon (bg persistent)", `python -c 'from aiw.queue import start_daemon_worker; start_daemon_worker()'`, `AIW_PERSISTENT_MAX_ITERATIONS=0`, resume via run_id. Fluxo completo em docs. Mission: `aiw mission run "Título" "Tarefa"`, múltiplos runs + approvals + queue tie-in. Cockpit é UI principal (perfis, OpenRouter, trace, apply, daemons, missões).

Estado (2026-07-08 pós batches): core aiw/ primário (loop, providers, policy, queue/worker, mission, patch, profiles workspace), ~31 legacy como delegates finos. Exec real + auto-PR + pesquisa + persist ckpt + 24/7 production-ready. Ver docs/MIGRATION.md para análise fresca + próximos 5 passos.

## Exemplo completo missão real (Step 5 E2E verificado)
```bash
# via CLI (aiw mission wrapper + daemon)
python -c '
from aiw.mission import Mission
m = Mission.create("aiw", "Refator missão E2E", "editar .aiw/generated/demo.py + validar py_compile + auto PR")
print(m.enqueue())
d = m.start_run(persistent=True, execute=True, confirm=True, max_iterations=2)
print("daemon+mission:", d)
print("status:", m.status())
'
# E2E completo exercitado em smoke:
# create_mission -> enqueue_mission_task -> start_persistent_agent_daemon(mission_id) ->
# run_agent (persistent, execute+confirm trusted) com editar real (file_write/project_patch em .aiw/gen seguro) + validate ->
# auto_pr interno (detect validate success) + explicit create_pr(preview_only=False, autonomous_persistent=True) com policy relax para aiw trusted ->
# + web_fetch(..., actions=["follow","extract"]) + LocalRAGProvider retrieve(use_embeddings=True)
# Verificação: _test_full_mission_daemon_e2e() -> ok, regression smoke full, preview_only=False do_real path (mocks gh/push seguros), import limpo.
# systemd example atualizado em MIGRATION (inclui --mission flows via cockpit/queue).
```
Use `./scripts/aiw-agent-loop-regression-smoke --workspace aiw` para smoke completo (agora inclui step5).
