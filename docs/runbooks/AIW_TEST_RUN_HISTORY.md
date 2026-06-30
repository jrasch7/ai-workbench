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
- trigger `patch_suggestion`;
- texto/comando;
- ultimos 30, 50 ou 100 itens.

## Detalhe de test-run

O detalhe continua disponivel via:

`GET /api/workspaces/<workspace_id>/tests/runs/<test_run_id>`

A resposta inclui metadata, command, result, stdout/stderr resumidos, summary e paths dos artefatos.

Quando um test-run nasce de uma sugestao de patch, a metadata inclui `trigger: patch_suggestion` e `patch_id`.

Quando nasce de um Validation Plan, a metadata inclui `trigger: validation_plan`, `patch_id`, `validation_snapshot_id`, `validation_group`, `score`, `mapping_name` e `matched_files`. O Cockpit mostra o badge `Validation plan` e linka o snapshot quando disponivel.

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

Usar o historico local para mostrar confiabilidade por area/source root e orientar quais validacoes devem ser priorizadas em cada patch.
