# AIW Agent Iterative Loop (Loop Iterativo do Agente)

**Nota de estado (2026-07):** O **Loop Iterativo do Agente** é o runtime principal em `aiw/agent/iterative_loop.py`. Suporta planejamento LLM (OpenRouter quando permitido pelo perfil), re-planejamento com feedback de resultados anteriores, despacho real a Provedores de Execução (CodeAct), execução com side-effects controlados (file_write + project_patch_preview/apply via aiw_runtime/tools), execution_trace estruturado e integração profunda com Cockpit.

Recursos recentes:
- Refatorações **precisas**: prompt instrui LLM a fazer `file_read` primeiro, depois emitir `old_text`/`new_text` exatos (do conteúdo lido) para `project_patch_preview` em fontes reais.
- Cockpit: após "Aplicar patch seguro", resultado (status + backup) é mostrado inline com trace atualizado (sem reload completo para runs do agent).
- Teste completo de fluxo: `_test_full_edit_preview_apply_validate_flow` + integrado no regression smoke.
- Preferências aiw/ cirúrgicas em policy (capabilities/registry).

Mantenha dry-run por padrão; use `--execute --confirm-agent-loop` apenas para tarefas reais seguras.

## Objetivo (v1 conceitual)

O Agent Iterative Loop prova ciclos locais e auditáveis do AIW. Versão atual suporta modelo real + execução controlada.

Fluxo atual:
- Task via Cockpit ou CLI
- Perfil de Agente + Roteador de Modelo (AUTO / OpenRouter)
- Planejador LLM (ou mock)
- Despacho a Provedor de Execução + tools
- Acumulação de contexto + memória
- execution_trace para visibilidade
- Múltiplas iterações com resultados anteriores

Fluxo:

```text
task manual
-> mock planner deterministico
-> Capability Registry
-> Capability Policy v1
-> Isolation Boundary v1
-> Runtime Gate v1
-> Execution Provider v1
-> contexto local existente ou contexto minimo
-> CodeAct Sandbox com acao fixa e segura
-> artifacts locais
-> status rastreavel
```

Esta versao nao e um agente autonomo completo. Ela nao planeja com LLM, nao aplica patch, nao roda daemon e nao escreve em GitHub/Jira.

## Planejador (LLM + Mock)

- Quando `llm_planning_allowed=true` no perfil e chave OpenRouter disponível: usa `LLMPlanner` (model.generate). O prompt instrui explicitamente para refatorações precisas:
  1. Passo `file_read` com `target_file`.
  2. Passo seguinte com `kind: patch` + `old_text` + `new_text` **exatos** (copiados do conteúdo do read anterior).
- Fallback: `_mock_plan` (determinístico, com hints de "editar" e suporte a target/old/new).

Exemplo de passo gerado para edição precisa:
```json
{"step":2, "kind":"codeact_python_eval", "action_hint":"editar com old/new exatos do read anterior",
 "target_file":"aiw/agent/iterative_loop.py", "old_text":"def _now_iso(): ...", "new_text":"def _now_iso(): ... # refatorado"}
```

_build_rich_action converte isso em wrapper que chama `project_patch_preview` (ou `file_write` para .aiw/generated).

## CLI (atual - usa Loop em aiw/)

```bash
./scripts/aiw-agent-loop --help
```

Dry-run (recomendado para explorar):

```bash
./scripts/aiw-agent-loop \
  --workspace aiw \
  --task "Liste arquivos e identifique o propósito do projeto" \
  --once \
  --dry-run \
  --profile software-engineer \
  --max-iterations 3
```

Execução real (requer OPENROUTER_API_KEY com saldo/recarga quando aplicável + confirmação):

```bash
./scripts/aiw-agent-loop \
  --workspace aiw \
  --task "Analise X e sugira refatoração segura" \
  --once \
  --execute \
  --confirm-agent-loop \
  --profile software-engineer \
  --max-iterations 4
```

Listar/ler runs do Loop Iterativo do Agente (agora implementado em aiw/agent/):

```bash
./scripts/aiw-agent-loop --workspace aiw --list
./scripts/aiw-agent-loop --workspace aiw --read-run ail-xxxx
```

**Fluxo preferencial:** use o **Cockpit** (`./scripts/aiw-cockpit`) para submeter tarefas reais com **Perfil de Agente** + modelo OpenRouter e ver `execution_trace` renderizado imediatamente. O Cockpit é a interface principal para desenvolvimento real.

### Exemplo simples de uso real (hoje)

