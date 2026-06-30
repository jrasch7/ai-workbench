# AIW Profile Test Runner

## Resultado

Implementado.

O AIW agora executa, sob confirmacao humana, comandos de teste ja declarados e validados no profile do workspace.

## Test Commands

Os comandos aceitos precisam existir em `profile.test_commands`. A UI e a API nao aceitam comando arbitrario digitado como execucao livre.

## Preview

`POST /api/workspaces/<workspace_id>/tests/preview` recebe `command_index` ou um comando exato existente no profile. O preview retorna:

- comando;
- `argv` preparado;
- workspace;
- `cwd`;
- timeout;
- motivo de bloqueio quando houver.

Preview nao executa nada.

## Execucao assistida

`POST /api/workspaces/<workspace_id>/tests/run` exige `confirm: true`. A execucao usa `subprocess.run([...], shell=False)` com ambiente minimo e cwd no root registrado do workspace.

## Logs por workspace

Cada execucao grava em:

`.aiw/workspaces/<workspace_id>/test-runs/<test_run_id>/`

Arquivos:

- `metadata.json`
- `command.json`
- `stdout.log`
- `stderr.log`
- `result.json`
- `summary.md`

## Historico visual

O Cockpit exibe o historico em `Test Runs`, com filtros por workspace, status, comando e limite de ultimos registros. O endpoint global e:

`GET /api/tests/runs`

Detalhes e rerun seguro permanecem escopados ao workspace.

## Patch-aware suggestions

Patches em preview podem sugerir testes usando apenas comandos ja presentes no profile. Runs disparados por sugestao registram `trigger: patch_suggestion` e `patch_id`.

## Seguranca

- sem comando arbitrario;
- sem `shell=True`;
- sem push;
- sem auto-commit;
- sem auto-apply;
- sem leitura de `.env`;
- sem carregar `.env`;
- env minimo e sanitizado;
- globs expandidos em Python com validacao de path;
- stdout/stderr passam por masking e truncamento.

## Limitacoes

- nao roda automaticamente apos agent run;
- comandos precisam existir no profile;
- timeout simples;
- sem fila paralela.

## Validacoes executadas

Ver relatorio final da fase.

## Proximo passo recomendado

Adicionar ranking de relevancia dos testes sugeridos por source root.
