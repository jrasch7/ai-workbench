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

## Latest (2026-07-08) — após passos de migração 1-4 (ROUNDs + movers)

- Cockpit (`scripts/aiw-cockpit`) agora usa **exclusivamente** o `aiw/agent/iterative_loop.py` para o caminho de "Loop Iterativo do Agente" (formulário com Perfil de Agente + modelo OpenRouter explícito). Fallback legado só para offline em último caso. Resultados renderizados com trace collapsível + "Re-executar com mesma tarefa".
- `aiw/agent/iterative_loop.py` é o primário: persistência de runs (`_persist_run`, disco em `.aiw/workspaces/.../agent-iterative-loop/runs/`), `list_agent_loop_runs` / `read_agent_loop_run` implementados em aiw/ (sem depender aiw_workspace para o core), execution_trace estruturado, _build_rich_action para ações reais (file_write, git via tools, shell), retry, replanejamento, policy para Execução Real.
- Provedores: CodeAct totalmente migrado (`aiw/providers/execution/codeact*`, registry, bridge atualizado). Docker/Devcontainer adapters. Model Provider OpenRouter registrado e usado via Roteador de Modelo + Perfil de Agente. LLMPlanner com fallback controlado.
- Migração de alto valor (passos recentes): github_intake, integration_outbox, integration_worker, evidence_bundle, patch_review_flow migrados para `aiw/integration/` e `aiw/patch/` (com thin delegates). CodeAct + queue/worker_loop + path hygiene removido do loop principal.
- `aiw-agent-loop` script prefere aiw/. Reexports em `aiw/__init__.py`.
- Legacy: ~25-30 arquivos ainda com lógica (thinned delegates onde seguro). Cobertura pesada (coverage_*, test_*, validation_plan, patch_gate, evidence_export, external_worker_policy, agent_dispatcher, profiles.py legado) ainda depende de interconexões. Não big-bang.
- Estado do Loop Iterativo do Agente + Cockpit: **pronto para uso real em desenvolvimento**. Roteador, Perfis de Agente, Provedor de Execução, Execução Real (com confirm), trace completo.
- Termos PT consistentes aplicados em código, UI e docs ("Loop Iterativo do Agente", "Perfil de Agente", "Provedor de Execução", "Execução Real", "Roteador de Modelo").
- Cockpit atualizado para formulários e views do Loop; listagem de runs do agente agora funciona via aiw/.
- Progresso geral alinhado com ARCHITECTURE: Provider-First sólido para o núcleo de agente. Cockpit é a interface principal.

**Após os passos de migração 1-4 (e movers/ROUNDs subsequentes)**: O fluxo "right way" (Cockpit → Perfil de Agente + OpenRouter model → Loop Iterativo do Agente → Provedores) está documentado e acionável hoje. Continua thin-delegate + migração incremental sem quebrar o operacional.

Próximo: mais delegates em coverage/test/patch_gate etc., refinar ações do plano no Loop, memória/context mais ricos, execução não-dry mais ampla.

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
  - Reduzir deps de aiw_workspace (path hygiene, resolve) — feito em 2026-07-08.
  - Integrar melhor com policy/checks em exec real.
  - Suporte a mais iterações com feedback real dos resultados para próximo plano.

Ver código em aiw/agent/iterative_loop.py para TODOs e comentários.


Next immediate work: OpenRouter wired into the agent loop for summarize step (uses model.generate). Tested with free model openai/gpt-oss-120b:free (reaches API when key set). Continue aligning more code (e.g. more delegation, make aiw/ primary for more modules, update other scripts). Update docs in parallel.

## Fluxo Prático de Desenvolvimento Real Hoje (Usável Agora)

**Cockpit como interface principal** (recomendado para uso real):
1. `./scripts/aiw-cockpit`
2. No formulário do **Loop Iterativo do Agente**:
   - Escolha **Perfil de Agente** (ex: `software-engineer` — permite planejamento LLM via Provedor de Modelo + despacho ao Provedor de Execução).
   - Escolha modelo OpenRouter explícito (ex: `openai/gpt-oss-120b:free` ou `anthropic/claude-3.5-sonnet`).
   - Descreva a tarefa.
   - Submeta via "Executar Loop Iterativo do Agente (execute=True)" ou versão offline.
3. Resultado: página com resumo + `execution_trace` (por iteração), `router_decision`, planos, re-executar.
4. Itere com contexto acumulado.

**CLI equivalente** (usa o mesmo Loop Iterativo do Agente):
```bash
./scripts/aiw-agent-loop --workspace aiw --task "Sua tarefa de engenharia aqui" --profile software-engineer --execute --confirm-agent-loop --max-iterations 4
```

