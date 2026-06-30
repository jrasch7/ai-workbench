# AIW Patch-Aware Test Suggestions

## Resultado

Implementado.

O AIW agora calcula sugestoes de testes para patches em preview, usando apenas comandos ja aprovados no profile do workspace.

## Como as sugestoes funcionam

O Cockpit le o patch preview em `.aiw/workspaces/<workspace_id>/patches/<patch_id>.json`, identifica `changed_files` e cruza esses arquivos com `profile.test_commands`.

As sugestoes nunca chamam LLM e nunca executam automaticamente.

Quando `profile.test_mappings` existe, ele tem prioridade sobre as heuristicas. Cada sugestao informa `source`, `mapping_name` e `matched_files`.

## Heuristicas

- Python: arquivos `.py` sugerem comandos `python3 -m py_compile` ou `python3 -m compileall` existentes no profile.
- Shell/scripts: arquivos em `scripts/` ou `.sh` sugerem comandos `bash -n` existentes no profile.
- Node/frontend: `package.json`, `src/`, `frontend/`, `.ts`, `.tsx`, `.js` e `.jsx` sugerem comandos Node/pnpm existentes no profile.
- Docs: patches somente `.md` podem retornar sem teste tecnico obrigatorio, salvo se existir comando docs no profile.

## Integracao com Profile Test Runner

Endpoints novos:

- `GET /api/workspaces/<workspace_id>/patches/<patch_id>/test-suggestions`
- `POST /api/workspaces/<workspace_id>/patches/<patch_id>/tests/preview`
- `POST /api/workspaces/<workspace_id>/patches/<patch_id>/tests/run`

Preview valida comando sugerido sem executar. Run exige `confirm: true` e grava um test-run normal com `trigger: patch_suggestion` e `patch_id`.

## Cockpit

O painel de patches mostra `Testes sugeridos`, arquivos alterados, motivo, confianca, status de allowlist e botoes de preview/run manual.

## Seguranca

- nao executa automaticamente;
- so sugere comandos do profile;
- comando precisa passar allowlist;
- sem `shell=True`;
- sem push;
- sem auto-commit;
- sem auto-apply;
- sem leitura de `.env`.

## Limitacoes

- heuristicas simples;
- sem LLM;
- sem coverage real;
- sem analise semantica profunda.

## Validacoes executadas

Ver relatorio final da rodada.

## Proximo passo recomendado

Adicionar ranking de relevancia por arquivo e grupos de validacao por tipo de tarefa.
