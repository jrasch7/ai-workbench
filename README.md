# AI Workbench (AIW)

**AIW is a powerful self-hosted AI Engineering Harness** — inspired by Manus, Devin, Claude Code, OpenHands and similar agent platforms — but designed as **your own controllable product**.

## Product Vision
- **Full control & no limits**: Self-hosted, no vendor lock-in, no usage caps, no external telemetry.
- **Security & isolation by design**: Every action goes through Policy, Isolation Boundary and Runtime Gates.
- **Provider-First architecture**: Pluggable Model Providers (OpenRouter, local, etc.), Execution Providers (CodeAct, Docker, Devcontainer), Context Providers.
- **Intelligent routing & profiles**: Model Router (AUTO mode) + Agent Profiles that drive model choice, execution environment, tools and LLM planning permission.
- **Real engineering power**: Iterative LLM planning + gated execution, tools (code, git, web, file ops), memory, context, Experiment Lab for systematic testing.
- **Experimentation first**: Test new models, strategies and providers safely.

The LLM is just a replaceable brain. The **harness** (providers, router, policy, memory, execution, observability) turns it into a reliable software engineering agent.

Current inspiration: bring the autonomy and breadth of Manus/Devin to a fully private, auditable, self-hosted environment with strong guardrails.

See **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** for the complete target layers and **[docs/MIGRATION.md](docs/MIGRATION.md)** for the migration path.

## Current Capabilities & Way of Working (2026-07)

**Core Loop (Provider-First)**
- **Loop Iterativo do Agente** com planejamento LLM-driven (OpenRouter + **Perfis de Agente**) + despacho real a **Provedores de Execução**.
- **Roteador de Modelo** (AUTO) + **Perfis de Agente** que controlam modelos permitidos, Provedor de Execução (codeact/docker/devcontainer), tools e se planejamento LLM real é permitido.
- Policy + Isolation + Runtime Gates fortes em toda ação.

**Tools & Execution**
- Execution Providers: CodeAct (primary), Docker & Devcontainer (improved stubs with realistic dry-run + basic execution).
- Tools: file ops, shell, git (log/diff), web_search (live attempt with graceful stub), code execution.
- Memory layer started (short-term + long-term stubs) integrated into the loop.

**Experimentation & Safety**
- Experiment Lab (benchmarks + arena across profiles/providers).
- Full dry-run / offline modes + evidence.
- Everything gated; nothing executes without confirmation when risky.

**Way of working**
1. Profile + task → Router chooses provider/model.
2. LLM Planner produces structured steps (or fallback).
3. Loop dispatches steps to the right Execution Provider + tools, accumulating context and memory.
4. Policy gates + isolation enforced at every step.
5. Results recorded; Experiment Lab used to measure and improve.

See recent progress in the Architecture document and the wiring in `aiw/agent/iterative_loop.py`.

**Hoje (usável)**: Cockpit + Loop Iterativo do Agente com **refatorações precisas** (LLM faz file_read + emite old_text/new_text exatos → project_patch_preview em fontes reais) + execução real (file_write / patch apply via aiw_runtime/tools) + "Aplicar patch seguro" com resultado inline no trace (sem reload). 

Exemplo completo e fluxo de 5 passos aplicados em `docs/MIGRATION.md`. Regression smoke agora cobre o fluxo inteiro "editar + preview + apply + validate".

Use:
```bash
./scripts/aiw-cockpit
# ou
./scripts/aiw-agent-loop --workspace aiw --task "refatore funcao Y (leia primeiro) e valide" --execute --confirm-agent-loop --profile software-engineer --max-iterations 2
```

Key OpenRouter melhora o planejamento LLM; o caminho de execução real funciona mesmo com fallback mock.

**Target architecture & migration**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/MIGRATION.md](docs/MIGRATION.md).

**Do not add major new features to the legacy monolith (`aiw_workspace/`).** New code targets the `aiw/` structure.

## Security & Working Principles

- Everything is gated by Policy / Isolation Boundary / Runtime Gate.
- Prefer dry-run and evidence.
- New development targets the clean `aiw/` Provider-First packages.
- Legacy lives in `aiw_workspace/` only during the migration bridge.

