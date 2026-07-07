# AIW Migration Plan

This document tracks the reorganization from the current state to the target architecture defined in `ARCHITECTURE.md`.

## Phase 1 — Documentation & Structure (Done)
- [x] Create `docs/ARCHITECTURE.md` (Provider-First, 3 provider types, Model Router, Agent Profiles, Experiment Lab)
- [x] Create target `aiw/` package skeleton (core, providers/*, policy, profiles, router, agent, etc.)
- [x] Isolate `aiw_langgraph` into `experiments/`
- [x] Add deprecation/README notes to legacy packages
- [x] Update root `README.md`, runbooks index, add STRUCTURE.md, INDEX.md, CONTRIBUTING.md, DEVELOPMENT.md
- [x] Move historical docs to subdirs, aggressive cleanup

## Phase 2 — Interfaces & Registries (In Progress)
- [x] Define public interfaces in `aiw/interfaces/` (matching docs)
- [x] Implement basic Provider registries (model/execution/context)
- [x] Introduce Model Provider abstraction (stubs + litellm adapter)
- [ ] Full Model Provider impls

## Phase 3 — Core Layers (In Progress)
- [x] Extract Policy / Isolation / Capabilities into `aiw/policy/`
- [x] Bridges/delegation from legacy (capability_registry, execution_provider, etc.)
- [x] Build initial Model Router (profile-aware, AUTO)
- [x] Agent Profiles loader + integration in loop
- [x] LLMPlanner + real model_prov.generate path in agent loop (openrouter)
- [x] aiw/agent/iterative_loop primary with thin delegate in aiw_workspace
- [x] Runtime Iterativo Real: Loop Iterativo do Agente agora executa múltiplas iterações, re-planeja com resultados, usa provedores de execução de verdade (dry + execute).
- [x] Docker/devcontainer adapters improved (2).
- [x] Memory layer started + loop integration (3).
- [x] Tools improved + wired (4).
- [x] More mover: aiw/queue + thin delegates (5). CodeAct migrated (sandbox logic to aiw/providers/execution), worker_loop and agent_queue thinned to delegates. Updated registry, bridge, scripts, __init__. reexports. aiw/queue now has create delegate.
- [x] Continued migration: more thin delegates, legacy code moved to aiw/ where possible (execution, queue).
- [ ] Full autonomous non-dry execution + production adapters.

## Phase 4 — Agent & Profiles (In Progress)
- [x] Refactor `agent_iterative_loop` to use new aiw/ (imports for policy, router, profiles, providers)
- [x] Profile drives cap, exec, router decision
- [x] OpenRouter registered + chosen via router for profiles that allow it; tested in loop
- [x] Extract primary to `aiw/agent/`, more thin-delegates + reexports (Round 2)
- [x] Add docker/devcontainer Execution Providers (priority 2) + profiles/runtime support
- [x] More mover progress: script imports updated to aiw.*, lazy in core loop, experiment lab populated as part of structure move.

## Phase 5 — Cleanup & Cockpit Alignment (Planned)
- Remove hard-coded CodeAct where possible
- Make Cockpit/scripts depend only on public interfaces
- Deprecate legacy runbooks
- Full migration of monolith

## Current Constraints
- **Keep the system working during migration (no big bang)**: Muitos módulos legados são interdependentes (ex: worker_loop usa integration_outbox, external_worker_policy, github_intake, patch flows etc.). Migrar tudo de uma vez quebraria scripts, cockpit, runs existentes e fluxos de PR/patch.
- Prioritize documentation and structure before large refactors.
- All changes should move us toward the layers in ARCHITECTURE.md.
- Estratégia: thin delegates primeiro (aiw_workspace vira "ponte"), mover lógica gradualmente para aiw/ só quando seguro e testado. Foco atual no core do **Loop Iterativo do Agente** + provedores.

**Por que não migrar todos os módulos de uma vez?**
- Risco alto de regressão (29 arquivos ainda cheios de lógica pesada).
- Dependências cruzadas: patch review, evidence, coverage, github intake, workers dependem uns dos outros e de paths/workspace resolution.
- Compatibilidade: scripts (aiw-*-loop, aiw-cockpit, etc.) e fluxos operacionais ainda chamam via legado.
- Já estamos fazendo: CodeAct migrado, queue/worker_loop thinned, mais delegates em agent/policy/execution, imports atualizados. Restam ~20+ arquivos pesados (ver lista em "Latest").

## Fase 5 — Cleanup & Cockpit Alignment (Planned)
- Remove hard-coded CodeAct where possible
- Make Cockpit/scripts depend only on public interfaces
- Deprecate legacy runbooks
- Full migration of monolith (priorizando módulos que impactam o Loop Iterativo do Agente)

## Latest (2026-07-07)
- ROUND2 tasks 1-7 completed in batch. File deleted.
- Continuação da migração: lógica de CodeAct Sandbox migrada para aiw/providers/execution/codeact_sandbox.py (validação, run seguro, etc.). aiw_workspace/codeact_sandbox.py agora thin delegate. Registry e bridge atualizados para usar versão migrada. Funções de compat (list/get/describe/validate providers) implementadas em aiw/providers/execution. Mais imports em scripts preferindo aiw/.
- Reanalysis (see ARCHITECTURE.md): Architecture + providers + profiles + experiment foundation good. Loop Iterativo do Agente com iterações reais, despacho a provedores. Legado ainda pesado em ~25+ arquivos (queue, worker, patch, etc.), mas com mais delegates.
- Módulos legados pesados que ainda não foram totalmente migrados (exemplos): worker_loop.py (thinned), agent_queue.py (thinned), changed_lines_coverage.py, coverage_*, evidence_*, github_intake.py, integration_*, patch_*, test_*, validation_plan.py, external_worker_policy.py, agent_dispatcher.py. Esses dependem uns dos outros e de paths/workspace resolution.
- Documentação para refinamento futuro do Loop: ver seção abaixo e TODOs no código do aiw/agent/iterative_loop.py .
- Next phases: continuar migração (mais thin em remaining files like patch_*, coverage; update remaining scripts; move more logic), refinar Loop Iterativo do Agente (after migration), flesh memory/context, full non-dry execution.
- Latest migration: Continuamos com thin delegates (worker_loop, agent_queue). CodeAct migrado. Mas **não migramos todos os módulos de uma vez** por razões de segurança e dependências (explicado na seção "Current Constraints" acima). Foco em não quebrar o sistema enquanto movemos o core do Loop Iterativo do Agente + provedores.

## Migração do Loop Iterativo do Agente e Planejado para Refinamento
O Loop Iterativo do Agente (aiw/agent/iterative_loop.py) é agora o primário.
- Migrado: despacho a Provedores de Execução (via registry/bridge, CodeAct migrado), integração com Perfis/Roteador/Planejador LLM, memória, ferramentas (git/web).
- Legado: aiw_workspace/agent_iterative_loop.py = thin delegate.
- Para refinar depois (documentado):
  - Tornar ações mais ricas (usar código real do passo do plano, não só placeholder).
  - Permitir Planejador LLM decidir "continuar" ou "finalizar" explicitamente (já parcial com should_continue).
  - Melhor tratamento de falhas (retry inteligente, replanejamento).
  - Expor execution_trace de forma clara (já adicionado).
  - Testar e robustecer caminho de Execução Real (execute=True, com passos que alteram algo seguro).
  - Reduzir deps de aiw_workspace (path hygiene, resolve).
  - Integrar melhor com policy/checks em exec real.
  - Suporte a mais iterações com feedback real dos resultados para próximo plano.

Ver código em aiw/agent/iterative_loop.py para TODOs e comentários.


Next immediate work: OpenRouter wired into the agent loop for summarize step (uses model.generate). Tested with free model openai/gpt-oss-120b:free (reaches API when key set). Continue aligning more code (e.g. more delegation, make aiw/ primary for more modules, update other scripts). Update docs in parallel.
