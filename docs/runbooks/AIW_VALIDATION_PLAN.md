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

Persistir snapshots de planos executados por patch e comparar resultados entre reruns.
