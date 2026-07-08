# AI Workbench (AIW) — Architecture

**Status:** RFC v0.2 (Approved direction) | Code alignment in progress (Phase 2-4)  
**Date:** 2026-07-07 | Last update: delegation + integration of router/profiles/policy in main loop  
**Vision:** A powerful, self-hosted AI Engineering Harness (in the spirit of Manus, Devin, Claude Code, OpenHands, etc.) with **full control**, no commercial usage limits, no vendor lock-in, and security/isolation by design.

---

## 1. What is AIW?

AIW is **not** a wrapper around an LLM.

It is a **platform** that turns any LLM (API or local) into a significantly more powerful software engineering agent by providing the surrounding infrastructure:

- Context & Memory
- Planning
- Controlled Execution
- Isolation & Policies
- Pluggable Providers (Model / Execution / Context)
- Observability & Experimentation

The LLM is just one replaceable component. The power comes from the harness around it.

**Goals:**
- Use the best models available (OpenRouter, OpenAI, Anthropic, Gemini, DeepSeek, GLM, Ollama, vLLM, future providers) without changing architecture.
- Full local control and privacy.
- No artificial limits (tokens, hours, credits).
- Strong security and isolation by default.
- Continuous experimentation with new models and strategies.
- Become the primary development tool for serious engineering work.

**Detailed contracts:** [docs/interfaces/](../interfaces/)  
**How-to guides:** [docs/guides/](../guides/)  
**Full docs navigation:** [docs/INDEX.md](../INDEX.md)

**Note on cleanup**: Obsolete and historical documentation has been moved to `historical/` folders across the docs tree. See `docs/INDEX.md` for the current clean structure.

**Product Vision (Manus / Devin inspired, self-hosted)**
- Powerful autonomous engineering agent harness with full local control.
- Strong security/isolation gates on every action.
- Pluggable everything via Provider-First design.
- Tools & working style: LLM-planned iterative loops, profile-driven routing, gated execution providers, memory/context accumulation, systematic experimentation.

**Current Alignment Status (2026-07-08, após passos de migração 1-4)**:
- `aiw/` structure solid: interfaces, providers (Model/OpenRouter real registrado + usado, Execution/CodeAct migrado completamente + Docker/Devcontainer), **Roteador de Modelo** + **Perfis de Agente**, policy, **Loop Iterativo do Agente** (primário em aiw/agent/iterative_loop.py: iterações reais, replanejamento com contexto, execution_trace estruturado, rich actions via tools, retry, Execução Real com confirm, persistência de runs).
- Cockpit é a interface principal para desenvolvimento real: formulário com seleção de **Perfil de Agente** + modelo OpenRouter explícito, executa via novo loop, exibe trace renderizado + "Re-executar com mesma tarefa".
- Legacy `aiw_workspace/`: reduzido via thin delegates (~25+ arquivos pesados remanescentes em coverage/patch/test/validation/worker flows). Vários módulos high-value (github/integration/patch/evidence) migrados para aiw/ com delegates.
- Migração: Avançada nos componentes que habilitam uso real (CodeAct, loop core, router/profiles/providers, cockpit wiring). Foco em não quebrar operacional.
- Progresso recente: Loop + Cockpit + Perfis + Provedores prontos para tarefas reais de dev. "Right way" documentado em README (seção "Como usar o AIW para desenvolvimento real hoje").
- Overall: Usável **hoje** via Cockpit + Perfil de Agente + OpenRouter para desenvolvimento real (gated, traceável). ~75% alinhado no núcleo de agente. Gaps remanescentes em fluxos legados pesados (PR/patch full, experiment lab avançado).
- Visão: Self-hosted como Manus/Devin com controle total + security por design via Provider-First. Foco atual: refinar Loop Iterativo do Agente, Execução Real e completar delegates.

See MIGRATION.md para tracking de fases e partes usáveis. O fluxo recomendado é Cockpit + Loop Iterativo do Agente.

---

## 2. Core Principles

- **Provider First** — The Provider Layer is a foundational pillar.
- **Never couple logic to a specific provider.**
- **Three distinct provider types** from day one.
- **Model Router** is a first-class intelligent layer (including AUTO mode).
- **Everything must be pluggable.**
- **Policy + Isolation** gate every important decision.
- Local models are first-class citizens.
- The architecture must enable continuous experimentation.

---

## 3. Architecture Layers (Provider-First)

```
Core
  ↓
Workspace Management
  ↓
Provider Layer (Pillar)
  ├── Model Providers
  ├── Execution Providers
  └── Context Providers
  ↓
Model Router (with AUTO mode)
  ↓
Agent Runtime
  ↓
Planner
  ↓
Execution
  ↓
Memory
  ↓
Context / RAG
  ↓
Policy + Isolation + Capability Registry
  ↓
Queue + Persistence + Observability
  ↓
CLI / Cockpit / UI
```