```bash
# 1. Inicie o Cockpit
./scripts/aiw-cockpit

# 2. No formulário:
#    - Perfil: software-engineer
#    - Modelo: openai/gpt-oss-120b:free (ou outro)
#    - Tarefa: "Analise aiw/agent/iterative_loop.py e liste 2 pontos de melhoria (sem editar)"
#    - Clique "Executar Loop Iterativo do Agente (execute=True)" (ou offline)

# 3. Veja na resposta:
#    - router_decision (openrouter + modelo do perfil)
#    - execution_trace com passos (inspect, codeact etc), status, resultados
#    - Re-execute para iterar
```

Com `OPENROUTER_API_KEY` válido: planner="llm", planos adaptados à tarefa. Execução Real usa o **Provedor de Execução** (codeact) do perfil.

## Regression Smoke

Rode antes de mudanças maiores:

```bash
./scripts/aiw-agent-loop-regression-smoke --workspace aiw
```

O smoke agora inclui o check completo **full_edit_preview_apply_validate_via_loop**:
- Loop com tarefa contendo "editar" + `execute=True` + `confirm_agent_loop=True` (mock planning, execução real via CodeAct).
- Gera `project_patch_preview` (verifica `patch_id`, `tool` e "editar" no trace).
- Executa `project_patch_apply` (só para workspace "aiw").
- Valida com `py_compile`.
- Afirmações: `has_real_execution`, `produced_preview`, `applied`, `validate_success`.

Helper direto:
```bash
python3 -c '
from aiw.agent.iterative_loop import _test_full_edit_preview_apply_validate_flow
import json
print(json.dumps(_test_full_edit_preview_apply_validate_flow(), indent=2, default=str))
'
```

Artefatos vão para `.aiw/workspaces/aiw/agent-iterative-loop/runs/...` e `.aiw/.../patches/`.

O artifact diferencia rede externa de localhost: `external_network_used=false` sempre, e `localhost_http_used=true` apenas quando `--with-cockpit` faz GETs locais em `127.0.0.1`. Ele tambem registra `unsafe_broad_search_used=false` e `validation_search_scope=explicit_paths_only` para reforcar a regra de validacao textual escopada.

O smoke tambem valida o Isolation Boundary: fixed CodeAct offline confirmado segue permitido, enquanto dynamic CodeAct, LLM planner, shell, rede externa e external write seguem bloqueados no profile `host_best_effort`.

Consulte [AIW Agent Loop Regression Smoke](AIW_AGENT_LOOP_REGRESSION_SMOKE.md) para a lista completa de checks.

## Dry-run vs Execute Offline

`--dry-run` valida argumentos, cria `plan.json`, consulta o Capability Registry, registra a decisao da Capability Policy v1 como simulacao permitida, registra o estado de contexto e cria uma iteracao simulada para cada passo do plano com status `dry_run`. Ele nao executa CodeAct.

`--execute --confirm-agent-loop` executa os passos do plano em foreground. Apenas o passo `codeact_python_eval` chama o CodeAct Sandbox com codigo fixo e inofensivo:

```python
print('AIW_AGENT_ITERATIVE_LOOP_STEP_OK')
```

A v1 limita `--max-iterations` a no maximo 3.

Opcionalmente, `--capability <name>` permite validar a policy contra outra capability registrada. O Agent Iterative Loop v1 so executa `codeact_sandbox`; outras capabilities ficam bloqueadas para execucao do loop mesmo se a policy local as reconhecer.

`--operation` existe para a policy e usa default seguro `python_eval_fixed`. Ele nao aceita codigo livre e qualquer operation desconhecida bloqueia a run.

## Artifacts

Cada run grava:

```text
.aiw/workspaces/<workspace_id>/agent-iterative-loop/runs/<run_id>/
```

Arquivos principais:

```text
run.json
plan.json
summary.md
iterations/iter-001.json
iterations/iter-002.json
iterations/iter-003.json
```

`run.json` inclui `run_id`, `workspace_id`, `mode`, `status`, `task`, `planner`, `max_iterations`, `plan_path`, `task_source`, `capabilities_checked`, `capability_decisions`, `isolation_profile`, `isolation_decision`, `isolation_decisions`, `runtime_decision`, `runtime_required`, `runtime_profile`, `runtime_allowed`, `execution_provider`, `execution_provider_version`, `execution_provider_supported`, `execution_provider_validation`, `requires_stronger_isolation_before_llm`, `context_pack_id`, `iterations` e `blocked_reason`.

Novos artifacts usam paths de display relativos ao repo, por exemplo `.aiw/workspaces/aiw/agent-iterative-loop/runs/<run_id>/run.json`, evitando expor `/home/...` na UI/API. Artifacts antigos com paths absolutos continuam legiveis e sao higienizados quando exibidos pelo Cockpit/API.

