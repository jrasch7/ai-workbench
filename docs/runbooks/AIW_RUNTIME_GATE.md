# AIW Runtime Gate v1

## Objetivo

O Runtime Gate decide qual runtime seria necessario para executar uma operacao do AIW.

Ele nao executa codigo, nao chama LLM, nao cria container, nao inicia Docker, nao abre Devcontainer e nao usa VM. Nesta sprint ele produz apenas metadata serializavel.

## Runtime Gate vs Isolation Boundary

Runtime Gate responde:

```text
onde esta operacao poderia executar?
```

Isolation Boundary responde:

```text
esta operacao pode continuar agora?
```

Na v1, o unico runtime permitido e `host_best_effort`. Os demais perfis existem apenas como destinos possiveis para decisoes futuras.

## Perfis

Perfis declarados:

```text
host_best_effort
devcontainer
docker
vm
```

`host_best_effort` e permitido somente para CodeAct fixo. Ele nao e isolamento forte.

`devcontainer`, `docker` e `vm` sao metadata nesta sprint:

- Docker nao e usado.
- Devcontainer nao e usado.
- VM nao e usada.
- Nenhum daemon ou runtime persistente e iniciado.

## API

`aiw_workspace/runtime_gate.py` expoe `evaluate_runtime_gate(...)`.

Entradas principais:

```text
capability
operation
mode
requires_confirmation
writes_files
runs_code
external_io
dynamic_code
llm
shell
```

Saida principal:

```text
allowed
runtime_required
runtime_profile
blocked_reason
requires_stronger_runtime
runtime_allowed
```

## Regras v1

Permitido:

```text
fixed_codeact_python_eval -> runtime_required=host_best_effort
python_eval_fixed        -> runtime_required=host_best_effort
```

Bloqueado com `runtime_required=devcontainer`:

```text
dynamic_codeact_python_eval
llm_planner
shell_command
network_access
external_write
```

`devcontainer` e apenas requerido como metadata. Ele nao e iniciado.

## CLI

O CLI e somente leitura:

```bash
./scripts/aiw-runtime-gate --capability codeact_sandbox --operation python_eval_fixed
./scripts/aiw-runtime-gate --operation dynamic_codeact_python_eval
./scripts/aiw-runtime-gate --operation llm_planner --mode llm
./scripts/aiw-runtime-gate --operation shell_command
./scripts/aiw-runtime-gate --operation network_access
./scripts/aiw-runtime-gate --operation external_write
```

Ele imprime JSON e retorna codigo `0` apenas quando `allowed=true`.

## Integracoes

`aiw_workspace/isolation_boundary.py` usa o Runtime Gate para enriquecer a decisao com:

```text
runtime_decision
runtime_required
runtime_profile
runtime_allowed
requires_stronger_runtime
```

`aiw_workspace/capability_policy.py` propaga esses campos para artifacts de capability. O Agent Iterative Loop tambem registra os campos no `run.json`.

O Execution Provider consome `runtime_required` apenas para informar se um provider suporta aquele runtime. Ele nao decide qual runtime e necessario.

## Limites

- Sem LLM real.
- Sem Docker.
- Sem Devcontainer.
- Sem VM.
- Sem shell livre.
- Sem rede externa.
- Sem external write.
- Sem codigo dinamico.

Antes de liberar `devcontainer`, `docker` ou `vm`, uma sprint futura precisa implementar o runtime real e mudar a policy explicitamente.
