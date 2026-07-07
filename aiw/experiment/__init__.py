"""Experiment Lab (aiw/experiment).

First-class support for systematic testing of models, profiles, providers and strategies.
Feeds back into Model Router and profiles.

Core:
- Benchmarks: standardized tasks
- Arena: comparisons
- Results: cost/latency/quality (stub for now)
"""

from .bench import run_benchmark, BENCHMARK_TASKS
from .arena import run_arena

__all__ = [
    "run_benchmark",
    "BENCHMARK_TASKS",
    "run_arena",
    "list_experiments",
]

def list_experiments():
    return ["bench", "arena", "model_matrix_smoke"]