See the full current state, tools, and how we work in:
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/guides/](docs/guides/)
- Recent code in `aiw/agent/`, `aiw/providers/`, `aiw/memory/`, `aiw/experiment/`

## Useful commands (current)

```bash
# Inicie o Cockpit (interface principal para desenvolvimento real com Loop Iterativo do Agente)
./scripts/aiw-cockpit

# Listar Provedores de Execução (codeact + docker + devcontainer)
./scripts/aiw-execution-provider --list

# Listar Perfis de Agente disponíveis
python3 -c 'from aiw import list_profiles; print(list_profiles())'

# Loop via CLI (equivalente para automação; prefira Cockpit para escolher modelo OpenRouter + perfil)
./scripts/aiw-agent-loop --workspace aiw --task "..." --profile software-engineer --execute --confirm-agent-loop --max-iterations 4 --once
```

Para fluxos operacionais completos e runbooks, consulte os scripts e `docs/runbooks/`.

## Como usar o AIW para desenvolvimento real hoje

O **Cockpit** (`./scripts/aiw-cockpit`) é a interface principal recomendada para desenvolvimento real com o AIW.

O núcleo é o **Loop Iterativo do Agente** (implementado primariamente em `aiw/agent/iterative_loop.py`):

- Escolha de **Perfil de Agente** (ex: `software-engineer`) + seleção explícita de modelo **OpenRouter**.
- **Roteador de Modelo** (AUTO) decide provider/model com base no perfil + tarefa.
- **Planejador LLM** (real quando chave OpenRouter presente e `llm_planning_allowed` no perfil) ou mock.
- Múltiplas iterações com replanejamento usando resultados + contexto acumulado.
- Despacho ao **Provedor de Execução** (CodeAct primário, também Docker/Devcontainer) com **Execução Real** (quando `--execute` / botão real + `confirm_agent_loop` + policy permite).
- `execution_trace` estruturado (por iteração/passo: status como "simulado"/"executado"/"concluido_llm"/"erro", policy, retries, resultados, ferramentas).
- Persistência de runs em `.aiw/workspaces/<ws>/agent-iterative-loop/runs/`.
- Integração com Memória (curto/longo prazo).

**Caminho recomendado**: Cockpit + **Perfil de Agente** + modelo OpenRouter. O `aiw-agent-loop` CLI é equivalente para automação/scripts.

Uso temporário de outros harnesses (ex: OpenHands local, Aider, Cursor) é aceitável para tarefas pontuais durante migração, mas **o Loop Iterativo do Agente + Cockpit é o caminho principal** para desenvolvimento real no AIW.

### 1. Inicie o Cockpit

```bash
./scripts/aiw-cockpit
```

Acesse `http://127.0.0.1:8765` (ou a porta em `AIW_COCKPIT_PORT`).

O Cockpit é a UI principal:
- Formulário de **Loop Iterativo do Agente** (seção destacada na home):
  - Textarea para tarefa em linguagem natural.
  - **Perfil do Agente** (seleção clara): `software-engineer` (recomendado), `security-analyst`, `code-reviewer`.
  - **Modelo OpenRouter** (seleção explícita): `openai/gpt-oss-120b:free`, `anthropic/claude-3.5-sonnet`, `openai/gpt-4o`, `meta-llama/llama-3.3-70b-instruct:free` etc.
  - Workspace (padrão "aiw"; outros via config).
- Botões:
  - "Executar Loop Iterativo do Agente (execute=True)" → **Execução Real** (sujeita a policy + confirm).
  - "Loop Iterativo (offline)" → dry-run / simulação segura.
- Resultado pós-submit: página dedicada com resumo (run_id, status, perfil, modelo, iterações) + `execution_trace` renderizado (collapsibles por iteração, destaques de paths de arquivos, status por passo).
- Botão "Re-executar com mesma tarefa" preserva perfil + modelo escolhidos.
- Listagem de runs recentes do Loop Iterativo do Agente na home.

### 2. Configure OPENROUTER_API_KEY (para LLM real + planejamento)

```bash
export OPENROUTER_API_KEY=sk-or-v1-...
# ou coloque em .env (seu .env.example ou similar) e exporte
```

