"""Planejador LLM para planejamento autônomo real.

Usa o ModelProvider para gerar planos iterativos.
Respeita llm_planning_allowed do Perfil de Agente.
Suporta decisão explícita de "continuar" ou "finalizar" no plano.
"""

from typing import Any, Dict, List, Optional
import json

class LLMPlanner:
    def __init__(self, model_provider: Any, model_name: str, max_steps: int = 3, profile: Optional[Dict] = None):
        self.model_provider = model_provider
        self.model_name = model_name
        self.max_steps = max_steps
        self.profile = profile or {}
        self.llm_allowed = self.profile.get("llm_planning_allowed", True)

    def plan(self, task: str, context: Optional[str] = None, dry: bool = True, previous_results: Optional[List[Dict]] = None) -> Dict[str, Any]:
        if not self.llm_allowed:
            return self._mock_plan(task)

        prev = ""
        if previous_results:
            prev = "\nResultados da iteração anterior:\n" + str(previous_results[-2:])

        prompt = f"""Dada a tarefa de engenharia: {task}
Contexto acumulado: {context or 'nenhum'}
{prev}
Perfil permite planejamento LLM: {self.llm_allowed}

Crie um plano JSON curto com até {self.max_steps} passos.
Tipos de passo suportados: "inspect_context", "codeact_python_eval", "git_log", "web_search", "summarize", "execute_provider".
Cada passo: {{"step": N, "kind": "...", "title": "...", "uses_codeact": bool, "execution_provider": "codeact|docker|devcontainer", "action_hint": "descrição curta do que executar"}}

No final do plano, adicione:
"should_continue": true/false   (decida se precisa de mais iterações)
"reason": "explicação curta"

Prefira passos reais quando não for dry. Saída APENAS JSON válido.
"""
        try:
            resp = self.model_provider.generate(prompt, self.model_name, temperature=self.profile.get("temperature", 0.2), max_tokens=700)
            text = resp.get("text", "").strip()
            start = text.find("{")
            end = text.rfind("}") + 1
            plan_json = json.loads(text[start:end])
            steps = plan_json.get("steps", [])[:self.max_steps]
            should_continue = plan_json.get("should_continue", len(steps) > 0)
            return {
                "planner": "llm",
                "task": task,
                "steps": steps,
                "should_continue": should_continue,
                "reason": plan_json.get("reason", ""),
                "llm_used": True,
                "dry": dry
            }
        except Exception as e:
            return self._mock_plan(task, error=str(e))

    def _mock_plan(self, task: str, error: Optional[str] = None):
        steps = [
            {"step":1,"kind":"inspect_context","title":"Inspecionar contexto","uses_codeact":False, "action_hint": "listar arquivos relevantes"},
            {"step":2,"kind":"codeact_python_eval","title":"Executar via CodeAct","uses_codeact":True, "execution_provider": self.profile.get("execution_provider", "codeact"), "action_hint": "rodar código simples para avançar a tarefa"},
            {"step":3,"kind":"summarize","title":"Resumir e evidenciar","uses_codeact":False, "action_hint": "criar resumo"}
        ][:self.max_steps]
        res = {"planner": "mock", "task": task, "steps": steps, "should_continue": False, "reason": "plano mock"}
        if error:
            res["fallback_reason"] = error
        return res
