# Concept: Provider First

The defining characteristic of AIW.

Instead of building features around one model or one execution method, the architecture treats **providers as the primary extension point**.

## Why
- Avoid lock-in
- Support local + remote models equally
- Allow experimentation with new execution sandboxes
- Enable mixing different knowledge sources

## Three Provider Types
1. **Model Providers** — who thinks
2. **Execution Providers** — who acts
3. **Context Providers** — who knows

All other layers (Router, Planner, Agent, Policy) are built on top of these abstractions.
