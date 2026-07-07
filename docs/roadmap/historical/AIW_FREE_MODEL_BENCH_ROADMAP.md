# AIW Free Model Bench Roadmap

## Timeline (approx.)
| Phase | Duration | Milestones |
|-------|----------|------------|
| **Setup** | 1 week | - Install Ollama, pull local model \n- Configure OpenRouter free tier token \n- Add `scripts/aiw-free-model-bench` harness skeleton |
| **Benchmark** | 1‑2 weeks | - Run all 6 tasks against each free provider \n- Collect latency, success, cost metrics \n- Store results in `reports/free-model-bench/` |
| **Analysis** | 1 week | - Summarise findings in this roadmap \n- Identify gaps (e.g., token limits, quality) |
| **Roadmap Update** | 2 days | - Prioritise providers for next AIW phase \n- Draft integration plan for paid options (future) |

## Deliverables
1. Completed benchmark JSON lines in `reports/free-model-bench/`.
2. Updated documentation (this file) with observed metrics.
3. Recommendations for next‑phase model selection.

## Risks & Mitigations
- **Token quota exhaustion** – schedule runs with back‑off, split across days.
- **Local model performance variance** – provide hardware recommendations (minimum 8 GB RAM, CPU with AVX2). 
- **Provider availability** – keep a fallback list; if a free endpoint goes down, switch to another.

## Next Steps After Bench
- Choose the top‑2 providers based on quality & latency.
- Create a lightweight wrapper (`model-free`) to abstract provider selection.
- Plan integration into the AIW planning pipeline (future PR).
