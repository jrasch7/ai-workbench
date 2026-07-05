# AIW Execution Provider v1

## Objetivo

O Execution Provider cria uma camada entre o Agent Iterative Loop e o mecanismo que executa uma operacao.

Nesta v1, o unico provider funcional e o `CodeActExecutionProvider`. Ele encapsula o CodeAct Sandbox existente e nao duplica nem move suas regras de seguranca.

## Runtime Gate vs Execution Provider

Runtime Gate responde:

```text
qual runtime seria necessario?
```

Execution Provider responde:

```text
quem executaria esta operacao?
```

O Runtime Gate continua registrando `runtime_required`. O Execution Provider apenas informa se suporta aquele runtime e aquela operacao. Ele nao libera runtime forte por conta propria.

## Fluxo

```text
Agent Loop
-> Capability Policy
-> Isolation Boundary
-> Runtime Gate
-> Execution Provider
-> CodeAct Sandbox
```

## API

`aiw_workspace/execution_provider.py` define uma API minima:

```text
describe()
validate()
supports_runtime()
supports_operation()
execute()
dry_run()
```

Separacao de responsabilidades:

- `describe()`: metadata serializavel do provider.
- `validate()`: valida disponibilidade/configuracao do provider sem executar a acao.
- `supports_runtime()`: informa se o provider suporta `runtime_required`.
- `supports_operation()`: informa se o provider suporta a operacao.
- `dry_run()`: descreve o que faria sem executar.
- `execute()`: delega ao mecanismo real quando a policy ja permitiu.

## CodeAct Provider

`CodeActExecutionProvider` suporta:

```text
runtime: host_best_effort
operations:
  - python_eval_fixed
  - fixed_codeact_python_eval
```

Execucao real continua indo para `run_codeact_action(...)`.

O provider nao executa codigo dinamico, nao chama LLM, nao roda shell livre, nao faz rede externa e nao altera o CodeAct Sandbox.

## CLI

O CLI e somente leitura e nunca chama `execute()`:

```bash
./scripts/aiw-execution-provider --list
./scripts/aiw-execution-provider --describe codeact
./scripts/aiw-execution-provider --validate codeact
./scripts/aiw-execution-provider --supports-runtime host_best_effort
./scripts/aiw-execution-provider --supports-operation python_eval_fixed
```

## Artifacts

O Agent Iterative Loop registra:

```text
execution_provider
execution_provider_version
execution_provider_supported
execution_provider_validation
```

Campos existentes de capability, isolation e runtime permanecem.

## Future Providers

Possiveis providers futuros, apenas como roadmap:

- Devcontainer Provider
- Docker Provider
- VM Provider
- Claude Code Provider
- OpenHands Provider
- Codex Provider
- Ollama Provider

Nenhum deles e implementado nesta sprint.

## Limites

- Sem Docker.
- Sem Devcontainer.
- Sem VM.
- Sem LLM real.
- Sem codigo dinamico.
- Sem shell livre.
- Sem daemon.
- Sem worker persistente.
