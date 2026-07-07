# ADR: Free‑Tier Model Strategy

**Status:** Proposed

## Context
AIW needs to continue advancing without incurring cloud costs. Existing paid providers (Fugu, OpenAI) are out of scope for the immediate next phase.

## Decision
We will prioritize **free** or **free‑tier** model providers:
- Ollama local models (e.g., llama‑3.1‑8B) – always free on‑premise.
- OpenRouter free tier (e.g., `openrouter://anthropic/claude-3.5-sonnet:free`).
- Gemini free tier (via Google AI Studio) where available.
- Any other community‑hosted endpoints that do not require payment.

## Rationale
- Aligns with the project's budget constraints.
- Enables rapid iteration and benchmarking without financial gating.
- Provides a clear matrix for future evaluation when paid options become feasible.

## Consequences
- Limited token quotas may affect large‑scale runs; the harness will respect provider limits.
- Model capabilities may be lower than paid alternatives; we will capture these gaps in the roadmap.
- No integration of paid APIs; future phases can re‑evaluate when budgets allow.

## Pitfalls & Mitigations
- **Rate‑limit errors** – implement exponential back‑off and fallback to a secondary free provider.
- **Model hallucinations** – enforce a reviewer step that flags nonsensical outputs.
- **Local model setup** – provide clear documentation for installing Ollama and pulling models.
