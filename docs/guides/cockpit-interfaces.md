# How the Cockpit Should Consume Interfaces

## Rule
The Cockpit (and all UIs/CLIs) **must** consume only public interfaces. They should not import directly from internal implementation modules.

## Expected Consumption Points
- List available Model Providers → via Model Provider Registry (`aiw.providers.model.registry`)
- Trigger AUTO routing → via ModelRouter (`aiw.router.router`)
- Select **Perfil de Agente** → via Agent Profile loader (`aiw.profiles.loader` + `aiw.load_profile`)
- Execute tasks → via **Loop Iterativo do Agente** (`aiw.agent.iterative_loop.run_agent_iterative_loop_once` which uses Router + LLMPlanner + Provedor de Execução)
- View execution trace / results → via run return value (includes `execution_trace`, `router_decision`, `step_results`)
- View experiments → via Experiment Lab

## Current State (alinhado com migração)
- O Cockpit (`scripts/aiw-cockpit`) já usa preferencialmente o **Loop Iterativo do Agente** novo (aiw/) para o formulário "Executar Agente Direto (Loop Iterativo Real + OpenRouter)".
- Submissão via POST `/runner/run-agent` → executa com `execute=True`, `confirm_agent_loop=True`, perfil + modelo do form → retorna JSON com trace completo (handler especial mostra o resultado diretamente, sem depender de redirect legacy).
- Perfis selecionáveis: software-engineer (padrão para dev), security-analyst, code-reviewer.
- Modelos OpenRouter selecionáveis no form (incluindo opções :free). Override de `default_model` no profile passado ao loop.
- Roteador e Provedor de Execução (codeact primário) são acionados.
- Listagem de runs históricos do loop via `list_agent_loop_runs` / read ainda retorna vazio (em evolução; trace visível imediatamente no submit).
- Muitos outros painéis ainda usam legado (thinned delegates onde possível).

O Cockpit é o ponto de entrada recomendado para o fluxo: submeter tarefa via Cockpit → ver execution_trace e resultados → iterar (re-executar ou nova tarefa).

## Fluxo de Desenvolvimento Real via Cockpit
1. Rode `./scripts/aiw-cockpit`.
2. Preencha tarefa + escolha **Perfil de Agente** + modelo OpenRouter.
3. Submeta → observe `router_decision`, planos por iteração e `execution_trace` (detalhes de cada passo: status, policy, resultado).
4. Itere diretamente no formulário ou via links de re-execução.

Requer `OPENROUTER_API_KEY` (recarregue em openrouter.ai se usando modelos pagos).

### Exemplo completo de uso real (tarefa real com edição → trace → re-execução)

**No formulário "Executar Agente Direto - Loop Iterativo do Agente":**
- Tarefa: `Liste os principais arquivos e diretórios do projeto (top 8) e crie um arquivo de resumo em .aiw/generated/resumo-estrutura.md com a contagem e nomes, usando o Provedor de Execução.`
- Perfil de Agente: `software-engineer`
- Modelo OpenRouter: `openai/gpt-oss-120b:free`
- Clique "Executar (Execução Real)"

**O que ver na página de resultado (direto, sem redirect legado):**
- Cabeçalho/meta: Perfil de Agente, Modelo, Execução Real: ✓, iters, status.
- `execution_trace` (renderizado com `<details>` por iteração):
  - Passos com `status: "executado"` (ou "simulacao" em dry), provider `codeact`.
  - Detalhes: action com code que invoca `from aiw_runtime.tools import file_write`, stdout mostrando `'path': '.aiw/generated/...' , 'bytes_written': ...`.
  - Destaque de paths de arquivos afetados.
- Botão "Re-executar com mesma tarefa" (form hidden preserva `profile`, `model`, `agent_task`).

**Após submit (Execução Real):**
- Artefatos reais criados em `.aiw/generated/` ou previews em `.aiw/.../patches/` (controlados por policy, com backups).
- Trace completo + "Preview de Alterações Propostas".
- **Novo (após "Aplicar patch seguro")**: banner inline com `Patch aplicado: status=..., backup=...` + trace atualizado (status dos patches muda para "applied", botão vira rollback) — sem reload completo da página para runs do Loop Iterativo.
- Re-exec: submete novamente com os mesmos Perfil de Agente + modelo OpenRouter.

Refatorações precisas agora são suportadas: o plano LLM pode incluir `file_read` seguido de patch com `old_text`/`new_text` exatos do conteúdo lido.

O Cockpit consome `aiw.agent.iterative_loop.run_agent_iterative_loop_once` + helpers de profile/model/router/execution (via try aiw/ primeiro). O `render_agent_trace_html` centraliza o display do `execution_trace`.

## Recommendation
All new Cockpit features should be developed against the interfaces defined in `aiw/interfaces/` and documented in `docs/interfaces/`.

Para guias de uso real, veja o README.md (seção "Como usar o AIW para desenvolvimento real hoje") e docs/MIGRATION.md.