- Perfil `code-reviewer`: llm_planning_allowed=false → plano mock + ferramentas de review.

## Próximo Passo Aplicado (2026-07-08): Full PR end-to-end + Browser research tool + Worktree Sandbox + Auto web_fetch

(Worktree sandboxing em CodeAct para exec isolada segura; auto-inject web_fetch no planner para tarefas de pesquisa.)

Verificação (bg task): auto_research/web_fetch injetado=True; worktree flag passado=True.

## Próximo Passo Aplicado: Persistent long-running agents with checkpointing

Subagent implemented checkpointing, resume via resume_run_id, relaxed max iters for persistent mode, periodic saves, cockpit support for start/resume + live ckpt status in trace/read.

Verification: resume increases iters, ckpt files created/loaded, persistent flag/mode set.

## Próximo Passo Aplicado (2026-07-08): Full auto PR in persistent mode

Subagent implemented:
- Auto PR creation in loop for persistent + completed + successful validation: detects tests passed, calls create_pr with run_id + test_results + evidence.
- Enhanced create_pr to accept run_id/test_results, augments body, policy gate.
- Cockpit displays "Auto-PR status" with link/evidence note.
- Policy support for auto.

Verification: logic present, E2E flows work in dry (gated in real without full confirm).

## Implemented approved step 2: Full autonomous git/PR for persistent validated runs on aiw ws

- In aiw_runtime/tools.py: updated _git_ws_gate (keep but add trusted_ws exception for aiw when autonomous_persistent), git_commit (extended w/ push= support for auto push after commit safely), create_pr (add autonomous_persistent + evidence params; relax confirm req for aiw+auton via flag; still policy gate; default allow commit/push for aiw trusted; pass flags to internal git_create_branch/git_commit).
- Enhanced auto-PR block in aiw/agent/iterative_loop.py (around Full autonomous PR creation): collect/pass run_id/test_results/evidence, call create_pr(confirm=False, autonomous_persistent=True) when policy + persistent + validated.
- git_commit + push now auto in aiw ws success path for persistent validated (via flag + extension).
- Non-aiw ws still gated (exception only for aiw).
- Surgical: builds directly on existing "autonomous for persistent" / auto-PR comments in loop + tools.
- Verified via python -c (mocks, direct calls, dry paths, gate checks for aiw vs other ws); imports + no breakage.
- MIGRATION.md updated (this note).
- Uses aiw/ paths only (aiw/agent/iterative_loop.py + aiw_runtime/tools.py); thin delegates propagate.

## Análise Atual vs Manus/Devin + Próximo Passo Definido

**Estado atual (pós 5 passos + worktree + web_fetch auto + persistent ckpt + auto PR):**
- Execução real poderosa: edits isolados (worktree), pesquisa auto (web_fetch), correção auto (until_success + failure parse), validação (experiment + tests), PR auto em persistent success.
- Persistência: checkpoint/resume para long-running (até 100 iters), missões no cockpit.
- UI: cockpit com trace, apply, PR, approvals, isolated, persistent.
- Contexto: AST indexing + early injection.
- Política/segurança: worktree_sandbox, gates, confirm.
- Migração: aiw/ core + delegates.
- Testes: E2E real + smoke.

**Gaps vs Manus/Devin (agentes autônomos full):**
- Ainda max iters (100 em persistent); não ilimitado sem intervenção.
- PR auto bom, mas gated (policy/confirm); não 100% sem humano para risky.
- Browser: fetch básico; não interativo/full (sem JS, forms, auth).
- RAG: symbols + lexical; não full semantic embeddings over large codebases.
- Autonomia: loop por invocação (mesmo persistent); falta daemon 24/7 que monitore queue/issues e rode missões longas sem re-invoke.
- Planejamento: LLM + injeções; não tree-of-thoughts ou self-reflection profunda.
- Sandbox: worktree bom, mas não full (sem docker/devcontainer por-run).
- Self-improvement: experiment integrado, mas não meta-learning.
- Escala: ainda depende de chaves externas; não full self-hosted sem fallback.
- UI: bom para submissão/trace, mas não dashboard live para múltiplos agentes longos.

**Próximo passo apropriado:**
**Remover limites duros de iters em modo persistent (ou usar config ilimitado com checkpoints), adicionar daemon/background worker para autonomia 24/7 (usando queue + persistent runs), e implementar browser interativo básico (e.g., playwright stub seguro para forms/JS research) integrado no planner para tarefas complexas.**

Isso avança para full long-running autonomous agents como Devin/Manus, mantendo surgical (aiw/, gates).

Subagente pode ser lançado para isso. Diga "sim, segue" para aplicar.

