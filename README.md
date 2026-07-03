# AI Workbench

AI Workbench é uma bancada local de engenharia de software assistida por agentes de IA, criada primariamente para o ecossistema Nivela e cenários reais de engenharia.

O objetivo do projeto é construir uma infraestrutura própria, controlável e extensível para desenvolvimento de software com agentes autônomos. Inspirada em plataformas como Devin, Manus e ambientes CodeAct, o AI Workbench preza pela liberdade operacional, controle de custos, múltiplos provedores de LLM e adaptação profunda aos projetos locais do usuário.

**Importante:** Este projeto não é um simples chatbot nem um fork de OpenHands (agora tratado apenas como referência legada). É um Cockpit próprio integrado a um Runtime seguro, com Context Pack e Gateway local de modelos.

## Capacidades atuais

A bancada evoluiu drasticamente e hoje contempla:

* **AIW Cockpit:** Interface centralizada e operacional para acompanhamento de tarefas e runs.
* **Agent Online/Offline:** Suporte a execuções com chamadas reais ao LLM ou modos offline/dry-run para testes sem custo.
* **Tool Runtime seguro:** Engine de tool calling protegida, nativa e acoplada.
* **Tool Evidence Console:** Console de logs visuais precisos para cada tool invocada.
* **File OS Seguro:** Tools guardrails para manipulação de arquivos (`file_read`, `file_write`, `file_patch`).
* **Project Write Mode:** Fluxo imutável de `project_patch_preview`, `project_patch_apply` e `project_patch_rollback`.
* **Context Pack v1:** Camada estruturada auditável contendo a saúde da documentação.
* **Search Index Cache:** Cache lexical para buscas instantâneas no Cockpit.
* **Context Injection:** O runner é capaz de injetar context packs vitais antes da call para o modelo (`--use-context-pack`).
* **Agent Iterative Loop Offline v1:** Loop manual/foreground com mock planner, Capability Policy `local_offline_v1`, path hygiene, histórico/detalhe read-only no Cockpit e CodeAct seguro sem LLM real.
* **Agent Loop Regression Smoke:** Harness offline para validar CLI, policy, traversal, path hygiene, CodeAct confirmado e Cockpit read-only opcional com artifacts auditáveis.
* **Isolation Boundary Gate:** Policy conservadora `host_best_effort` que permite apenas CodeAct fixo offline confirmado e bloqueia LLM planner, codigo dinamico, shell, rede externa e external write ate existir devcontainer/VM.
* **Safe Search Guard:** Busca textual operacional que exige paths explicitos e bloqueia secrets/artifacts antes de leitura.
* **Operational View:** Visão clara de missões, status de aprovação de handoffs e rejeições de patches.

## Arquitetura atual

```text
AIW Cockpit
  ├── Mission Control / Operational View
  ├── Workspace & Task Navigation
  ├── Tool Evidence Console
  ├── Proposed Patches
  ├── Context Pack Health
  └── Local Search

Agent Runner
  ├── online mode via LiteLLM
  ├── offline/dry-run mode
  ├── context pack injection
  └── run artifacts

Tool Runtime
  ├── directory_list
  ├── file_read
  ├── shell_exec seguro
  ├── file_write restrito
  ├── file_patch restrito
  └── project_patch preview/apply/rollback

Context Layer
  ├── search-index.json
  ├── context-pack.json
  └── context-used por run

LiteLLM Gateway
  └── aliases dev-fast/dev-coder/dev-review...
```

## Segurança e Limites

Este projeto segue regras estritas de infraestrutura local:
* **`.env` bloqueado:** Impedido de ser lido ou patcheado ativamente.
* **Segredos mascarados:** Resumos do indexer varrem paths e ocultam padrões de secrets como `[masked]`.
* **Path traversal bloqueado:** Bloqueio forte no Tool Runtime contra `../` saindo da base do projeto.
* **Shell restrito:** Operações mutáveis perigosas via CLI requerem aprovação ou são sumariamente negadas em background.
* **Patches imutáveis:** Patches rodam sempre em preview e exigem apply via UI com garantias de rollback (backups persistidos).
* **Sem dependência externa:** O indexador léxico é python puro nativo, sem provider online para montar vetores do repositório neste estágio.
* **Artefatos isolados:** Logs de run e tools são marcados como temporários e não compõem o histórico Git.

## Como rodar

Inicialize o painel principal na interface web (default porta 4000 ou parametrizada):

