# AIW Workspace-Scoped Artifacts

## Resultado

Implementado.

O AIW agora prefere artifacts por workspace para runs, patches e caches de contexto. O workspace padrao e `aiw`, definido por `AIW_WORKSPACE_ID` quando presente.

## Layout

Artifacts novos:

- `.aiw/workspaces/<workspace_id>/runs/`
- `.aiw/workspaces/<workspace_id>/patches/`
- `.aiw/workspaces/<workspace_id>/context/`

Artifacts legados continuam em leitura:

- `.aiw/runs/`
- `.aiw/patches/`
- `.aiw/context/`

Para o workspace `aiw`, o Cockpit e o indexer leem scoped primeiro e fazem fallback para legacy. Novas execucoes do runner agent gravam em scoped.

## Runner

`scripts/aiw-runner-agent` usa `AIW_WORKSPACE_ID`, com fallback para `aiw`, e registra em `status.json`:

- `workspace_id`
- `artifact_scope`

Com isso, cada run novo fica isolado em `.aiw/workspaces/<workspace_id>/runs/`.

## Context Pack e Search

`aiw_context.indexer` aceita `workspace_id` nos helpers principais:

- `rebuild_indexes(root, workspace_id)`
- `get_search_index(root, workspace_id)`
- `get_context_pack(root, workspace_id)`
- `build_agent_context(root, workspace_id)`

O cache scoped e escrito em `.aiw/workspaces/<workspace_id>/context/`. Para `aiw`, a leitura ainda aceita `.aiw/context/` se o cache scoped nao existir.

## Cockpit

Endpoints com workspace:

- `GET /api/context/status?workspace=aiw`
- `POST /api/context/rebuild?workspace=aiw`
- `GET /api/context/pack?workspace=aiw`
- `GET /api/search?q=offline&workspace=aiw`

O Cockpit mostra o workspace ativo e o escopo `scoped` ou `legacy` em runs, patches e health de contexto. Patches scoped sao lidos antes dos legados; apply e rollback continuam aceitando patches antigos.

## Git Hygiene

Os artifacts locais scoped ficam ignorados:

- `.aiw/workspaces/*/runs/`
- `.aiw/workspaces/*/patches/`
- `.aiw/workspaces/*/context/`

`.aiw/workspaces.json` permanece local e ignorado.

## Restricoes Respeitadas

- Nao leu nem alterou `.env`.
- Nao mexeu em `~/.hermes/config.yaml`.
- Nao usou OpenHands.
- Nao integrou Hermes.
- Nao adicionou dependencia nova.
- Nao criou shell livre via HTTP.
- Nao adicionou push pela UI.

## Riscos Restantes

- Workspaces externos ainda nao executam agents; o Cockpit apenas enxerga health/git control por workspace conhecido.
- O isolamento de artifacts nao substitui sandbox de execucao.
- Patches legados continuam suportados para compatibilidade e devem ser migrados naturalmente conforme novos previews forem criados.

## Proximo Passo Recomendado

Retomar o Tool Runtime minimo estilo Manus/Devin/CodeAct com foco em:

1. `directory_list`
2. `file_read`
3. `shell_exec` controlado
4. logs e evidencias por workspace
5. `file_write` restrito
6. `file_patch` com diff auditavel
7. integracao progressiva com a UI do Cockpit
