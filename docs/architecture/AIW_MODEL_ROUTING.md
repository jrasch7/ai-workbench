# AIW Model Routing Architecture

> **Historical**
> Early free-tier routing ideas. 
> Replaced by the Model Router concept in [../ARCHITECTURE.md](../ARCHITECTURE.md) (dynamic selection + AUTO mode across all providers).
>
> See the current design for Model Router behavior.

## Goal
Provide a lightweight, low‑risk routing layer that directs AIW tasks to **free or free‑tier** model providers.

## Components
| Component | Responsibility |
|-----------|----------------|
| **Planner** | Chooses a model based on cost‑free criteria (free‑tier, open‑source) and task type. |
| **Coder / Executor** | Sends the prompt to the selected model and returns raw output. |
| **Reviewer** | Performs a quick sanity check (e.g., safety, hallucination) using a deterministic rule‑set. |
| **Validator** | Runs automated unit‑style tests on the output (JSON schema, syntax, length). |
| **Summarizer / Context Builder** | Enriches the result with relevant repository context for downstream steps. |
| **Fallback (Local)** | If all free providers fail, fall back to a local Ollama model. |

## Data Flow
1. **Input** – a task description (e.g., bug‑fix, diff review).  
2. **Planner** selects a provider from the **Free Model Matrix** (see PRD).  
3. **Executor** calls the provider via the existing `model‑ask` CLI wrapper.  
4. **Reviewer** applies safety rules (no secrets, no destructive commands).  
5. **Validator** runs the LangGraph smoke suite on the response to ensure no crashes.  
6. **Summarizer** stores the final structured result in `docs/decisions/` for audit.

## Non‑Goals
* No paid‑tier APIs (Fugu, OpenAI paid).  
* No automatic merges – all decisions remain docs‑only.