```bash
# Iniciar o AIW Cockpit (background server + browser)
AIW_COCKPIT_OPEN_BROWSER=0 AIW_LLM_ENABLED=1 AIW_MODEL=dev-coder ./scripts/aiw-cockpit

# Iniciar uma run em modo Offline para testes e Dry-run (sem chamar a API do modelo)
AIW_AGENT_OFFLINE=1 AIW_USE_CONTEXT_PACK=1 ./scripts/aiw-runner-agent --offline

# Rodar a suíte de Tool Smoke Test atestando restrições de segurança
./scripts/aiw-tool-smoke

# Reconstruir o índice de contexto de força bruta
python3 -m aiw_context.indexer

# Rodar o Agent Iterative Loop offline em dry-run
./scripts/aiw-agent-loop --workspace aiw --task "Validate offline iterative loop" --once --dry-run

# Rodar a regressao offline do Agent Loop
./scripts/aiw-agent-loop-regression-smoke --workspace aiw

# Avaliar o Isolation Boundary sem executar nada
./scripts/aiw-isolation-gate --workspace aiw --operation fixed_codeact_python_eval --mode offline --confirmed

# Buscar texto com guardrails de escopo
./scripts/aiw-safe-search "isolation_profile" --paths aiw_workspace docs/runbooks README.md
```

O regression smoke registra `external_network_used=false` e diferencia GETs locais do Cockpit com `localhost_http_used=true` apenas quando `--with-cockpit` e usado. Validacoes textuais devem usar paths explicitos, nunca busca ampla em `.`.
O Isolation Boundary registra `isolation_profile=host_best_effort`; LLM real, codigo dinamico e shell continuam bloqueados por policy ate existir isolamento forte.
Use `./scripts/aiw-safe-search` em vez de `grep -R` quando houver risco de varrer secrets ou artifacts locais.


## Estado operacional atual

O AIW possui hoje um fluxo local e auditável:

GitHub Intake
→ Integration Inbox
→ Patch Intent
→ Agent Queue
→ LLM Queue Guard
→ Patch Preview
→ Validation Plan
→ Review Gate
→ Evidence Bundle
→ Evidence Export
→ Integration Outbox
→ Integration Worker CLI
→ External Worker Policy

Nenhum daemon externo roda por padrão.
Nenhuma ação GitHub/Jira é executada pela UI.
Toda integração externa exige CLI manual, confirmação explícita e policy permitindo.


## Foreground Worker Loop

O AIW possui um worker loop manual e foreground para processar Integration Outbox.

Ele não é daemon, não roda em background e não executa pela UI.

Fluxo:

Integration Outbox item ready
→ dispatch.json explícito
→ Foreground Worker Loop
→ External Worker Policy
→ Integration Worker CLI
→ gh pr edit somente se permitido

Por padrão, roda em dry-run.
Execução real exige --execute e --confirm-worker-loop.

## Inspirações

O AIW se inspira em Devin, Manus, OpenHands, CodeAct/Cyber Bench e workspaces locais como Odysseus.

Odysseus fica como inspiração para:
- local-first AI workspace;
- model cockpit;
- local models;
- MCP/tools;
- cookbook de modelos;
- deep research;
- memory/skills;
- UX de bancada pessoal de IA.

Odysseus não é dependência do AIW neste momento.

## Documentação operacional

Manuais detalhados (Runbooks) do funcionamento real das camadas:

* [Tool Runtime Phase 3](docs/runbooks/AIW_TOOL_RUNTIME_PHASE3.md)
* [LiteLLM Tool Calling Investigation](docs/runbooks/AIW_LITELLM_TOOL_CALLING_INVESTIGATION.md)
* [Cockpit Tool Runtime Integration](docs/runbooks/AIW_COCKPIT_TOOL_RUNTIME_INTEGRATION.md)
* [Cockpit Tool Runtime Validation](docs/runbooks/AIW_COCKPIT_TOOL_RUNTIME_VALIDATION.md)
* [File OS Phase 3D](docs/runbooks/AIW_FILE_OS_PHASE3D.md)
* [Project Write Mode Phase 3D.2](docs/runbooks/AIW_PROJECT_WRITE_MODE_PHASE3D2.md)
* [Agent Offline Mode](docs/runbooks/AIW_AGENT_OFFLINE_MODE.md)
* [Cockpit Execution Harness](docs/runbooks/AIW_COCKPIT_EXECUTION_HARNESS.md)
* [Tool Evidence Console](docs/runbooks/AIW_COCKPIT_TOOL_EVIDENCE_CONSOLE.md)
* [Cockpit Operational View](docs/runbooks/AIW_COCKPIT_OPERATIONAL_VIEW.md)
* [Cockpit Navigation and Local Search](docs/runbooks/AIW_COCKPIT_NAVIGATION_SEARCH.md)
* [Context Pack v1](docs/runbooks/AIW_CONTEXT_PACK_V1.md)
* [Agent Context Injection](docs/runbooks/AIW_AGENT_CONTEXT_INJECTION.md)
* [Workspace-Scoped Artifacts](docs/runbooks/AIW_WORKSPACE_SCOPED_ARTIFACTS.md)
* [External Workspace Agent Execution](docs/runbooks/AIW_EXTERNAL_WORKSPACE_AGENT_EXECUTION.md)
* [Workspace Onboarding](docs/runbooks/AIW_WORKSPACE_ONBOARDING.md)
* [Profile Test Runner](docs/runbooks/AIW_PROFILE_TEST_RUNNER.md)
* [Test Run History](docs/runbooks/AIW_TEST_RUN_HISTORY.md)
* [Patch-Aware Test Suggestions](docs/runbooks/AIW_PATCH_AWARE_TEST_SUGGESTIONS.md)
* [Source Root Test Mapping](docs/runbooks/AIW_SOURCE_ROOT_TEST_MAPPING.md)
* [Validation Plan](docs/runbooks/AIW_VALIDATION_PLAN.md)
* [Validation Plan Snapshots](docs/runbooks/AIW_VALIDATION_PLAN_SNAPSHOTS.md)
* [Agent Iterative Loop Offline v1](docs/runbooks/AIW_AGENT_ITERATIVE_LOOP.md)
* [Agent Loop Regression Smoke](docs/runbooks/AIW_AGENT_LOOP_REGRESSION_SMOKE.md)
* [AIW Isolation Boundary](docs/runbooks/AIW_ISOLATION_BOUNDARY.md)
* [AIW Safe Search Guard](docs/runbooks/AIW_SAFE_SEARCH.md)