---

## 4. Provider Types (Three Categories)

### 4.1 Model Providers
Generate reasoning / text.

Examples:
- OpenRouter (multi-model)
- OpenAI
- Anthropic
- Gemini
- DeepSeek, GLM
- Azure OpenAI
- Ollama, LM Studio, vLLM, local models
- Future providers

Each provider can expose multiple models.

### 4.2 Execution Providers
Perform actions in the environment.

Current / future:
- CodeAct (Python sandbox)
- Devcontainer
- Docker
- VM
- Claude Code style
- OpenHands style
- Native Shell / Filesystem
- Browser tools
- Future specialized executors

### 4.3 Context Providers
Supply knowledge to the agent.

Examples:
- Local Filesystem + RAG
- Git repository
- Documentation / Markdown
- GitHub / Jira / Linear
- Obsidian vault
- Vector databases
- SQL databases
- Confluence / internal wikis
- Future sources

---

## 5. Key Components

### Model Router
Intelligent selection layer.

Responsibilities:
- Choose provider + model
- Choose temperature, reasoning effort, context window
- Cost / speed / quality tradeoffs
- Fallback strategies
- **AUTO mode**: Given a task + constraints, decide the best combination dynamically

Example:
- "Refactor large module" → Claude Sonnet / Opus
- "Generate unit tests" → DeepSeek or local fast model
- "Security review" → Strong reasoning model
- "AUTO" → Router decides

### Agent Profiles
Specialized agent personas (inspired by Manus).

Examples:
- Software Engineer
- Security Analyst
- Code Reviewer / Architect
- Performance Engineer
- Data Engineer
- DevOps
- Researcher
- Technical Writer

Each profile defines:
- Preferred Planner
- Allowed Model Providers
- Tools / Capabilities
- Temperature & parameters
- System prompts
- Context strategy
- Required isolation level

See `docs/interfaces/agent-profile.md` and `docs/guides/adding-agent-profile.md`.

### Experiment Lab
Dedicated module for benchmarking, comparison, and data collection. Critical for making AUTO mode intelligent over time and for safely onboarding new providers.

---

## 5.1 Textual Architecture Diagram (Target)

```
User (Cockpit / CLI)
        │
        ▼
Agent Profile (defines defaults + constraints)
        │
        ▼
Agent Runtime
        │
        ├─► Model Router (AUTO or specific)
        │        │
        │        ▼
        │   Model Provider (OpenRouter / Ollama / Anthropic / ...)
        │
        ├─► Planner (uses context + profile)
        │
        ▼
Execution Layer
        │
        ▼
Execution Provider (CodeAct / Docker / Devcontainer / ...)
        │
        ▼
Context Layer ← Context Providers (RAG / Git / Docs / Jira / ...)
        │
        ▼
Policy + Isolation + Capability Registry (gates every step)
        │
        ▼
Persistence + Queue + Observability + Experiment Lab
```

All layers above the Provider Layer must remain provider-agnostic.

### Experiment Lab
Dedicated module for continuous experimentation (major differentiator).

Capabilities:
- Model / Provider benchmarks
- Arena (head-to-head comparison)
- Prompt A/B testing
- Cost, latency, and quality analysis
- Regression testing across models
- New provider onboarding tests

---

## 6. Current State Mapping (July 2026)

**Existing pieces that align with target:**
- Capability Registry + Policy + Isolation Boundary + Runtime Gate
- Execution Providers (CodeAct migrado completamente + Docker/Devcontainer em `aiw/providers/execution/`)
- **Loop Iterativo do Agente** primário (`aiw/agent/iterative_loop.py`: iterações, replanejamento, rich actions com file_write/patch/git via tools, retry, `execution_trace` estruturado, Execução Real com confirm)
- Roteador de Modelo + Perfis de Agente (profile-driven routing para OpenRouter/litellm + execution_provider)
- Model Providers (OpenRouter registrado e usado)
- aiw_context (Context Pack, Index, Search — foundation for Context/RAG)
- Workspace profiles + path hygiene + Safe Search
- Queue, Worker Loop, Dispatcher, GitHub Intake (com thin delegates em vários casos)
- Cockpit + artifact system (observability foundation) — formulário com **Perfil de Agente** + modelo OpenRouter, trace rico + re-exec