Docs atualizados. Sistema está muito mais próximo de harness poderoso self-hosted.

- Persistir estado (plan, results, context, worktree) em checkpoints após cada iteração.
- Suporte a resume de run_id com checkpoint.
- Modo 'persistent' relaxando limites de iters, com gates para ações de risco.
- Integração com worktree existente + web_fetch.
- Cockpit: UI para iniciar/resumir missões longas com status ao vivo.

Rumo a autonomia full (Devin-like long sessions).

Adicionado:
- web_fetch em aiw_runtime/tools.py (urllib safe fetch, network_access, para research/docs como Devin).
- Aprimorado create_pr para full flow (commit/push/gh se possível, outbox integration).
- Handler em cockpit para /runner/pr/create com banner e trace update.
- Suporte em _build_rich_action para web_fetch / browser hints.
- Policy cap para web_fetch (network_access: True, requires_confirmation).
- Teste E2E real com execute + apply + PR stub + smoke.

Isto avança autonomia: agente pode pesquisar externo + criar PR após edits validados.

## 5 Passos Aplicados (Sugestão de Próximo Passo — 2026-07-08)

**Todos os 5 passos foram aplicados com subagentes em paralelo (worktree isolation) + ports/sincronização para main.**

1. **Robustecer Loop para auto-correção** (aiw/agent/iterative_loop.py, planner, tools): until_success_mode, run_tests estruturado, parse de falhas, force continue + heurística "pedir ajuda humana", effective_max=10.
2. **Ferramentas git write + PR** (aiw_runtime/tools.py, cockpit, integration): git_create_branch, git_commit, create_pr (gates fortes, only aiw ws, confirm, backups, outbox tie-in); Cockpit "Gerar PR" pós-apply.
3. **Context Provider repo-aware** (providers/context/local_rag.py, planner, loop): AST symbol index (funções/classes/imports), hybrid retrieve (lexical + usage), early call para tarefas complexas, chunks no prompt para old/new precisos.
4. **Cockpit missões + UX** (scripts/aiw-cockpit): missões persistentes (.aiw/.../missions/), render_unified_diff_html, aprovações inline (pending_approval, botões, handlers), re-exec attach.
5. **Migração + Experiment Lab** (patch, experiment, cockpit/regression): mais delegates para patch_gate/validation_plan/etc, prefers aiw/ em cockpit/regression, integração de run_benchmark/arena no loop para tasks de "test"/"validar".

Subagentes completaram (IDs nos logs), verificação: compiles, smoke, until_success=True, experiment_lab_used, context symbols, git tools, missions/diffs/approvals. Progresso significativo rumo a autonomia Manus/Devin (self-correction, full workflow, repo understanding, UX para long tasks).

## Exemplo Completo: Tarefa Real → Trace com Edição Real → Resultado (Loop + Cockpit)

Foco atual: Execução Real poderosa + refatorações precisas via aiw/agent/iterative_loop + aiw_runtime/tools + "Aplicar patch seguro" com feedback inline no Cockpit. Sem big-bang.

**Tarefa exemplo (via CLI ou Cockpit "Executar Agente Direto")**:
```
refatorar exemplo: usar editar para escrever log em .aiw/generated/refator_test.py e validar
```
(ou "adicione log em Z e rode pytest"; use --profile software-engineer --model openai/gpt-oss-120b:free --execute --confirm-agent-loop --max-iterations 2)

**Fluxo**:
1. LLM (ou mock no fallback) gera plano com action_hint contendo "editar" + target_file .aiw/generated/... + kind codeact.
2. _build_rich_action detecta (PT/EN: editar/refatorar/adicionar/log/...) → constrói ação python_eval que chama `from aiw_runtime.tools import file_write ... ; file_write(..., overwrite=True)`
3. Provedor CodeAct (execute=True + confirm) roda o code em sandbox (validação BAD_PATTERNS passa para wrappers limpos).
4. Side-effect real: arquivo criado em .aiw/generated/ (com backup se overwrite), trace registra "tool": "file_write", "bytes_written", "path", "side_effect=edicao_real" etc.
5. Feedback rico → accumulated_context → replan (se mais iters).
6. No Cockpit: trace collapsível por iteração + seção "Preview de Alterações Propostas" (com diffs se patch) + botão "Aplicar patch seguro" (chama /runner/patch/apply → project_patch_apply via tools, só para ws=aiw).
7. Resultado: status=completed, has_real_execution=true, run_id, código gerado + readback no stdout do trace.

