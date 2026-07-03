# AIW Agent Iterative Loop Offline v1

## Objetivo

O Agent Iterative Loop Offline v1 prova o primeiro ciclo local e auditavel do AIW sem modelo real, sem integracao externa e sem automacao em background.

Fluxo:

```text
task manual
-> mock planner deterministico
-> Capability Registry
-> contexto local existente ou contexto minimo
-> CodeAct Sandbox com acao fixa e segura
-> artifacts locais
-> status rastreavel
```

Esta versao nao e um agente autonomo completo. Ela nao planeja com LLM, nao aplica patch, nao roda daemon e nao escreve em GitHub/Jira.

## Mock Planner

O planner interno `build_mock_plan(task, max_iterations)` e deterministico. Ele gera de 1 a 3 passos, nunca transforma texto da task em codigo executavel e nunca chama LLM, internet ou GitHub.

Plano padrao de 3 passos:

```json
[
  {"step": 1, "kind": "inspect_context", "title": "Inspect available context", "uses_codeact": false},
  {"step": 2, "kind": "codeact_python_eval", "title": "Run safe offline CodeAct check", "uses_codeact": true},
  {"step": 3, "kind": "summarize", "title": "Summarize offline result", "uses_codeact": false}
]
```

## CLI

Ajuda:

```bash
./scripts/aiw-agent-loop --help
```

Dry-run padrao:

```bash
./scripts/aiw-agent-loop \
  --workspace aiw \
  --task "Validate mock planner loop" \
  --once \
  --dry-run \
  --max-iterations 3
```

Execucao offline explicita:

```bash
./scripts/aiw-agent-loop \
  --workspace aiw \
  --task "Validate mock planner loop" \
  --once \
  --execute \
  --confirm-agent-loop \
  --max-iterations 3
```

Listar e ler runs:

```bash
./scripts/aiw-agent-loop --workspace aiw --list
./scripts/aiw-agent-loop --workspace aiw --read-run ail-1234abcd
```

## Dry-run vs Execute Offline

`--dry-run` valida argumentos, cria `plan.json`, consulta o Capability Registry, registra o estado de contexto e cria uma iteracao simulada para cada passo do plano com status `dry_run`. Ele nao executa CodeAct.

`--execute --confirm-agent-loop` executa os passos do plano em foreground. Apenas o passo `codeact_python_eval` chama o CodeAct Sandbox com codigo fixo e inofensivo:

```python
print('AIW_AGENT_ITERATIVE_LOOP_STEP_OK')
```

A v1 limita `--max-iterations` a no maximo 3.

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

`run.json` inclui `run_id`, `workspace_id`, `mode`, `status`, `task`, `planner`, `max_iterations`, `plan_path`, `task_source`, `capabilities_checked`, `context_pack_id`, `iterations` e `blocked_reason`.

`plan.json` inclui `planner`, `task`, `max_iterations` e `steps`.

Cada iteracao registra `iteration`, `step_kind`, `step_title`, `uses_codeact`, `capability`, `context_pack_id`, `codeact_run_id`, `stdout_preview`, `stderr_preview` e `error`.

## Capability Registry

Antes de qualquer execucao, o loop consulta `codeact_sandbox` no Capability Registry e exige que a capability exista e valide pelo schema atual. Se a capability estiver ausente ou invalida, a run fica `blocked`.

## Context Pack

O loop detecta se existe indice local em:

```text
.aiw/workspaces/<workspace_id>/context/chunks.jsonl
```

Se o indice existir, `--execute` cria um context pack pequeno usando o Context Pack Builder. Se nao existir, a v1 nao indexa o repositorio automaticamente; ela registra `context_mode=minimal` no artifact e segue com contexto minimo.

O loop nao indexa `.env`, `config/litellm.yaml`, `AGENTS.md` ou `.aiw/` por conta propria.

## CodeAct

O execute offline usa `run_codeact_action(..., confirm=True)` com `kind=python_eval` e codigo fixo. Nao executa shell livre, comandos externos, Git, rede, Docker, gh, pip install ou npm install.

CodeAct continua sendo host-sandbox best-effort, nao isolamento forte. Nao deve rodar codigo nao confiavel e nao substitui container, VM ou devcontainer.

## Cockpit Read-only

O Cockpit lista runs recentes do Agent Iterative Loop em modo read-only no overview. Nao ha botao de execucao.

Endpoints:

```text
GET /api/workspaces/<workspace_id>/agent-iterative-loop/runs
GET /api/workspaces/<workspace_id>/agent-iterative-loop/runs/<run_id>
```

## Limites

- Manual e foreground apenas.
- Sem `--watch`.
- Sem LLM real.
- Sem GitHub/Jira write.
- Sem patch apply.
- Sem commit/push automatico.
- Sem scheduler, daemon, tmux, nohup, cron ou systemd.

## Proximos Passos

Antes de usar LLM real, ainda falta conectar politicas por capability, validacao de contexto, UI de detalhe dedicada e isolamento forte via devcontainer/VM.