## Próximos Passos (Roadmap Resumido)

1. Seleção e ranking de Context Pack avançado;
2. Profiles de projeto / task vinculados a contextos específicos;
3. Workspace Multi-Project na interface do Cockpit;
4. Fluxo de aprovação humana hiper-refinado;
5. Especialização e Worker Pools dedicados (Architect, Validator, Integrator);
6. Fluxo robusto de Git e Integração Contínua (PR Workflow);
7. RAG lexical puramente assistido -> Migração futura para RAG vetorial profundo;
8. Hermes integration deixado em standby apenas para quando e se for estritamente viável operá-lo semanticamente na stack atual.

*(Veja o arquivo completo em `ROADMAP.md` e o snapshot situacional em `docs/snapshots/SNAPSHOT_AIW_2026-06-29.md`).*

- [Patch Review Gate](docs/runbooks/AIW_PATCH_REVIEW_GATE.md) avalia segurança de apply.

- [Patch Test Coverage Intent](docs/runbooks/AIW_PATCH_TEST_COVERAGE_INTENT.md) avalia intenção de cobertura.

- [Coverage Report Adapter](docs/runbooks/AIW_COVERAGE_REPORT_ADAPTER.md) adapta relatórios LCOV/XML.

- [Coverage Run Capture](docs/runbooks/AIW_COVERAGE_RUN_CAPTURE.md) captura coverage e usa thresholds.

- [Coverage Baseline and Diff](docs/runbooks/AIW_COVERAGE_BASELINE_DIFF.md) define baselines locais manuais e compara diffs.

- [Changed Lines Coverage](docs/runbooks/AIW_CHANGED_LINES_COVERAGE.md) restringe análise de cobertura exclusivamente às linhas afetadas pelo patch.
- [AIW Patch Evidence Bundle](docs/runbooks/AIW_PATCH_EVIDENCE_BUNDLE.md)
- [AIW Patch Evidence Export](docs/runbooks/AIW_PATCH_EVIDENCE_EXPORT.md)
- [AIW Integration Outbox](docs/runbooks/AIW_INTEGRATION_OUTBOX.md)
- [AIW Integration Worker CLI](docs/runbooks/AIW_INTEGRATION_WORKER_CLI.md)
- [AIW GitHub Intake CLI](docs/runbooks/AIW_GITHUB_INTAKE_CLI.md)
- [AIW Agent Run Queue](docs/runbooks/AIW_AGENT_RUN_QUEUE.md)
- [AIW LLM Queue Execution Guard](docs/runbooks/AIW_LLM_QUEUE_EXECUTION_GUARD.md)
- [AIW Agent Patch Review & Apply Flow](docs/runbooks/AIW_AGENT_PATCH_REVIEW_FLOW.md)
- [AIW GitHub Worker Policy Integration](docs/runbooks/AIW_GITHUB_WORKER_POLICY_INTEGRATION.md)
- [AIW Foreground Worker Loop](docs/runbooks/AIW_FOREGROUND_WORKER_LOOP.md)
- [AIW Agent Queue Foreground Dispatcher](docs/runbooks/AIW_AGENT_QUEUE_FOREGROUND_DISPATCHER.md)
- [AIW End-to-End Dummy PR Smoke](docs/runbooks/AIW_END_TO_END_DUMMY_PR_SMOKE.md)
- [AIW Agent Capability Layer](docs/architecture/AIW_AGENT_CAPABILITY_LAYER.md)
- [AIW Agent Capability Roadmap](docs/roadmap/AIW_AGENT_CAPABILITY_ROADMAP.md)
- [AIW Agent Capability Foundation Runbook](docs/runbooks/AIW_AGENT_CAPABILITY_FOUNDATION.md)
- [AIW Tool Registry](docs/runbooks/AIW_TOOL_REGISTRY.md)
- [AIW Context RAG Local Index](docs/runbooks/AIW_CONTEXT_RAG_LOCAL_INDEX.md)
- [AIW Context Pack Builder](docs/runbooks/AIW_CONTEXT_PACK_BUILDER.md)
- [AIW CodeAct Sandbox](docs/runbooks/AIW_CODEACT_SANDBOX.md)
