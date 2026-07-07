"""Benchmark runner for Experiment Lab.

Runs standardized tasks across registered model providers + profiles.
Results can be used to improve AUTO router decisions.

Current: lightweight, uses existing router + model_prov.generate.
"""

from typing import Any, Dict, List, Optional
import time

from aiw.router.router import get_model_router
from aiw.profiles.loader import load_profile, list_profiles
from aiw.providers.model.registry import get_model_provider_registry

BENCHMARK_TASKS = [
    {"id": "refactor_small", "task": "Refactor a small function for clarity and add type hints.", "category": "refactor"},
    {"id": "test_gen", "task": "Generate unit tests for a simple parser.", "category": "test"},
    {"id": "security_review", "task": "Review code for common vulnerabilities (SQLi, XSS).", "category": "security"},
    {"id": "summarize", "task": "Summarize a long technical document concisely.", "category": "docs"},
]

def run_benchmark(
    profile_name: str = "software-engineer",
    provider_names: Optional[List[str]] = None,
    tasks: Optional[List[Dict]] = None,
    max_tokens: int = 300,
    dry: bool = True,
) -> Dict[str, Any]:
    """Run a set of benchmark tasks for a profile across providers."""
    profile = load_profile(profile_name)
    router = get_model_router()
    model_reg = get_model_provider_registry()

    if provider_names is None:
        provider_names = ["litellm", "openrouter"]  # known

    if tasks is None:
        tasks = BENCHMARK_TASKS

    results = []
    start = time.time()

    for t in tasks:
        task = t["task"]
        rd = router.route(task, profile=profile, mode="auto")
        chosen_provider = rd.get("provider", "litellm")
        model = rd.get("model", profile.get("default_model", "dev-coder"))

        if chosen_provider not in provider_names:
            chosen_provider = provider_names[0] if provider_names else "litellm"

        prov = model_reg.get(chosen_provider)
        output = {"text": "", "error": None, "latency_ms": None}

        if prov and not dry:
            t0 = time.time()
            try:
                gen = prov.generate(task, model, max_tokens=max_tokens, temperature=profile.get("temperature", 0.2))
                output["text"] = gen.get("text", "")[:500]
                output["latency_ms"] = int((time.time() - t0) * 1000)
            except Exception as e:
                output["error"] = str(e)[:200]
                output["latency_ms"] = int((time.time() - t0) * 1000)
        else:
            # dry or no key: simulate
            output["text"] = f"[dry] plan for {t['id']} using {chosen_provider}/{model}"
            output["latency_ms"] = 120

        results.append({
            "task_id": t["id"],
            "category": t["category"],
            "provider": chosen_provider,
            "model": model,
            "profile": profile_name,
            "output_preview": output["text"][:200],
            "latency_ms": output["latency_ms"],
            "error": output["error"],
            "router_rationale": rd.get("rationale"),
        })

    duration = int((time.time() - start) * 1000)

    return {
        "experiment": "bench",
        "profile": profile_name,
        "providers_tested": provider_names,
        "num_tasks": len(results),
        "duration_ms": duration,
        "results": results,
        "summary": {
            "success_rate": sum(1 for r in results if not r["error"]) / max(1, len(results)),
            "avg_latency": sum(r["latency_ms"] or 0 for r in results) / max(1, len(results)),
        },
    }
