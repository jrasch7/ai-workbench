---
layout: decision
title: ADR - LangGraph Engineering Loop
---

# Decision Record: LangGraph Engineering Loop

**Date:** 2026-06-22

## Context
We are pausing the use of Paperclip as the primary engineering engine. Paperclip will be frozen as a spike/documentation reference.

## Decision
Adopt a deterministic engineering loop powered by **LangGraph** within the AI Workbench repository.

## Reasons
- Need deterministic orchestration for engineering tasks.
- LangGraph provides a clear state graph for planning, execution, testing, and feedback.
- Paperclip’s heuristic approach is less suitable for repeatable CI/CD pipelines.

## Paperclip Status
- Paperclip is **frozen**: no further development or execution.
- Existing documentation and code remain under `vendor/paperclip` for reference.

## Learnings from Paperclip Spike
- Rapid prototyping is valuable but lacks reproducibility.
- Integration with Hermes agents is possible but ad‑hoc.
- Testing hooks were manual; LangGraph will formalize them.

## Target Architecture
```
Context Loader → Planner → Executor → Test Runner → Failure Analyzer → Fix Loop → Final Report
```
LangGraph will orchestrate these components; individual executors such as Hermes/OpenCode/scripts/tests remain unchanged.

## Limits
- LangGraph **does NOT replace** the executor; it only coordinates.
- Heavy dependencies are avoided; LangGraph is the sole new requirement.
- No changes to external projects (Nivela, SisOpERP, Store).

## Implementation Plan (Spike)
1. Create a new branch `spike/langgraph-engineering-loop`.
2. Add the ADR file (this document).
3. Scaffold `aiw_langgraph/` package with core modules.
4. Add local engineering context docs.
5. Provide a simple smoke‑test script `scripts/aiw-langgraph-smoke`.
6. Generate a markdown report under `reports/langgraph-smoke/`.

---