**Alinhamento do fluxo real de desenvolvimento (tarefa real → trace com edição → resultado):**
- Cockpit form → escolhe **Perfil de Agente** (`software-engineer`) + modelo OpenRouter explícito → `run_agent_iterative_loop_once(execute=..., profile=..., model=...)`.
- Router decide → LLMPlanner (ou mock) → despacho ao **Provedor de Execução** (codeact).
- Execução Real (confirm) produz side-effects seguros (ex: `file_write` em `.aiw/generated/*` via aiw_runtime.tools) → trace registra `status: "executado"`, `mode: "Execucao_Real"`, stdout com `bytes_written` + path, policy.
- UI mostra collapsibles + destaques de arquivos editados; botão re-exec preserva Perfil + modelo.
- Persistência + list/read via aiw/agent (independente de legado para o core).

Exemplo concreto (tarefa que gera edição):
Tarefa: "Liste os principais arquivos e diretórios do projeto e crie um resumo em .aiw/generated/... usando o Provedor de Execução."
Resultado no trace (resumido):
```json
{
  "router_decision": {"provider": "openrouter", "model": "openai/gpt-oss-120b:free", "profile_used": "software-engineer"},
  "profile": {"name": "software-engineer", "execution_provider": "codeact", ...},
  "execution_trace": [
    {"iteration":1, "kind":"codeact_python_eval", "status":"executado", "success":true, "provider":"codeact", "mode":"Execucao_Real",
     "result": {"stdout": "... 'tool': 'file_write', 'path': '.aiw/generated/...', 'bytes_written': N ..."}}
  ],
  "has_real_execution": true
}
```
Re-executa → novo run reutilizando Perfil de Agente + modelo. Ver `.aiw/generated/` e o run.json persistido.

**Problemas / gaps remanescentes:**
- `aiw_workspace` ainda contém lógica pesada (thinned delegates em ~25+ arquivos para coverage/patch/test/validation/workers).
- Algumas integrações de patch/PR completas ainda dependem de CLI legado.
- Migração cirúrgica em andamento (foco em não quebrar operacional + Cockpit/Loop).

O núcleo Provider-First + Loop Iterativo do Agente + Cockpit está alinhado e usável para desenvolvimento real hoje.

---

## 7. Target Package Structure (Proposed)

```
aiw/
├── core/                  # Shared primitives, schemas, security basics
├── workspace/             # Workspace resolution, profiles, path hygiene
├── providers/
│   ├── model/             # ModelProvider interface + implementations
│   ├── execution/         # ExecutionProvider interface + CodeAct, etc.
│   └── context/           # ContextProvider interface + RAG, Git, etc.
├── router/                # Model Router + AUTO logic
├── profiles/              # Agent Profiles
├── agent/                 # Agent Runtime + main loops
├── planner/               # Planner implementations (mock, LLM-based, graph, ...)
├── execution/             # Execution orchestration layer
├── memory/                # Long-term memory
├── context/               # Context/RAG orchestration
├── policy/                # Capability, Isolation, Runtime policies
├── experiment/            # Experiment Lab (benchmarks, arena, A/B)
├── queue/                 # Task queue, workers
├── persistence/           # Run storage, artifacts
├── observability/         # Logging, tracing, evidence
└── interfaces/            # Public contracts (recommended)
```

Legacy `aiw_workspace/`, `aiw_runtime/`, `aiw_context/`, `aiw_langgraph/` will be gradually migrated or deprecated.

---

## 8. High-Level Migration Roadmap

1. **Foundation (Docs + Structure)**
   - Finalize this Architecture document
   - Create target directory structure
   - Define public interfaces

2. **Provider Layer**
   - Extract and generalize Execution Provider
   - Introduce Model Provider abstraction (on top of current LiteLLM usage)
   - Introduce Context Provider concept

3. **Router + Profiles**
   - Implement Model Router (with AUTO)
   - Implement Agent Profiles

4. **Experiment Lab**
   - Build dedicated experimentation module

5. **Reorganization**
   - Break up `aiw_workspace` monolith
   - Clean legacy (langgraph move to experiments, outdated docs)
   - Make Cockpit and CLIs consume only public interfaces

6. **Advanced Capabilities**
   - Multiple real Execution Providers
   - Stronger runtime isolation (devcontainer, docker, vm)
   - Full Experiment Lab features

---

## 9. Non-Goals / Anti-Patterns

- Do not tie core logic to any specific LLM provider.
- Do not hide policy/decision logic inside graphs or frameworks.
- Do not treat the monolith as permanent.
- Do not add new major features on top of the current tangled structure without following this architecture.

---

**This document is the current constitution for AIW architecture.**

All future work (repo organization, code changes, documentation, UI) should align with the layers, provider types, Model Router, Agent Profiles, and Experiment Lab defined here.

Next steps will focus on documentation + repo structure alignment, then incremental refactoring.