# AIW Agent Offline Mode

## Resultado

Modo offline/dry-run adicionado ao `scripts/aiw-runner-agent`.

## Objetivo

Validar o fluxo Cockpit/Runner sem depender de LiteLLM ou provider externo.

## Como usar

Via ambiente:

```bash
AIW_AGENT_OFFLINE=1 ./scripts/aiw-runner-agent
```

Via flag:

```bash
./scripts/aiw-runner-agent --offline
```

Via Cockpit:

- abrir o AIW Cockpit;
- criar ou selecionar uma task na inbox;
- usar o botao `Executar Agent Offline`.

## Arquivos gerados

O modo offline cria uma run normal em `.aiw/runs/<run-id>/` com:

- `task.md`;
- `status.json`;
- `messages.json`;
- `commands.log`;
- `tool-traces.log`;
- `tool-traces.jsonl`;
- `summary.md`.

O status final esperado e `succeeded_offline`.

## Validacoes executadas

Validacoes esperadas para qualquer alteracao nesse modo:

```bash
python3 -m py_compile aiw_runtime/*.py
bash -n scripts/aiw-runner-agent
bash -n scripts/aiw-tool-smoke
bash -n scripts/aiw-cockpit
AIW_AGENT_OFFLINE=1 ./scripts/aiw-runner-agent
./scripts/aiw-tool-smoke
git diff --check
```

## Limitacoes

- nao substitui LLM real;
- nao executa raciocinio real;
- nao chama tools destrutivas;
- serve para smoke, QA, desenvolvimento local e validacao do pipeline.

## Proximo passo recomendado

Usar o modo offline como caminho padrao de smoke para evoluir o Cockpit, o Tool Runtime e os proximos harnesses de RAG/evals antes de depender de provider externo.
