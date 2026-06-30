# AIW Source Root Test Mapping

## Resultado

Implementado.

Profiles de workspace agora podem declarar `test_mappings`, ligando arquivos/source roots a comandos de teste ja aprovados em `profile.test_commands`.

## test_mappings

Cada mapping possui:

- `name`: nome humano da area;
- `patterns`: globs relativos ao workspace;
- `commands`: comandos ja existentes em `test_commands`.

Mappings com `commands: []` sao permitidos para areas sem teste tecnico obrigatorio, como documentacao.

## Compatibilidade com profiles antigos

`test_mappings` e opcional. Profiles antigos continuam validos e o Patch-Aware Test Suggestions cai nas heuristicas anteriores quando nenhum mapping bate.

## Patch-Aware Suggestions

A ordem de decisao e:

1. usar `profile.test_mappings`;
2. se nenhum mapping bater, usar heuristicas simples;
3. sugerir apenas comandos existentes no profile;
4. validar allowlist antes de preview/run.

Sugestoes por mapping incluem `source`, `mapping_name` e `matched_files`.

## Cockpit

O Cockpit mostra `Source Root Test Mapping` no card do workspace e detalha source/mapping/matched files em `Testes sugeridos` no painel de patches.

## Seguranca

- mappings sao relativos;
- comandos precisam existir em `test_commands`;
- comandos passam allowlist;
- sem execucao automatica;
- sem `shell=True`;
- sem leitura de `.env`.

## Limitacoes

- patterns simples;
- sem coverage real;
- sem analise semantica profunda.

## Validacoes executadas

Ver relatorio final da rodada.

## Proximo passo recomendado

Adicionar score de relevancia por mapping e permitir que profiles externos declarem grupos de validacao por tipo de tarefa.
