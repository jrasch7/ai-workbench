#!/usr/bin/env python3
"""
Teste End-to-End do Loop Iterativo do Agente com OpenRouter real (via aiw/).

Uso:
  source .env
  python3 scripts/test-e2e-agent-loop-openrouter.py

Ou direto (o script carrega .env):
  python3 scripts/test-e2e-agent-loop-openrouter.py

Tarefas de exemplo em PT conforme pedido:
1. "refatore função Y e rode pytest" (usando py_compile como safe equivalente)
2. "adicione log em Z"

Verifica: LLM planning real (OpenRouter), execution_trace com ações de edit/validate, router, resultados.
"""

import os
import sys
import json
import time
from pathlib import Path

# Carrega .env manualmente (robusto, sem depender de dotenv ou source externo)
def load_env_key():
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        print("AVISO: .env nao encontrado, usando env atual")
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and v and k not in os.environ:  # não sobrescreve se já exportado
                os.environ[k] = v

load_env_key()

# Garante PYTHONPATH
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from aiw.profiles.loader import load_profile
from aiw.agent.iterative_loop import run_agent_iterative_loop_once, list_agent_loop_runs, read_agent_loop_run

def run_test_task(task: str, profile_name: str = "software-engineer", model: str = "openai/gpt-oss-120b:free", max_iter: int = 1, execute: bool = True):
    print("\n" + "="*80)
    print(f"TAREFA: {task}")
    print(f"PERFIL: {profile_name} | MODELO: {model} | execute={execute} | max_iterations={max_iter}")
    print("="*80)

    prof = load_profile(profile_name).copy()
    prof["default_model"] = model  # CRUCIAL para OpenRouter real (evita "dev-coder" invalido)
    # Força allowed para openrouter
    if "openrouter" not in prof.get("allowed_model_providers", []):
        prof["allowed_model_providers"] = ["openrouter", "litellm"]

    t0 = time.time()
    res = run_agent_iterative_loop_once(
        workspace_id="aiw",
        task=task,
        dry_run=not execute,
        execute=execute,
        confirm_agent_loop=execute,
        max_iterations=max_iter,
        task_source="e2e-test-openrouter",
        capability_name="codeact_sandbox",
        operation="python_eval_fixed",
        profile=prof,
    )
    dt = time.time() - t0

    print(f"\nTEMPO: {dt:.1f}s")
    print("RETORNO ok:", res.get("ok"))
    if not res.get("ok"):
        print("ERRO:", res.get("error"))
    run = res.get("run", {}) or {}

    # Verificacoes chave
    print("\n--- ROUTER / PROVIDER ---")
    print("router_decision:", json.dumps(run.get("router_decision"), indent=2, ensure_ascii=False))
    print("chosen_provider:", run.get("chosen_provider"))
    print("chosen_model:", run.get("chosen_model"))
    print("llm_planning_used:", run.get("llm_planning_used"))
    print("planner:", run.get("planner"))
    print("status:", run.get("status"))
    print("mode:", run.get("mode"))
    print("has_real_execution:", run.get("has_real_execution"))

    # Plano LLM (ou mock se falhou)
    print("\n--- PLANO (plan_iteration_1) ---")
    plan = run.get("plan_iteration_1") or {}
    print(json.dumps(plan, indent=2, ensure_ascii=False)[:2000])

    # Execution trace (o mais importante: edits, resultados reais)
    trace = run.get("execution_trace", []) or []
    print(f"\n--- EXECUTION_TRACE ({len(trace)} entries) ---")
    for i, entry in enumerate(trace[:5]):  # mostra primeiras
        print(f"  [{i}] iter={entry.get('iteration')} kind={entry.get('kind')} title={entry.get('title')}")
        print(f"      success={entry.get('success')} provider={entry.get('provider')} retries={entry.get('retries')}")
        out = entry.get("output") or {}
        if isinstance(out, dict):
            if out.get("stdout"):
                print(f"      stdout[:200]: {str(out.get('stdout'))[:200]}")
            if out.get("status"):
                print(f"      status: {out.get('status')}")
            if out.get("returncode") is not None:
                print(f"      rc: {out.get('returncode')}")
        if entry.get("error"):
            print(f"      error: {entry.get('error')}")
    if len(trace) > 5:
        print(f"  ... +{len(trace)-5} mais no trace")

    print("\n--- STEP_RESULTS RESUMO ---")
    for sr in (run.get("step_results") or [])[:3]:
        print(f"  iter={sr.get('iteration')} status={sr.get('status')} success={sr.get('success')}")

    # Salva full run para inspecao
    out_dir = root / ".aiw" / "workspaces" / "aiw" / "agent-iterative-loop" / "runs" / run.get("run_id", "unknown")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "e2e-full.json").write_text(json.dumps(res, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"\nRun salvo em: {out_dir}")

    # Lista recente via API
    try:
        listed = list_agent_loop_runs("aiw", limit=3)
        print("list_agent_loop_runs (recentes):", len(listed.get("runs", [])))
    except Exception as e:
        print("list falhou:", e)

    return res


if __name__ == "__main__":
    print("=== TESTE E2E LOOP ITERATIVO DO AGENTE + OPENROUTER REAL ===")
    print("OPENROUTER_API_KEY presente?", bool(os.environ.get("OPENROUTER_API_KEY")))
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("ERRO: sem chave. Exporte ou coloque em .env")
        sys.exit(1)

    # Tarefa 1: refatore + rode verificacao (equivalente pytest via py_compile + tools)
    task1 = "refatore funcao build_mock_plan em aiw/agent/iterative_loop.py para adicionar comentario claro e rode py_compile para validar (use pytest se possivel)"
    res1 = run_test_task(task1, model="openai/gpt-oss-120b:free", max_iter=1, execute=True)

    # Tarefa 2: adicione log
    task2 = "adicione log informativo na funcao _create_run do arquivo aiw/agent/iterative_loop.py e valide a mudanca com leitura simples"
    res2 = run_test_task(task2, model="meta-llama/llama-3.3-70b-instruct:free", max_iter=1, execute=True)

    print("\n=== FIM DOS TESTES E2E ===")
    print("Verifique os run.json e e2e-full.json nos dirs de runs para traces completos.")
    print("Use Cockpit (./scripts/aiw-cockpit apos source .env) para UI com escolha de modelo OpenRouter + perfil.")