- Para modelos pagos: recarregue créditos em https://openrouter.ai/credits .
- Modelos `:free` funcionam sem recarga (sujeitos a limites do provedor).
- Sem chave válida: cai automaticamente em planner mock + simulações (ainda útil para explorar o fluxo).

## Resumo Análise do Sistema (2026-07-08, pós 5 passos via subagentes)
- Loop Iterativo do Agente: Refinado (ações ricas, retry, trace completo, Exec Real).
- Cockpit: Integrado e melhorado (form Perfil+modelo, trace bonito, re-exec).
- Migração: Cirúrgica (integration/patch em aiw/, delegates).
- Docs: Atualizados com fluxo prático, PT terms, usáveis vs gaps.
- Estado: ~75% alinhado, usável para dev real via interface. Gaps: migração full, exec autonomous total. Foco "do jeito certo".

Full docs: ARCHITECTURE.md + MIGRATION.md.

### 3. Fluxo prático para desenvolvimento real (hoje)

1. Rode `./scripts/aiw-cockpit`.
2. No formulário do Loop:
   - Perfil: `software-engineer` (habilita LLM planning + Provedor de Execução codeact).
   - Modelo: inicie com `openai/gpt-oss-120b:free`.
   - Tarefa: ex: "Analise o módulo aiw/agent/iterative_loop.py e sugira 2 melhorias concretas de código sem editar arquivos."
3. Clique **"Executar Loop Iterativo do Agente (execute=True)"** (ou offline para dry).
4. Aguarde o processamento (planejamento + 1-N iterações + dispatch).
5. Na página de resultado veja:
   - `router_decision` (provider, model, rationale do Perfil de Agente).
   - Planos por iteração (`plan_iteration_N`).
   - **`execution_trace`**: array detalhado com `status`, `result`, policy, retries, provider, timestamps.
   - Contexto acumulado e resumo.
6. Itere: use "Re-executar com mesma tarefa" ou volte e refine a tarefa com "baseado no trace anterior...".

**Via CLI (mesmo Loop, para scripts/automação):**

```bash
./scripts/aiw-agent-loop \
  --workspace aiw \
  --task "Liste arquivos .py principais e resuma o objetivo do projeto" \
  --profile software-engineer \
  --execute \
  --confirm-agent-loop \
  --max-iterations 3
```

- Sem `--execute`: dry-run (simulação via Provedor de Execução).
- `--execute --confirm-agent-loop`: habilita **Execução Real** (ações podem escrever em `.aiw/generated/*`, usar tools git/file via aiw_runtime, etc., sempre gateadas por Policy).
- Perfil `code-reviewer` força `llm_planning_allowed=false` (plano mock determinístico).

**max-iterations** 3-5 é típico para tarefas reais.

### Exemplo completo de fluxo de desenvolvimento real: "tarefa real → trace com edição → resultado"

Este é o fluxo acionável recomendado para desenvolvimento real usando o **Loop Iterativo do Agente**.

#### Passo a passo no Cockpit (interface principal)

1. Inicie o Cockpit:
   ```bash
   ./scripts/aiw-cockpit
   ```
   Acesse `http://127.0.0.1:8765`.

2. Localize o formulário **"Executar Agente Direto - Loop Iterativo do Agente (Perfil de Agente + Execução Real)"**.

3. Preencha:
   - **Tarefa** (textarea): `Liste os principais arquivos e diretórios do projeto (top 8) e crie um arquivo de resumo em .aiw/generated/resumo-estrutura.md listando-os com contagem, usando ferramentas reais do Provedor de Execução.`
   - **Perfil de Agente**: `software-engineer` (habilita `llm_planning_allowed=true`, tools incluindo `file_write`, `execution_provider=codeact`).
   - **Modelo OpenRouter** (explícito): `openai/gpt-oss-120b:free` (ou `anthropic/claude-3.5-sonnet`, `meta-llama/llama-3.3-70b-instruct:free` etc.).
   - Workspace: `aiw` (padrão).

