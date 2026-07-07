# AIW Free Model Bench Harness PRD

## Scope
Create a lightweight benchmark harness that runs a series of **docs‑only** tasks against free model providers. The harness does not execute any code, it only records model responses and metadata.

## Benchmark Tasks
| # | Task Type | Description |
|---|-----------|-------------|
| 1 | **Bug‑fix** | Small code snippet with a known bug; model must propose a correct fix. |
| 2 | **Diff Review** | Provide a diff and ask the model to comment on potential issues. |
| 3 | **Feature Plan** | Draft a short plan for a new feature (e.g., add a CLI flag). |
| 4 | **Log Diagnosis** | Summarise a brief error log and suggest next steps. |
| 5 | **Context Summary** | Summarise repository context for a given issue.
| 6 | **PR Validation** | Review a mock PR description and flag any missing tests.

## Success Criteria
* **Quality** – answer must be syntactically correct and logically sound (manual review). 
* **Latency** – each model call < 4 s (average). 
* **Cost** – total cost $0 (free tier only). 
* **Free‑Tier Limits** – respect per‑day token limits of each provider. 
* **Stability** – no crashes in the LangGraph smoke suite when parsing responses. 
* **Safety** – no secrets, no destructive commands, no policy violations.

## Harness Implementation (pseudo‑code)
```
for task in TASKS:
    provider = choose_free_provider(task.type)
    response = model_ask(provider, task.prompt)
    record(task.id, provider.name, response, latency, success)
```
The harness stores results in `reports/free-model-bench/` as JSON lines.

## Next Steps
1. Implement the harness script under `scripts/aiw-free-model-bench`. 
2. Run the harness locally and evaluate each provider. 
3. Summarise findings in the roadmap.