`plan.json` inclui `planner`, `task`, `max_iterations` e `steps`.

Cada iteracao registra `iteration`, `step_kind`, `step_title`, `uses_codeact`, `capability`, `context_pack_id`, `codeact_run_id`, `stdout_preview`, `stderr_preview` e `error`.

## Capability Registry

Antes de qualquer execucao, o loop consulta `codeact_sandbox` no Capability Registry e exige que a capability exista e valide pelo schema atual. Se a capability estiver ausente ou invalida, a run fica `blocked`.

## Capability Policy v1

A policy v1 e local, pequena e hardcoded em `aiw_workspace/capability_policy.py`. Ela usa `policy_profile=local_offline_v1`, nao le arquivos sensiveis e nao implementa RBAC, multiusuario ou configuracao dinamica.

Campos avaliados:

```text
workspace_id, capability_name, mode, operation, requires_confirmation,
confirmed, risk, runs_code, writes_files, external_io, blocked_by_default
```

Comportamento:

- `dry-run`: permite apenas simulacao, registra `allowed=true`, `dry_run=true`, `simulation_only=true`, `capability_not_executed=true` e nao executa a capability real.
- `offline execute`: exige capability existente e valida no Registry, bloqueia IO externo, exige confirmacao quando `requires_confirmation=true` e permite `codeact_sandbox` somente com `operation=python_eval_fixed`, codigo fixo, local e rastreado.
- Sem `--confirm-agent-loop`: bloqueia antes do CodeAct com `blocked_reason=confirmation_required`.
- Capability inexistente: bloqueia com `blocked_reason=capability_missing`.
- Modo `llm`: bloqueia com `llm_mode_blocked`.
- Operation desconhecida: bloqueia com `unknown_operation`.

A policy registra a decisao do Isolation Boundary junto da decisao de capability. Modo `llm` e operacoes dinamicas agora bloqueiam com `stronger_isolation_required`, mantendo `llm_real_allowed=false`.

Exemplo de artifact em `run.json`:

```json
{
  "capability_decisions": [
    {
      "capability": "codeact_sandbox",
      "allowed": true,
      "mode": "offline",
      "operation": "python_eval_fixed",
      "policy_profile": "local_offline_v1",
      "risk": "high",
      "requires_confirmation": true,
      "confirmed": true,
      "runs_code": true,
      "writes_files": true,
      "external_io": false,
      "blocked_by_default": true,
      "reason": "offline_confirmed_fixed_codeact_eval"
    }
  ]
}
```

## Context Pack

O loop detecta se existe indice local em:

```text
.aiw/workspaces/<workspace_id>/context/chunks.jsonl
```

Se o indice existir, `--execute` cria um context pack pequeno usando o Context Pack Builder. Se nao existir, a v1 nao indexa o repositorio automaticamente; ela registra `context_mode=minimal` no artifact e segue com contexto minimo.

O loop nao indexa `.env`, `config/litellm.yaml`, `AGENTS.md` ou `.aiw/` por conta propria.

## CodeAct

O execute offline passa pelo `CodeActExecutionProvider`, que delega ao `run_codeact_action(..., confirm=True)` com `kind=python_eval` e codigo fixo. Nao executa shell livre, comandos externos, Git, rede, Docker, gh, pip install ou npm install.

CodeAct continua sendo host-sandbox best-effort, nao isolamento forte. Nao deve rodar codigo nao confiavel e nao substitui container, VM ou devcontainer.

Antes de habilitar LLM real ou codigo dinamico, o AIW precisa trocar o perfil de isolamento para devcontainer ou VM e atualizar a policy de forma explicita.

## Cockpit Read-only

O Cockpit lista runs recentes do Agent Iterative Loop em modo read-only no overview. Nao ha botao de execucao.

O detalhe read-only mostra a ultima run com task, planner, contexto, blocked reason, decisions de capability, passos do plano, iteracoes, `codeact_run_id`, previews de stdout/stderr, erros e caminhos de artifact. O endpoint JSON de uma run tambem inclui `plan`, `iterations` e `artifacts`.

O historico mostra `run_id`, status, modo, `created_at`, task, planner, `context_mode`, max iterations, contagem de iteracoes, resumo da policy e blocked reason. Nao ha POST ou botao de execucao para o Agent Iterative Loop.

Endpoints:

```text
GET /api/workspaces/<workspace_id>/agent-iterative-loop/runs
GET /api/workspaces/<workspace_id>/agent-iterative-loop/runs/<run_id>
```

## Limites