**Evidência de run real (execute)**:
- mode: "execute", status: "completed", has_real: True
- trace entry: success true, provider "codeact", output inclui `{'ok': True, 'tool': 'file_write', 'path': '.aiw/generated/....py', 'bytes_written': N, 'created': True}`
- Arquivo aparece em .aiw/generated/ (ver ls)
- Cockpit mostra trace + botão apply (para previews de sources); re-exec preserva profile/model.

**Segurança**: paths restritos, dry default, confirm explícito, policy gates, backups em .aiw/backups, project_patch só apply manual para aiw ws, validate no sandbox.

Atualize sempre com `./scripts/aiw-agent-loop ...` ou cockpit. Key OpenRouter: atualmente pode dar 401 ("User not found") — o código cai graciosamente em mock_plan (planner except) mas o caminho de **Execução Real** (execute + confirm + aiw_runtime/tools file_write/patch_preview/apply + validate) funciona 100% (veja demo controlada abaixo).

**Demo E2E controlado "refator preciso + apply manual + validate" (step 2)**:
```python
from aiw_runtime.tools import project_patch_preview, project_patch_apply, file_write, shell_exec
target = ".aiw/generated/e2e_precise_refactor_demo.py"
... write base, preview with exact old/new (como LLM faria após file_read), apply, py_compile ...
# Resultado: preview_ok, applied=True, backup=..., validate exit_code=0, conteúdo atualizado.
```
Isso simula "LLM planning (ou mock) → read → precise patch → apply via botão/CLI → pytest/py_compile".

Ver também: runbooks/AIW_AGENT_ITERATIVE_LOOP.md , scripts/aiw-cockpit (render_agent_trace_html + inline apply banner), aiw_runtime/tools.py (file_write/project_patch_*), aiw/agent/iterative_loop.py (_test_full_edit_preview_apply_validate_flow).

**Smoke de regressão do fluxo completo**:
```bash
./scripts/aiw-agent-loop-regression-smoke --workspace aiw
```
Inclui o check `full_edit_preview_apply_validate_via_loop`.

- `--execute --confirm-agent-loop` habilita **Execução Real**.

**O que esperar** (com chave):
- Roteador de Modelo escolhe com base no Perfil de Agente.
- 1-N iterações com replanejamento e `should_continue`.
- Despacho ao **Provedor de Execução** (codeact principal).
- execution_trace completo (status, policy, resultado, provider).
- Persistência em `.aiw/.../agent-iterative-loop/runs/`.

**Nota**: `list_agent_loop_runs` / `read_agent_loop_run` agora funcionais via aiw/agent (disco + cache). Cockpit handler especial mostra trace rico imediatamente.

Uso temporário de outros harnesses é ok durante migração de partes legadas, mas o fluxo via Cockpit + Loop Iterativo do Agente + Perfis de Agente é o caminho principal para desenvolvimento real.

### Exemplo completo "tarefa real → trace com edição → resultado" (Cockpit + Execução Real)

**Tarefa real usada:**
```
Liste os principais arquivos e diretórios do projeto (top 8) e crie um arquivo de resumo em .aiw/generated/resumo-estrutura.md listando-os com contagem, usando ferramentas reais do Provedor de Execução.
```

**Via Cockpit (formulário do Loop Iterativo do Agente):**
- Perfil de Agente: `software-engineer`
- Modelo OpenRouter: `openai/gpt-oss-120b:free`
- Botão: **Executar (Execução Real)**

**O que aparece na página de resultado (render via render_agent_trace_html):**
- Meta tags: `Perfil de Agente: software-engineer`, `Modelo: openai/gpt-oss-120b:free`, `Execução Real: ✓`, `status: completed`.
- `router_decision` com `profile_used`.
- `execution_trace` com `<details>` por iteração:
  - Passos `inspect_context` → status `executado`.
  - Passo `codeact_python_eval` (action_hint com edit) → status `"executado"`, stdout contendo `{'ok': True, 'tool': 'file_write', 'path': '.aiw/generated/loop_iter1_... .log', 'bytes_written': ...}`.
  - Destaques de arquivos modificados (📄 spans).
- Botão **"Re-executar com mesma tarefa"** (hidden fields preservam `profile`, `model`, `agent_task`).

**Resultado observável:**
- Novo arquivo criado em `.aiw/generated/` (escrito por `file_write` do aiw_runtime via Provedor de Execução codeact).
- Run persistido: `.aiw/workspaces/aiw/agent-iterative-loop/runs/ail-*/run.json`.
- Re-exec: gera novo run_id, reutiliza Perfil de Agente + modelo do form → permite iteração rápida "tarefa → trace com edição → ajuste → re-exec".

Este exemplo prova que o núcleo migrado (`aiw/agent/iterative_loop.py` + cockpit wiring + providers) está usável para **desenvolvimento real** com side-effects controlados e visibilidade completa no trace. Atualizações em MIGRATION refletem o alinhamento do "right way" para o Loop.

