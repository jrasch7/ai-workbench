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

**Current Alignment Status (post 1-5 recent work, 2026-07)**:
- `aiw/` structure: interfaces, providers (Model/OpenRouter, Execution/CodeAct+Docker+Devcontainer, Context), router+perfis, policy, planner, **Loop Iterativo do Agente** (múltiplas iterações, re-planejamento, despacho real para provedores), experiment lab, memória, queue. Legacy further migrated (thinned worker_loop, agent_queue; CodeAct logic in aiw/).
- Legacy `aiw_workspace/`: still contains most operational code (29 files); key pieces are now thin delegates.
- Recent progress: execution dispatch wired + refined, docker/devcontainer adapters, memory integration, tools (web/git) wired, mover on queue.
- Overall alignment: ~65-70% toward clean runtime. Structure is being actively cleaned (empty layers now have status READMEs, historical docs isolated).

See MIGRATION.md for phase tracking. ROUND2 control file removed.

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
- Execution Provider (early stage, only CodeAct)
- Agent Iterative Loop (base for Agent Runtime)
- CodeAct Sandbox (core execution with strong guardrails)
- aiw_context (Context Pack, Index, Search — foundation for Context/RAG)
- Workspace profiles + path hygiene + Safe Search
- Queue, Worker Loop, Dispatcher, GitHub Intake
- Cockpit + artifact system (observability foundation)

**Problems to solve:**
- `aiw_workspace` is a large monolith mixing many concerns.
- CodeAct is still hardcoded in multiple places.
- No Model Router yet.
- No distinction of the three provider types.
- `aiw_langgraph` is an isolated experiment (not integrated).
- `aiw_runtime` is underutilized and unclear.
- Cockpit and scripts reach into internal modules.
- Lots of historical runbooks and aspirational docs that are out of date.

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