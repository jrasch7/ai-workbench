# AIW Test Run History

## Resultado

Implementado.

O Cockpit agora possui um dashboard visual de historico de test-runs, com filtros por workspace, status, texto do comando e limite de ultimos registros.

## Dashboard

A secao `Test Runs` lista execucoes gravadas em:

`.aiw/workspaces/<workspace_id>/test-runs/<test_run_id>/`

Cada item mostra workspace, status, comando, duracao, exit code, data/hora, detalhe tecnico e acao de rerun seguro.

## Filtros

Filtros disponiveis:

- workspace;
- status: todos, succeeded, failed, timed_out, blocked;
- texto/comando;
- ultimos 30, 50 ou 100 itens.

## Detalhe de test-run

O detalhe continua disponivel via:

`GET /api/workspaces/<workspace_id>/tests/runs/<test_run_id>`

A resposta inclui metadata, command, result, stdout/stderr resumidos, summary e paths dos artefatos.

## Safe Rerun

O endpoint:

`POST /api/workspaces/<workspace_id>/tests/runs/<test_run_id>/rerun`

exige `confirm: true`, localiza o comando original no test-run, confere se ele ainda existe no profile atual e valida a allowlist atual antes de executar. O novo run recebe `rerun_of` e `parent_test_run_id` na metadata.

## Seguranca

- sem comando arbitrario;
- rerun so usa comando original;
- comando precisa existir no profile atual;
- sem `shell=True`;
- sem push;
- sem auto-commit;
- sem auto-apply;
- sem leitura de `.env`.

## Limitacoes

- sem fila paralela;
- sem comparacao visual avancada;
- sem execucao automatica pos-agent.

## Validacoes executadas

Ver relatorio final da rodada de implementacao.

## Proximo passo recomendado

Conectar o historico de testes ao fluxo de patch preview para sugerir o comando mais relevante por workspace, ainda mantendo execucao manual e confirmada pelo humano.
