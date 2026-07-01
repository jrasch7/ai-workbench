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
```

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
