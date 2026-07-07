# AIW Validation Plan

## Resultado

Implementado.

O AIW agora monta um plano de validacao por patch, ranqueando comandos do profile em grupos como `syntax`, `targeted`, `smoke`, `build`, `docs` e `full`.

## validation_groups

`profile.validation_groups` e opcional. Cada grupo declara:

- `name`;
- `kind`;
- `priority`;
- `commands`.

Todo comando precisa existir em `profile.test_commands` e passar a allowlist.

## Ranking e score

O score e heuristico:

- match por `test_mapping`: peso alto;
- comando presente em `validation_group`: peso medio;
- mesmo source root: bonus;
- sintaxe para arquivo alterado: bonus;
- smoke amplo: bonus baixo.

Scores sao limitados a 100.

## Integracao com Patch-Aware Suggestions

O plano usa as sugestoes existentes como entrada. Quando um mapping bate, o comando herda `source`, `mapping_name` e `matched_files`; quando nao ha mapping, o plano usa fallback para sugestoes heuristicas.

## Cockpit

O painel de patches mostra `Plano de validação sugerido`, com grupos ordenados, score, motivo, matched files e botoes manuais de Preview/Executar.

Ao abrir o plano pelo Cockpit ou pela API, o AIW materializa um snapshot local quando ainda nao existe snapshot identico sem execucao. O snapshot fica em `.aiw/workspaces/<workspace_id>/validation-plans/<patch_id>/<snapshot_id>/`.

Execucoes confirmadas do plano criam um novo snapshot, gravam `validation_snapshot_id` no test-run e atualizam `executions.json` e `comparison.json`.

Endpoints relacionados:

- `GET /api/workspaces/<workspace_id>/patches/<patch_id>/validation-plan/snapshots`;
- `GET /api/workspaces/<workspace_id>/patches/<patch_id>/validation-plan/snapshots/<snapshot_id>`;
- `GET /api/workspaces/<workspace_id>/patches/<patch_id>/validation-plan/compare`.

## Seguranca

- nao executa automaticamente;
- so usa comandos do profile;
- comandos passam allowlist;
- sem `shell=True`;
- sem push;
- sem auto-commit;
- sem auto-apply;
- sem leitura de `.env`.

## Limitacoes

- score heuristico;
- sem coverage real;
- sem analise semantica profunda;
- execucao em lote limitada/confirmada.

## Validacoes executadas

Ver relatorio final da rodada.

## Proximo passo recomendado

Usar os snapshots para guiar a selecao de validacoes por area e evoluir o cockpit para uma visao operacional de qualidade por patch.

## Patch Review Gate

O resultado final do plano de validação alimenta o [Patch Review Gate](AIW_PATCH_REVIEW_GATE.md) para aprovação de commits/apply.

## Test Coverage Intent

Veja também o [Patch Test Coverage Intent](AIW_PATCH_TEST_COVERAGE_INTENT.md).
