# AIW Agent Iterative Loop Offline v1

## Objetivo

O Agent Iterative Loop Offline v1 prova o primeiro ciclo local e auditavel do AIW sem modelo real, sem integracao externa e sem automacao em background.

Fluxo:

```text
task manual
-> mock planner deterministico
-> Capability Registry
-> Capability Policy v1
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

`--dry-run` valida argumentos, cria `plan.json`, consulta o Capability Registry, registra a decisao da Capability Policy v1 como simulacao permitida, registra o estado de contexto e cria uma iteracao simulada para cada passo do plano com status `dry_run`. Ele nao executa CodeAct.

`--execute --confirm-agent-loop` executa os passos do plano em foreground. Apenas o passo `codeact_python_eval` chama o CodeAct Sandbox com codigo fixo e inofensivo:

```python
print('AIW_AGENT_ITERATIVE_LOOP_STEP_OK')
```

A v1 limita `--max-iterations` a no maximo 3.

Opcionalmente, `--capability <name>` permite validar a policy contra outra capability registrada. O Agent Iterative Loop v1 so executa `codeact_sandbox`; outras capabilities ficam bloqueadas para execucao do loop mesmo se a policy local as reconhecer.

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

`run.json` inclui `run_id`, `workspace_id`, `mode`, `status`, `task`, `planner`, `max_iterations`, `plan_path`, `task_source`, `capabilities_checked`, `capability_decisions`, `context_pack_id`, `iterations` e `blocked_reason`.

`plan.json` inclui `planner`, `task`, `max_iterations` e `steps`.

Cada iteracao registra `iteration`, `step_kind`, `step_title`, `uses_codeact`, `capability`, `context_pack_id`, `codeact_run_id`, `stdout_preview`, `stderr_preview` e `error`.

## Capability Registry

Antes de qualquer execucao, o loop consulta `codeact_sandbox` no Capability Registry e exige que a capability exista e valide pelo schema atual. Se a capability estiver ausente ou invalida, a run fica `blocked`.

## Capability Policy v1

A policy v1 e local, pequena e hardcoded em `aiw_workspace/capability_policy.py`. Ela nao le arquivos sensiveis e nao implementa RBAC, multiusuario ou configuracao dinamica.

Campos avaliados:

```text
workspace_id, capability_name, mode, requires_confirmation, confirmed,
risk, runs_code, writes_files, external_io, blocked_by_default
```

Comportamento:

- `dry-run`: permite apenas simulacao, registra `allowed=true`, `dry_run=true` e nao executa a capability real.
- `offline execute`: exige capability existente e valida no Registry, bloqueia IO externo, exige confirmacao quando `requires_confirmation=true` e permite `codeact_sandbox` somente com codigo fixo, local e rastreado.
- Sem `--confirm-agent-loop`: bloqueia antes do CodeAct com `blocked_reason=confirmation_required`.
- Capability inexistente: bloqueia com `blocked_reason=capability_missing`.

Exemplo de artifact em `run.json`:

```json
{
  "capability_decisions": [
    {
      "capability": "codeact_sandbox",
      "allowed": true,
      "mode": "offline",
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

O execute offline usa `run_codeact_action(..., confirm=True)` com `kind=python_eval` e codigo fixo. Nao executa shell livre, comandos externos, Git, rede, Docker, gh, pip install ou npm install.

CodeAct continua sendo host-sandbox best-effort, nao isolamento forte. Nao deve rodar codigo nao confiavel e nao substitui container, VM ou devcontainer.

## Cockpit Read-only

O Cockpit lista runs recentes do Agent Iterative Loop em modo read-only no overview. Nao ha botao de execucao.

O detalhe read-only mostra a ultima run com task, planner, contexto, blocked reason, decisions de capability, passos do plano, iteracoes, `codeact_run_id`, previews de stdout/stderr, erros e caminhos de artifact. O endpoint JSON de uma run tambem inclui `plan`, `iterations` e `artifacts`.

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
- Policy local simples; ainda nao substitui isolamento forte nem revisao humana.

## Proximos Passos

Antes de usar LLM real, ainda falta conectar validacao de contexto, politicas por capability mais granulares, tela dedicada de detalhe e isolamento forte via devcontainer/VM.