4. Submeta:
   - Clique **"Executar (Execução Real)"** (usa `execute=True` + `confirm_agent_loop=True` internamente → **Execução Real**).
   - Ou primeiro teste com **"Executar (Offline / Dry-run)"** (sem side-effects).

5. Observe o processamento:
   - Roteador de Modelo decide com base no **Perfil de Agente** + tarefa.
   - Planner produz plano (LLM se chave + perfil permite, senão mock).
   - Múltiplas iterações: despacho de passos ricos ao **Provedor de Execução** (codeact), com retry, policy gates e contexto acumulado.

6. Resultado imediato na página dedicada:
   - Cabeçalho com meta: Status, **Perfil de Agente**, Modelo, Provider (Provedor de Execução), "Execução Real: ✓", iterações.
   - `router_decision`, `plan_iteration_N`.
   - **`execution_trace`** renderizado (collapsibles por iteração, status por passo como "executado", badges de sucesso, spans com 📄 paths de arquivos modificados/criados).
   - Seção de Contexto Acumulado.
   - Links: "Ver JSON do run", API direta.
   - **Botão "Re-executar com mesma tarefa"** — preserva automaticamente o **Perfil de Agente** + modelo OpenRouter escolhidos e re-submete.

7. Verifique o resultado da edição real (side-effect controlado):
   ```bash
   ls -l .aiw/generated/ | grep resumo
   cat .aiw/generated/resumo-estrutura.md
   # (backups automáticos em .aiw/backups/ para writes)
   ```
   O arquivo foi criado por `file_write` via `aiw_runtime.tools` dentro de uma ação `python_eval` despachada pelo Provedor de Execução.

8. Re-execute:
   - Clique "Re-executar com mesma tarefa" (ou volte ao form principal e refine a tarefa, mantendo Perfil + modelo).
   - Observe novo `run_id`, possivelmente mais iterações ou refinamento pelo contexto acumulado do run anterior.

#### Exemplo de `execution_trace` (com Execução Real e edição via Provedor de Execução)

```json
{
  "run_id": "ail-d82d7acb",
  "workspace_id": "aiw",
  "mode": "execute",
  "status": "completed",
  "planner": "llm",
  "task": "Liste os principais arquivos e diretórios do projeto (top 8) e crie um arquivo de resumo em .aiw/generated/resumo-estrutura.md ...",
  "router_decision": {
    "provider": "openrouter",
    "model": "openai/gpt-oss-120b:free",
    "rationale": "...",
    "profile_used": "software-engineer"
  },
  "profile": {
    "name": "software-engineer",
    "execution_provider": "codeact",
    "llm_planning_allowed": true,
    "tools": ["file_read", "file_write", "codeact_sandbox", ...]
  },
  "chosen_model": "openai/gpt-oss-120b:free",
  "chosen_provider": "openrouter",
  "chosen_execution_provider": "codeact",
  "has_real_execution": true,
  "plan_iteration_1": { "planner": "llm", "steps": [ ... ], "should_continue": false },
  "execution_trace": [
    {
      "iteration": 1,
      "kind": "inspect_context",
      "title": "Inspecionar contexto",
      "status": "executado",
      "success": true,
      "provider": "codeact",
      "mode": "Execucao_Real",
      "result": { "inspecao": { "tool": "directory_list", "entries": [...] } },
      "policy_decision": { "allowed": true, "reason": "offline_confirmed_fixed_codeact_eval" }
    },
    {
      "iteration": 1,
      "kind": "codeact_python_eval",
      "title": "Executar via CodeAct",
      "status": "executado",
      "success": true,
      "provider": "codeact",
      "mode": "Execucao_Real",
      "retries": 0,
      "input": { "action": { "kind": "python_eval", "source": "generated_default_tool_use" } },
      "result": {
        "status": "completed",
        "returncode": 0,
        "stdout": "...\n{'ok': True, 'tool': 'file_write', 'path': '.aiw/generated/loop_iter1_Executar_via_CodeAct.log', 'bytes_written': 114, 'overwritten': true, ...}\n",
        "action": { "code": "from aiw_runtime.tools import ... file_write(...) ..." }
      },
      "policy_decision": { "allowed": true }
    },
    {
      "iteration": 1,
      "kind": "summarize",
      "title": "Resumir e evidenciar",
      "status": "concluido_fallback",
      "success": true
    }
  ],
  "total_iterations_executed": 1,
  "accumulated_context": "Tarefa inicial: ...\n[Iter 1][codeact_python_eval] ... file_write ...",
  "execution_provider_used": "codeact"
}
```

