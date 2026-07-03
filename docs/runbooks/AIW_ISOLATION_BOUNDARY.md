# AIW Isolation Boundary + Devcontainer Gate v1

## Objetivo

O Isolation Boundary e um gate conservador para responder se uma operacao pode continuar no estado atual do AIW.

Ele nao executa codigo, nao chama LLM, nao cria devcontainer e nao roda Docker. Ele apenas retorna uma decisao JSON auditavel.

## Perfil Atual

O unico perfil operacional real hoje e:

```text
host_best_effort
```

Perfis conhecidos pelo gate:

```text
host_best_effort
devcontainer_required
vm_required
```

`host_best_effort` significa que a execucao acontece no host local com guardrails de processo, confirmacao, timeout e artifacts. Isso nao e sandbox forte.

## Operacoes

O gate conhece estas operacoes:

```text
fixed_codeact_python_eval
python_eval_fixed
dynamic_codeact_python_eval
llm_planner
shell_command
network_access
external_write
```

`python_eval_fixed` e alias historico de `fixed_codeact_python_eval`.

## Decisoes

Permitido hoje:

```text
fixed_codeact_python_eval
```

Somente quando:

- modo `offline`;
- confirmado pelo usuario;
- codigo fixo;
- execucao local;
- artifact rastreado;
- sem rede externa.

Bloqueado hoje:

- `dynamic_codeact_python_eval`: `stronger_isolation_required`.
- `llm_planner`: `stronger_isolation_required`.
- `shell_command`: `shell_blocked_by_isolation_boundary`.
- `network_access`: `external_network_blocked`.
- `external_write`: `external_write_blocked`.

`localhost_http_allowed=true` indica apenas que GET local para `127.0.0.1` pode ser usado pelo smoke/Cockpit read-only. Isso nao libera rede externa.

## Exemplo Permitido

```bash
./scripts/aiw-isolation-gate \
  --workspace aiw \
  --operation fixed_codeact_python_eval \
  --mode offline \
  --confirmed
```

Retorno esperado:

```json
{
  "isolation_profile": "host_best_effort",
  "operation": "fixed_codeact_python_eval",
  "allowed": true,
  "reason": "host_best_effort_fixed_code_confirmed",
  "requires_devcontainer": false,
  "requires_vm": false,
  "llm_real_allowed": false,
  "dynamic_code_allowed": false,
  "shell_allowed": false,
  "network_allowed": false,
  "external_write_allowed": false,
  "localhost_http_allowed": true
}
```

## Exemplos Bloqueados

```bash
./scripts/aiw-isolation-gate \
  --workspace aiw \
  --operation llm_planner \
  --mode llm
```

```bash
./scripts/aiw-isolation-gate \
  --workspace aiw \
  --operation dynamic_codeact_python_eval \
  --mode offline \
  --confirmed \
  --dynamic-code
```

Ambos bloqueiam antes de execucao com `stronger_isolation_required` e `requires_devcontainer=true`.

## Integração com Capability Policy

`aiw_workspace/capability_policy.py` chama o Isolation Boundary antes de permitir execucao offline.

Artifacts da policy incluem:

```text
isolation_profile
isolation_allowed
isolation_reason
isolation_decision
requires_devcontainer
requires_vm
requires_stronger_isolation_before_llm
llm_real_allowed
dynamic_code_allowed
shell_allowed
network_allowed
external_write_allowed
localhost_http_allowed
```

Modo `llm` permanece bloqueado por `stronger_isolation_required`.

## Integração com Agent Loop

O Agent Iterative Loop continua aceitando:

- dry-run;
- execute offline confirmado com `operation=python_eval_fixed`;
- mock planner deterministico;
- CodeAct com acao fixa.

Cada run nova registra `isolation_profile`, `isolation_decision`, `isolation_decisions` e `requires_stronger_isolation_before_llm`.

## Limites

- Sem LLM real.
- Sem Docker.
- Sem devcontainer funcional.
- Sem VM.
- Sem shell livre.
- Sem rede externa.
- Sem GitHub/Jira write.
- Sem endpoint POST de execucao no Cockpit.
- Sem codigo dinamico vindo de task ou modelo.

Antes de LLM real ou codigo dinamico, o AIW precisa de devcontainer ou VM e uma nova policy liberando explicitamente esse perfil.

## Busca Segura

Para confirmar texto relacionado ao Isolation Boundary, prefira:

```bash
./scripts/aiw-safe-search "isolation_profile" --paths aiw_workspace docs/runbooks README.md
```

O safe search exige `--paths`, bloqueia `.env`, `config/litellm.yaml`, `AGENTS.md`, `.aiw/` e paths absolutos antes de leitura, e evita erros de quoting comuns em `grep -R`.
