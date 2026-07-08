# Adding or Customizing an Agent Profile

Perfis de Agente são a forma principal de customizar o **Loop Iterativo do Agente** (escolha de modelo/provedor, permissões de planejamento LLM, Provedor de Execução, tools).

## Location
Profiles are declarative (in code for now) + can have associated system prompts.

Recommended location: `aiw/profiles/loader.py` (BUILTIN_PROFILES) or future workspace-level overrides.

## Structure
See `docs/interfaces/agent-profile.md` for the schema. Campos chave usados hoje:
- `allowed_model_providers`: ["openrouter", "litellm"]
- `default_model`, `temperature`
- `execution_provider`: "codeact" (primário), "docker", "devcontainer"
- `llm_planning_allowed`: controla se usa Planejador LLM real (OpenRouter) ou mock
- `default_capability`, `default_operation`, `tools`, `allowed_execution_providers`

## How to add a new one
1. Adicione em `aiw/profiles/loader.py` BUILTIN_PROFILES.
2. Defina allowed_model_providers, execution_provider + allowed_..., llm_planning_allowed, tools.
3. (Opcional) associe prompt de sistema.
4. Ele aparece automaticamente no Cockpit (select de perfil) e CLI (`--profile`).
5. Teste:
   - Via Cockpit: formulário de Agente Direto.
   - Via CLI: `./scripts/aiw-agent-loop --workspace aiw --task "..." --profile SEU-PERFIL --execute --confirm-agent-loop`
   - Experiment Lab: `python -c 'from aiw import get_experiment_lab; ...'`

## Round 2 notes + uso real
- `llm_planning_allowed` controla planejamento real com OpenRouter (requer chave + saldo/recarga para não-free).
- `execution_provider` direciona o despacho no Loop Iterativo do Agente.
- Perfis agora guiam o Roteador de Modelo (AUTO) e o Provedor de Execução.
- Exemplo de perfil "code-reviewer" (llm desabilitado): útil para tarefas só de inspeção sem chamadas LLM de planejamento.

Perfis são a principal forma de customizar sem mudar código do core.

### Exemplo de uso no Loop (via Cockpit ou CLI)
Escolha `software-engineer` para tarefas de dev real (planeja com LLM + executa via codeact).
Escolha `code-reviewer` para revisão rápida (plano mock + file/git tools apenas).

Teste com tarefas reais e inspecione o `execution_trace` no resultado para validar o perfil.