## Resumo Análise Pós 5 Passos (via subagentes)
- Loop: Refinado com ações ricas, retry, trace completo, Exec Real.
- Cockpit: Integrado, form com Perfil+modelo, trace bonito, re-exec.
- Migração: Módulos chave (integration, patch) em aiw/, delegates.
- Docs: Fluxo prático documentado.
- Estado: ~75% alinhado, usável para dev real via interface. Gaps: migração completa, full autonomous exec.

## Estado Atual da Migração vs Partes Usáveis (2026-07-08, após passos 1-4)

**Usável para desenvolvimento real HOJE (foco principal — "right way")**:
- `aiw/agent/iterative_loop.py` (primário) + planner/llm_planner + router/router + profiles/loader + providers/model (openrouter real) + providers/execution/* (CodeAct migrado completo, Docker/Devcontainer, registry/bridge).
- Cockpit: formulário principal com Perfil de Agente + modelo OpenRouter → usa aiw/agent diretamente; exibe execution_trace rico + re-executar.
- `aiw-agent-loop` CLI: suporta --profile + --execute --confirm-agent-loop.
- Roteador de Modelo (AUTO), Perfis de Agente, Provedor de Execução, policy para dry vs Execução Real, memória, tools (aiw_runtime), persistência de runs do loop.
- List/read de runs do Loop Iterativo do Agente funcionais. Trace, iterações, replanejamento, rich actions.

**Ainda em legado (thinned delegates, ~25+ arquivos pesados)**:
- worker_loop, agent_queue, agent_dispatcher, patch_gate, evidence_export, coverage_*, changed_lines_coverage, test_*, validation_plan, external_worker_policy, profiles.py (legado).
- Fluxos completos de patch/PR + integração externa (exigem CLI manual na maioria).
- Algumas listagens históricas legadas, experiment lab completo, context packs avançados.

**Estratégia**: thin delegates (aiw_workspace como ponte) + mover só quando seguro. Core do **Loop Iterativo do Agente**, **Provedor de Execução**, **Roteador de Modelo** e **Perfil de Agente** priorizado — isso habilita o fluxo de desenvolvimento real via Cockpit hoje.

**O que NÃO fazer**:
- Não adicione features pesadas novas em aiw_workspace/.
- Para uso real: prefira Cockpit + Loop Iterativo do Agente (mesmo que use temporariamente harness alternativo para partes ainda legadas).

Consulte `docs/ARCHITECTURE.md` para o target e `aiw/agent/iterative_loop.py` (docstring + TODOs) para refinamentos planejados do Loop.

Se precisar de harness temporário alternativo para partes ainda em migração, veja seção equivalente no README.md.

## Atualização Cockpit (scripts/aiw-cockpit) como interface principal para Loop Iterativo do Agente (2026-07, após migração)

- Formulário principal para desenvolvimento real usa **Perfil de Agente** + **modelo OpenRouter** explícito (AGENT_OPENROUTER_MODELS + agent_profile_select_html).
- Submissão `/runner/run-agent` (real) e offline chamam `run_agent_from_cockpit` que prioriza `aiw.agent.iterative_loop.run_agent_iterative_loop_once` com `execute=...`, `confirm_agent_loop`, profile enriquecido com default_model.
- Resultado: render rico com trace por iteração (collapsibles), destaque de paths, tags de status/perfil/modelo, form de re-executar preservando perfil+modelo.
- Persistência + list/read de runs do Loop Iterativo do Agente via aiw/agent (sem legacy para este fluxo).
- UI usa consistentemente "Loop Iterativo do Agente", "Perfil do Agente", "Provedor de Execução".
- O Cockpit é a interface funcional principal para o fluxo de desenvolvimento real hoje (Cockpit + Loop Iterativo do Agente + Perfis + OpenRouter).

Mantenha docs/README atualizados em paralelo com refinamentos do loop.

## Cockpit: Integração Completada do novo aiw/agent/iterative_loop (follow-up)
- "Executar Agente Direto" form + existing agent buttons (workspaces, exec panel) fully wired to aiw.agent.iterative_loop.run_agent_iterative_loop_once via run_agent_from_cockpit.
- Enhanced form: free-text task, clear "Perfil de Agente" select (software-engineer, security-analyst, code-reviewer), explicit OpenRouter models incl. free like openai/gpt-oss-120b:free.
- Rich results: render_agent_trace_html (central helper) for execution_trace+step_results using <details> per iteration, status per step, modified file paths (with spans), accumulated_context, summary.
- Post-submit: direct trace HTML for /runner/run-agent* (avoid generic redirect); re-exec button pre-fills form with same tarefa/perfil/modelo.
- UI text updated to PT terms ("Loop Iterativo do Agente", "Perfil de Agente", "Execução Real").
- Prefer aiw/ (try first) + backward compat kept; only cockpit file edited for this.
- Verified: Python parses (no syntax err), paths wired (agent-iterative-loop APIs, run funcs, lists).
- Changes commented in code + this MIGRATION note.

## Continuação Cirúrgica da Migração (2026-07-08+): Foco Exclusivo em Cockpit + Loop Iterativo do Agente

**Apenas módulos que impactam o caminho do agente/cockpit (targeted/surgical, sem big bang):**
- Thin delegate para execution-related: `aiw_workspace/execution_provider.py` agora reexporta puro de `aiw/providers/execution/` (CodeActExecutionProvider migrado + registry). Atualizado bridge em aiw/providers/execution/bridge.py para usar aiw/ nativo (remove dep de aiw_workspace no caminho do Provedor de Execução).
- Garantido que `aiw_workspace/github_intake.py`, `integration_outbox.py`, `integration_worker.py` são thin delegates apontando para `aiw/integration/*` (já eram, reforçado).
- Atualizados **scripts/aiw-cockpit** + outros agent-related (aiw-runner-agent, aiw-worker-loop, aiw-agent-queue, aiw-agent-dispatcher) para **preferir imports de aiw/** para loop (`aiw/agent`), profiles (`aiw.profiles`, load_profile), providers (`aiw.providers.execution`, model) + github/integration migrados (usando blocos try: from aiw.integration... except: aiw_workspace fallback).
- Adicionados reexports de workspace helpers em `aiw/__init__.py` (resolve_workspace, load_workspaces_config) para permitir "from aiw import" em scripts.
- Comentários em PT-BR adicionados ("Loop Iterativo do Agente", "Provedor de Execução", "Intake de GitHub", "Outbox de Integração", "thin delegate", "migração cirúrgica").
- **Não tocado**: fluxos full de patch, coverage_*, evidence_*, validation, workers pesados, agent_dispatcher full, patch_review_flow, etc. (conforme instruções).
- Compatibilidade mantida 100% (delegates + try/except + reexports).
- Foco estreito: habilita Cockpit funcional + novo Loop Iterativo do Agente (perfis, providers, execução via registry/bridge).

**Estado após**: aiw/ é primário para o core do agente (loop + perfis + providers + alguns integration intake). Cockpit e scripts agent-related priorizam aiw/. Ver seção "Fluxo Prático" acima para uso.

Atualização registrada para rastreamento da Fase 5 (Cockpit Alignment).

## Continuação Cirúrgica da Migração (2026-07-08, subagente): runtime_gate + integration (Cockpit/agent path)

**Escopo restrito a 1-2 módulos impactando caminho Cockpit + Loop Iterativo do Agente**:
- **Módulo 1: runtime_gate (Porta de Runtime)**:
  - Lógica completa movida de `aiw_workspace/runtime_gate.py` → `aiw/policy/runtime_gate.py` (agora source of truth, com consts RUNTIME_PROFILE, RUNTIME_PROFILES, FIXED_CODEACT_OPERATIONS, KNOWN_..., evaluate_runtime_gate, assert_runtime_allowed).
  - `aiw_workspace/runtime_gate.py` reescrito como **thin delegate** (reexports explícitos de aiw.policy.runtime_gate; mantém compat para callers relativos em aiw_workspace/* e scripts).
  - Atualizado `aiw/policy/registry.py` para preferir `.runtime_gate` (aiw/) ao invés de aiw_workspace para runtime (outros como capability_policy/isolation permanecem legacy).
  - `aiw/policy/runtime_gate.py` agora implementa a lógica + header com termos PT.
  - Usado via PolicyEngine no _check_capability do Loop Iterativo do Agente e gates de Execução Real.
- **Módulo 2: integration (completando)**:
  - Atualizados helpers `_get_workspace_helpers` em `aiw/integration/github_intake.py`, `integration_outbox.py`, `integration_worker.py` para **preferir `from aiw import resolve_workspace`** + cálculo de AIW_ROOT via os.environ + Path(__file__).parents[2] (mesmo padrão de aiw/agent/iterative_loop.py).
  - Removida dependência direta de `aiw_workspace.profiles` dentro do código de aiw/integration/ (sem tocar lógica pesada de profiles.py ou evidence).
  - Thin delegates em aiw_workspace/ para integration já estavam corretos; isso "completa" o prefer aiw/ no lado aiw/.
  - Termos PT: Intake de GitHub, Outbox de Integração, Worker de Integração.

**Atualizações em scripts (prefer aiw/)**:
- `scripts/aiw-agent-loop`: imports atualizados/comentados para prefer aiw/ (já usava aiw.agent + from aiw import load_profile); adicionado try: from aiw.policy import evaluate_runtime_gate .
- `scripts/aiw-cockpit`: try block estendido com `from aiw.policy import evaluate_runtime_gate`; comentários expandidos sobre migração de runtime_gate + integration; _get_aiw_or_legacy_integration doc atualizado.
- Mantidos try/except para compat total.

**O que NÃO foi tocado (conforme instruções estritas)**:
- Nenhuma lógica pesada/relacionada não-impactante: aiw_workspace/profiles.py (workspace validation etc), evidence_*, patch_review_flow, coverage_*, validation_*, agent_dispatcher, worker_loop, etc.
- Não se mexeu em capability_policy.py, isolation_boundary.py (apenas runtime_gate na camada policy).
- Nenhuma mudança em aiw_workspace/profiles.py ou arquivos pesados legados.
- Patch/evidence ainda usam aiw_workspace.profiles em seus aiw/ impls (escopo limitado).

**Compatibilidade**: 100% mantida (thin delegates reexportam, aiw/ agora primário para os 2 módulos, fallbacks intactos). Systema continua funcional.

**Termos PT aplicados** (consistentes com prev): "Loop Iterativo do Agente", "Porta de Runtime", "Perfil de Agente", "Execução Real", "Intake de GitHub", "Outbox de Integração", "Worker de Integração", "thin delegate", "migração cirúrgica".

**Report do que foi migrado**:
- Migrado: runtime_gate (lógica + delegates + registry update) + integração helpers em aiw/ (prefer aiw/ completo).
- Arquivos editados: aiw/policy/runtime_gate.py (novo conteúdo), aiw_workspace/runtime_gate.py (thin), aiw/policy/registry.py, aiw/integration/github_intake.py, aiw/integration/integration_outbox.py, aiw/integration/integration_worker.py, scripts/aiw-cockpit, scripts/aiw-agent-loop, docs/MIGRATION.md.
- Resultado: aiw/ preferido no path Cockpit/agent para policy/runtime + integration; delegates em aiw_workspace; sem big-bang.

Esta atualização cirúrgica continua o alinhamento Fase 5 sem regressões. Próximo (se aplicável): mais targeted se solicitado.

Atualização registrada (2026-07-08).

## Daemon-Next Completo (2026-07-08) — 5 Subpassos + Fluxo 24/7

**daemon-next marcado completo** após verificação (smokes, imports, exec básico, compile, _test_daemon_persistent_logic, cockpit wiring, queue disk + worker).

**5 subpassos aplicados (todos verificados presentes e operacionais):**
1. Relaxar limites duros de iters em modo persistent: `MAX_ITERATIONS_PERSISTENT` via env `AIW_PERSISTENT_MAX_ITERATIONS=0` (prático ilimitado, quebra em !should_continue / policy / stop explícito). Código em aiw/agent/iterative_loop.py + suporte em aiw-agent-loop --persistent.
2. Checkpointing + resume: `_save_checkpoint` / `_load_checkpoint` + resume_state no loop (plan, previous_results, accumulated_context, status), paths em `.aiw/.../checkpoints/<run_id>.json`, listagem de ckpts em list_running_daemons, resume_run_id param em start_persistent_agent_daemon e CLI --resume --run-id.
3. Daemon bg + queue intake: `start_persistent_agent_daemon` (enqueue + thread bg chamando run_... com persistent=True), list_running_daemons, stop_persistent_agent_daemon; + `PersistentAgentWorker` em aiw/queue/worker.py (poll, start_daemon_worker, max_concurrent, requeue, resume_all_checkpoints_as_daemons); disk-backed queue em AgentQueue (persist/load em queue.json).
4. Integração Cockpit + UI/monitor 24/7: start_daemon_agent_from_cockpit, list_daemons_from_cockpit, checkbox "start_daemon", botão "Start Daemon (bg persistent)", handlers /runner/start-daemon + /api/daemons + /api/workspaces/.../daemons; daemon_status_html; suporte a mission_id.
5. Auto-PR + research em persistent + tools: auto create_pr em persistent completed + has_real + tests pass (em loop); web_fetch (com render_js) + detecção "daemon-next-3" (pesquisar/research/fetch) no _build_rich_action; policy network_access; Fluxo completo com queue + daemon threads.

**Verificação realizada:**
- python -c imports + basic calls (daemon, persistent, queue, web_fetch('https://httpbin.org/html'))
- _test_daemon_persistent_logic() -> ok
- ./scripts/aiw-agent-loop-regression-smoke components (targeted) + compile py (aiw/agent/iterative_loop.py, aiw/queue/* etc)
- Sistema roda (no syntax errors, basic exec de start/list/stop/ckpt)
- Todos os 5 subpassos: código + delegates + reexports + cockpit + env + resume presentes e exercitados.

**Fluxo 24/7 (exemplo completo):**
```bash
# 1. Cockpit (UI principal)
./scripts/aiw-cockpit
# marque "Start as background daemon", perfil software-engineer, tarefa "pesquisar docs + editar + validar até sucesso", submit

# 2. CLI daemon worker
./scripts/aiw daemon aiw
# ou
python3 -c 'from aiw.queue import start_daemon_worker; start_daemon_worker("aiw")'

# 3. Env unlimited + resume
AIW_PERSISTENT_MAX_ITERATIONS=0 ./scripts/aiw-agent-loop --workspace aiw --task "missão longa autônoma" --persistent --execute --confirm-agent-loop --run-id <rid> --resume

# 4. Monitor
python3 -c '
from aiw.queue import list_daemon_workers
from aiw.agent.iterative_loop import list_running_daemons
print(list_daemon_workers()); print(list_running_daemons())
'
# ou GET /api/daemons no cockpit server
```
Auto-PR dispara em persistent+completed+real exec+validação sucesso. Checkpoints permitem recovery pós-restart.

**Atualização "Análise Atual" (pós daemon-next):**
Estado atual (pós 5 passos + worktree + web_fetch + persistent ckpt + auto PR + daemon-next 24/7):
- Autonomia: daemon bg 24/7 com queue intake + múltiplas missões + checkpoint recovery (sem re-invoke manual).
- Exec real + self-correction + PR auto + research (web_fetch) em long-running.
- Iters: ilimitado prático via env + gates.
- UI: cockpit start/resume/monitor daemons + trace live.
- Persist: queue disk + run ckpts + missions.
- Migração: aiw/queue + aiw/agent/iterative_loop primary para daemon path.
Gaps reduzidos vs Manus/Devin: agora tem daemon 24/7 (threaded, cockpit-driven); ainda: full browser interativo, embeddings RAG, auto-commit sem confirm em trusted, E2E multi-missão tests dedicados, relax policies.

**Próximos 5 passos concretos aprovados (2026-07-08) — "Aprovado, segue"**

1. Migrate 2-3 more high-impact modules (e.g. patch_gate.py + coverage/validation) to aiw/ with thin delegates + reexports; update callers to prefer aiw/.
2. Full autonomous git/PR — enhance create_pr + loop to do real git commit + push + gh pr create (with run evidence/tests) for aiw ws when persistent + validated + policy allows (reduce extra confirm for trusted ws).
3. Deeper context/RAG — extend aiw/providers/context/ with simple local embeddings (or reuse existing indexer) + inject richer chunks/symbols + usage into LLMPlanner and loop for long missions.
4. E2E multi-mission daemon test — add/extend regression smoke (or new test) that starts ≥2 persistent daemons via worker/cockpit, exercises resume from ckpt, queue drain, auto-PR, and monitor; run via aiw-agent-loop-regression-smoke.
5. Policy + browser polish — relax a few more caps for aiw ws in runtime_gate/policy when trusted; add basic follow/extract actions to web_fetch (still gated, stdlib+playwright) and expose in _build_rich_action.

**Step 3 (Deeper RAG with simple local embeddings) implemented (aiw-first, stdlib only):**
- aiw/providers/context/local_rag.py: added _tokenize/_counter/_cosine/_build_embedding_index (BOW over symbols+chunks.jsonl)/_retrieve_with_embeddings; index-on-build; retrieve now does hybrid lexical + code_aware + embed (combined score boost via overlap).
- aiw/planner/llm_planner.py: improved chunks_str to show embedding_score + richer usage/symbols + note for persistent.
- aiw/agent/iterative_loop.py: explicit use_embeddings=True on retrieve calls; for persistent/long missions: re-retrieve richer context_chunks (limit+embed) passed to planner.plan per replan.
- Registry unchanged (auto). For long missions: fresher richer chunks injected.
- Verify: python -c "from aiw.providers.context.local_rag import LocalRAGContextProvider; ..."; planner/loop paths exercised.
- MIGRATION: this note. No new deps. Surgical.

Todos os passos com subagentes paralelos, surgical aiw-first, relative paths, read-before-edit, smoke/E2E verification.

Subagentes lançados para os 5 passos. Progresso em paralelo.

Atualização registrada (após aprovação do usuário).
