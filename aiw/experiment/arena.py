"""Arena: head-to-head comparison for Experiment Lab.

Compares two profiles or two providers on identical tasks.
"""

from typing import Any, Dict, List, Optional
from aiw.experiment.bench import run_benchmark, BENCHMARK_TASKS

def run_arena(
    profile_a: str = "software-engineer",
    profile_b: str = "code-reviewer",
    provider: str = "openrouter",
    tasks: Optional[List[Dict]] = None,
    dry: bool = True,
) -> Dict[str, Any]:
    """Run same tasks under two profiles (or setups) and compare."""
    if tasks is None:
        tasks = BENCHMARK_TASKS[:2]  # small for speed

    res_a = run_benchmark(profile_name=profile_a, provider_names=[provider], tasks=tasks, dry=dry)
    res_b = run_benchmark(profile_name=profile_b, provider_names=[provider], tasks=tasks, dry=dry)

    comparison = []
    for i, ta in enumerate(res_a["results"]):
        tb = res_b["results"][i] if i < len(res_b["results"]) else {}
        comparison.append({
            "task_id": ta["task_id"],
            "a": {"profile": profile_a, "preview": ta.get("output_preview"), "latency": ta.get("latency_ms")},
            "b": {"profile": profile_b, "preview": tb.get("output_preview"), "latency": tb.get("latency_ms")},
        })

    return {
        "experiment": "arena",
        "profile_a": profile_a,
        "profile_b": profile_b,
        "provider": provider,
        "num_tasks": len(comparison),
        "comparison": comparison,
        "winner_hint": "profile_a" if profile_a == "software-engineer" else "compare_latency",
    }
