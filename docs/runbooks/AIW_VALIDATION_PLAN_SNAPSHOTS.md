# AIW Validation Plan Snapshots

## Resultado

Implementado.

O AIW agora persiste snapshots locais do Validation Plan por patch, registra execucoes confirmadas pelo humano e compara resultados entre snapshots.

## Snapshots

Snapshots ficam em:

`.aiw/workspaces/<workspace_id>/validation-plans/<patch_id>/<snapshot_id>/`

Cada snapshot guarda `plan.json`, `executions.json`, `comparison.json` e `summary.md`.

`plan.json` preserva o plano sugerido naquele momento, incluindo changed files, grupos, comandos, score, origem, mapping e matched files.

## Executions

Quando um comando do plano e executado com `confirm: true`, o test-run recebe metadata:

- `trigger: validation_plan`;
- `patch_id`;
- `validation_snapshot_id`;
- `validation_group`;
- `score`;
- `mapping_name`;
- `matched_files`.

O snapshot tambem atualiza `executions.json` com `test_run_id`, status, exit code, duracao e timestamps.

## Comparison

`comparison.json` compara o snapshot atual com o snapshot anterior do mesmo patch.

A comparacao e heuristica e cobre:

- `improved`;
- `regressed`;
- `unchanged`;
- `new`;
- `removed`;
- `changed`.

## Reliability By Area

O endpoint de reliability calcula uma visao v1 baseada em test-runs locais com `trigger=validation_plan`.

O agrupamento prefere `mapping_name`, depois `validation_group`, depois source root derivado de `matched_files`.

## Cockpit

O Cockpit mostra:

- snapshot atual no painel `Plano de validacao sugerido`;
- `Historico do plano de validacao` abaixo do plano;
- links para snapshots, detalhes e comparacao;
- `validation_snapshot_id` no Test Run History;
- `Confiabilidade por area` no card do workspace.

## Seguranca

- snapshots sao artifacts locais ignorados;
- sem execucao automatica;
- so comandos do profile;
- sem `shell=True`;
- sem push;
- sem auto-commit;
- sem auto-apply;
- sem leitura de `.env`.

## Limitacoes

- comparacao heuristica;
- sem coverage real;
- sem analise semantica profunda;
- reliability v1 baseada em historico local;
- snapshots antigos nao sao migrados.

## Validacoes executadas

Ver relatorio final da rodada de implementacao.

## Proximo passo recomendado

Usar os snapshots para montar uma trilha visual de qualidade por patch e, depois, conectar isso ao harness de agentes estilo Manus/Devin/CodeAct com selecao assistida de planos de validacao.