**Observações chave:**
- `status: "executado"` e `mode: "Execucao_Real"` indicam que o **Provedor de Execução** (codeact) executou com side-effects reais (file_write permitido em `.aiw/generated`).
- O trace destaca o path do arquivo editado/criado (visível também na UI do Cockpit).
- Re-execução cria novo run (novo `run_id`), reutilizando Perfil de Agente + modelo do form.
- Política (PolicyEngine) + Isolation + Runtime Gate sempre avaliam; `confirm_agent_loop` é obrigatório para Execução Real.

Resultados persistem em `.aiw/workspaces/aiw/agent-iterative-loop/runs/<run_id>/run.json` e são listáveis via `list_agent_loop_runs` / `read_agent_loop_run`.

Use este fluxo para tarefas reais de engenharia: inspeção → edits seguros → validação → re-iteração via re-exec ou nova tarefa com contexto.

### Notas importantes sobre estado atual (pós migração)

- **Provedor de Execução** primário: CodeAct (totalmente migrado em `aiw/providers/execution/`). Suporte a Docker/Devcontainer.
- **Execução Real** passa por Policy + Isolation + Runtime Gate; requer confirmação explícita.
- Integrações externas (GitHub Intake, workers, patch review) ainda exigem CLI dedicado na maioria dos casos (thinned delegates em aiw/ para vários).
- O Loop suporta re-planejamento, retries inteligentes, ferramentas via aiw_runtime (git, file, shell, web_search com guard).
- Listagem/histórico de runs do Loop Iterativo do Agente agora funcional via aiw/ (disco + memória).

### Usando outro harness temporariamente (ok, mas este é o caminho)

Para partes ainda em migração (ex: fluxos completos de PR/patch pesados), é aceitável usar temporariamente:
- Runners legados (`aiw-runner-agent`, `aiw-runner-once` com `AIW_AGENT_OFFLINE=1`).
- Invocações diretas de providers.
- Harnesses externos (OpenHands, Aider, Claude Code) — depois integre artefatos de volta.

**Mas para desenvolvimento real hoje: use Cockpit + Loop Iterativo do Agente.** É o fluxo estável, provider-first, com trace e policy.

Veja:
- [docs/MIGRATION.md](docs/MIGRATION.md) (estado da migração e partes usáveis).
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- `docs/runbooks/AIW_AGENT_ITERATIVE_LOOP.md`, `docs/guides/cockpit-interfaces.md`
- Runbooks de Policy, Execution Provider, etc. em `docs/runbooks/`.


## Foreground Worker Loop

O AIW possui um worker loop manual e foreground para processar Integration Outbox (parte ainda mais dependente de legado durante migração).

Ele não é daemon, não roda em background e grande parte não executa pela UI do Cockpit.

Fluxo (requer CLI explícito):

Integration Outbox item ready
→ dispatch.json explícito
→ Foreground Worker Loop
→ External Worker Policy
→ Integration Worker CLI
→ gh pr edit somente se permitido

Por padrão, roda em dry-run.
Execução real exige --execute e --confirm-worker-loop.

(Para o Loop Iterativo do Agente, prefira o Cockpit ou aiw-agent-loop como descrito acima.)

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
* [Agent Iterative Loop (Loop Iterativo do Agente)](docs/runbooks/AIW_AGENT_ITERATIVE_LOOP.md)
* [Agent Loop Regression Smoke](docs/runbooks/AIW_AGENT_LOOP_REGRESSION_SMOKE.md)
* [AIW Isolation Boundary](docs/runbooks/AIW_ISOLATION_BOUNDARY.md)
* [AIW Runtime Gate](docs/runbooks/AIW_RUNTIME_GATE.md)
* [AIW Execution Provider](docs/runbooks/AIW_EXECUTION_PROVIDER.md)
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
