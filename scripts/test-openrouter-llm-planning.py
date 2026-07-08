#!/usr/bin/env python3
"""Teste direto do LLM Planning com OpenRouter real (usado pelo LLMPlanner no Loop)."""

import os
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

def load_env_key():
    env_path = root / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = [x.strip() for x in line.split("=", 1)]
                    if k and v and k not in os.environ:
                        os.environ[k] = v.strip('"').strip("'")

load_env_key()

from aiw.providers.model.registry import get_model_provider_registry

print("OPENROUTER_API_KEY set?", bool(os.environ.get("OPENROUTER_API_KEY")))
reg = get_model_provider_registry()
prov = reg.get("openrouter")
if not prov:
    print("No openrouter provider")
    sys.exit(1)

model = "openai/gpt-oss-120b:free"
task = "refatore funcao build_mock_plan e rode validacao com py_compile"
prompt = f"""Dada a tarefa de engenharia: {task}
Contexto acumulado: nenhum
Perfil permite planejamento LLM: True

Crie um plano JSON curto com ate 1 passo para o Loop Iterativo do Agente.
Tipos de passo: "inspect_context", "codeact_python_eval", "file_read", "file_write", "patch", "validate", "summarize".
Cada passo: {{"step": 1, "kind": "...", "title": "...", "uses_codeact": true, "action_hint": "...", "target_file": "..." }}
"should_continue": false
"reason": "..."
Saida APENAS JSON valido.
"""

print("Chamando OpenRouter generate com model:", model)
try:
    resp = prov.generate(prompt, model, temperature=0.2, max_tokens=400)
    text = resp.get("text", "")
    print("\n=== RESPOSTA LLM REAL (OpenRouter) ===\n")
    print(text)
    print("\n=== USAGE ===\n", json.dumps(resp.get("usage", {}), indent=2))
    outf = root / "reports" / "openrouter-llm-plan-sample.json"
    outf.parent.mkdir(parents=True, exist_ok=True)
    outf.write_text(json.dumps({"prompt": prompt, "response": resp}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSalvo em {outf}")
except Exception as e:
    print("ERRO no generate:", repr(str(e)[:300]))
    import traceback
    traceback.print_exc()