- Manual e foreground apenas.
- Sem `--watch`.
- Sem LLM real.
- LLM planner bloqueado por `stronger_isolation_required`.
- Dynamic CodeAct bloqueado por `stronger_isolation_required`.
- Sem GitHub/Jira write.
- Sem patch apply.
- Sem commit/push automatico.
- Sem scheduler, daemon, tmux, nohup, cron ou systemd. (agora: daemon 24/7 via queue+persistent implementado abaixo)
- Regression smoke local/offline disponivel em `./scripts/aiw-agent-loop-regression-smoke --workspace aiw`.
- Policy local simples; ainda nao substitui isolamento forte nem revisao humana.

## Daemon 24/7 + Persistent Agents (Fluxo Autônomo Long-Running)

Implementado via `aiw/agent/iterative_loop.py` (start_persistent_agent_daemon + checkpoints + relaxed MAX) + `aiw/queue/worker.py` (PersistentAgentWorker) + cockpit wiring + queue disk-backed.

**Uso principal (Cockpit - recomendado):**
1. `./scripts/aiw-cockpit`
2. No form "Executar Agente Direto":
   - Marque "Start as background daemon (24/7 queue worker + multiple runs)"
   - Preencha Perfil (ex: software-engineer), modelo, tarefa longa.
   - Submit via botão "Start Daemon (bg persistent)" (ou normal + checkbox).
3. Monitor: na UI aparece "Daemons: N" + link /api/daemons ; seções de missões persistentes.
4. Resume: use run_id de checkpoint listado, ou re-submeta com resume.

**CLI equivalente:**
```bash
# Start via queue worker (bg)
python3 -c '
from aiw.queue import start_daemon_worker, list_daemon_workers
print(start_daemon_worker("aiw"))
print(list_daemon_workers("aiw"))
'

# Ou direto daemon para uma missão (usa thread bg + loop persistent)
python3 -c '
from aiw.agent.iterative_loop import start_persistent_agent_daemon, list_running_daemons
d = start_persistent_agent_daemon("aiw", "Tarefa autônoma longa 24/7: pesquisar e refatorar", profile="software-engineer", execute=True, confirm=True)
print(d)
print(list_running_daemons("aiw"))
'

# Via aiw-agent-loop (foreground mas com persistent/ckpt)
./scripts/aiw-agent-loop --workspace aiw --task "missão persistente" --persistent --profile software-engineer --execute --confirm-agent-loop --max-iterations 0

# Resume de run_id (checkpoint)
./scripts/aiw-agent-loop --workspace aiw --run-id ail-xxxx --resume --persistent ...

# Env para unlimited (prático ilimitado, quebra só em !should_continue/policy/stop)
AIW_PERSISTENT_MAX_ITERATIONS=0 ./scripts/aiw-agent-loop ...
# (ou export; default 1000, 0 -> 1M interno)
```

**./scripts/aiw-daemon (via wrapper):**
O script principal `aiw` suporta subcomando (adicione symlink `ln -s aiw aiw-daemon` ou use `aiw daemon`):
```bash
./scripts/aiw daemon aiw   # inicia worker + lista
# ou direto:
./scripts/aiw-cockpit  # prefira UI
```

**Resume / Recovery:**
- Checkpoints em: `.aiw/workspaces/<ws>/agent-iterative-loop/checkpoints/<run_id>.json`
- list_running_daemons() lista também de disco.
- resume_all_checkpoints_as_daemons() helper no queue/worker.
- Daemon threads são daemon=True (morrem com main); para true 24/7 use nohup/tmux ou cockpit http server rodando.

**Env + Config:**
- `AIW_PERSISTENT_MAX_ITERATIONS=0` : ilimitado (confie em checkpoints + planner.should_continue + policy gates).
- Persistência queue: `.aiw/workspaces/<ws>/queue/queue.json` (sobrevive restart).
- Monitor JSON: `/api/daemons` ou `/api/workspaces/aiw/daemons`

**Segurança:** Todas as gates (policy, runtime, confirm, isolation) passam para o run_agent... subjacente. Auto-PR em persistent success (se validado).

**Smoke/Verify:**
```bash
python3 -c '
from aiw.agent.iterative_loop import _test_daemon_persistent_logic
print(_test_daemon_persistent_logic())
'
./scripts/aiw-agent-loop-regression-smoke --workspace aiw  # (ou partes)
```

Ver também: aiw/queue/__init__.py , aiw/queue/worker.py , aiw/agent/iterative_loop.py (seção daemon), scripts/aiw-cockpit (start_daemon_agent_from_cockpit).

## Proximos Passos

Antes de usar LLM real, ainda falta conectar validacao de contexto, politicas por capability mais granulares, tela dedicada de detalhe e isolamento forte via devcontainer/VM.
