# AIW External Workspace Agent Execution

## Resultado

Implementado.

O AIW Cockpit pode executar Agent Mode no workspace ativo ou em workspace registrado, mantendo artifacts no host AIW e usando paths relativos ao workspace alvo.

## Workspace Profiles

Workspaces continuam configurados localmente em `.aiw/workspaces.json`, ignorado pelo Git. O exemplo versionado fica em `config/aiw-workspaces.example.json`.

O onboarding controlado pelo Cockpit esta documentado em `docs/runbooks/AIW_WORKSPACE_ONBOARDING.md`.

Cada profile define:

- `safe_roots`
- `source_roots`
- `test_commands`
- `blocked_paths`

O workspace `aiw` existe por padrao mesmo sem config local. Workspaces externos so existem quando registrados explicitamente.

## Tool Runtime workspace-aware

As tools usam:

- `AIW_WORKSPACE_ID`
- `AIW_WORKSPACE_ROOT`
- `AIW_SOURCE_ROOTS`

O LLM continua enviando apenas paths relativos. A policy bloqueia path absoluto, `..`, `.env`, secrets, `.git`, `.venv`, `node_modules`, `vendor` e `__pycache__`.

`shell_exec` roda com `cwd=AIW_WORKSPACE_ROOT` e segue allowlist restrita.

## Runner Agent

`scripts/aiw-runner-agent` resolve o workspace registrado, exporta o root controlado para as tools e grava em `status.json`:

- `workspace_id`
- `workspace_name`
- `workspace_root`
- `artifact_scope`

Runs continuam em `.aiw/workspaces/<workspace_id>/runs/`.

## Cockpit

O Cockpit permite escolher workspace ao executar agents e adiciona botoes por workspace:

- `Executar Agent Online neste workspace`
- `Executar Agent Offline neste workspace`

O detalhe do run mostra workspace, workspace root e artifact scope.

## Endpoints

- `POST /runner/run-agent`
- `POST /runner/run-agent-offline`
- `GET /api/workspaces/<workspace_id>/execution-policy`
- `GET /api/context/status?workspace=<id>`
- `POST /api/context/rebuild?workspace=<id>`
- `GET /api/context/pack?workspace=<id>`
- `GET /api/search?q=...&workspace=<id>`

## Seguranca

- sem path arbitrario;
- sem shell livre;
- sem auto-apply;
- sem auto-commit;
- sem push;
- `.env` bloqueado.

## Limitacoes

- execucao externa ainda e leitura + shell seguro + patch preview;
- apply/commit exigem acao explicita;
- push via UI nao existe;
- workspaces precisam ser registrados.

## Validacoes executadas

Ver relatorio final do commit desta fase para as saidas completas.

## Proximo passo recomendado

Criar sandbox por workspace externo e adicionar uma fila de aprovacoes para aplicar patches externos de forma auditavel.
