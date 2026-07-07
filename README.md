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
- Agent Iterative Loop with LLM-driven planning (OpenRouter + profiles) + real dispatch to Execution Providers.
- Model Router (AUTO) + Agent Profiles that control allowed models, execution provider (codeact/docker/devcontainer), tools and whether real LLM planning is allowed.
- Strong Policy + Isolation + Runtime Gates on every action.

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
# Agent loop with current wiring (profile + router + providers)
./scripts/aiw-agent-loop --workspace sandbox-test --task "your engineering task" --profile software-engineer --dry-run --once

# List execution providers (codeact + docker + devcontainer)
./scripts/aiw-execution-provider --list

# Quick experiment
python3 -c 'from aiw.experiment import run_benchmark; print(run_benchmark(dry=True))'
```

For full operational cockpit and older flows, see the scripts and runbooks (many are historical).

## Como começar a usar o AIW HOJE para desenvolver (prioridade máxima agora)

Entendi perfeitamente. O objetivo mudou: **fazer o AIW útil para desenvolvimento real o mais rápido possível**, para você não precisar pular para Hermes/Odysseus hoje.

### Setup em 2 minutos:

1. Tenha `OPENROUTER_API_KEY` com saldo (recarregue agora se precisar).

2. Rode com execução real:

```bash
./scripts/aiw-agent-loop \
  --workspace seu-projeto \
  --task "Analise o código do módulo principal, identifique problemas e faça uma refatoração pequena e segura" \
  --profile software-engineer \
  --execute \
  --confirm-agent-loop \
  --max-iterations 5
```

O que o Loop Iterativo do Agente faz em modo real:
- Chama OpenRouter de verdade para planejar
- Executa múltiplas iterações
- Usa ferramentas reais (git, web, execução de código Python)
- O CodeAct provider pode fazer edições quando o plano pedir (sujeito à policy de segurança)
- Mostra execution_trace detalhado no final

Melhorias recentes para uso real:
- Ações mais úteis para desenvolvimento (não só prints)
- Suporte melhor a iterações com contexto acumulado
- Rastreamento claro do que foi executado

### Interface funcional (Cockpit - comece por aqui)

```bash
./scripts/aiw-cockpit
```

Agora tem:
- Formulário "Executar Agente Direto" com textarea para descrever a tarefa livremente.
- Seleção de perfil e workspace.
- Botão que chama o **novo Loop Iterativo do Agente** com execução real + OpenRouter.
- Resultados e execution_trace aparecem na seção Agent Iterative Loop.

Isso é o início de uma interface real. Podemos melhorar o formulário, adicionar live view, etc. rapidamente.

Se quiser, me diga uma tarefa específica ("Refatore o módulo Y para usar X") que eu preparo/testo o fluxo via código. 

Nenhum daemon externo roda por padrão.
Nenhuma ação GitHub/Jira é executada pela UI.
Toda integração externa exige CLI manual, confirmação explícita e policy permitindo.

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
