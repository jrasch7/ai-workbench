# Experiment Lab Guide

## Purpose
The Experiment Lab is a first-class module for continuous model and strategy evaluation. It is one of AIW's main differentiators. (Round 2 foundation complete)

## Core Capabilities
- **Benchmarks**: Run standardized tasks across multiple providers/models (aiw/experiment/bench.py)
- **Arena**: Head-to-head comparison of two setups/profiles on the same task (aiw/experiment/arena.py)
- **A/B Testing**: Prompt variations, temperature, profiles
- **Cost / Latency / Quality Analysis** (basic latency + success in v1)
- **Regression Harness**: Ensure new providers don't break existing behavior

## Usage (code)
```python
from aiw.experiment import run_benchmark, run_arena
print(run_benchmark(profile_name="software-engineer", dry=True))
print(run_arena(profile_a="software-engineer", profile_b="code-reviewer", dry=True))
```

## How to Add a New Model to Experiments
1. Implement the ModelProvider interface.
2. Register it (providers/model/registry).
3. Add to BENCHMARK_TASKS or pass custom tasks.
4. Run via `aiw.experiment` or future CLI.

## Integration Points
- Feeds data back to the Model Router for better AUTO decisions.
- Uses profiles + router + model providers.
- Future: persist results, Cockpit UI, cost tracking.

## Current (Round 2)
Populated with bench + arena. Runnable in dry mode (real LLM when key + not dry).
Update docs/guides as expanded.
- Visible in Cockpit for users to compare options.
- Used during onboarding of new providers.
