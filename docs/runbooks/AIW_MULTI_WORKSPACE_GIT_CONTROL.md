# AIW Multi-Workspace and Git Control

## Resultado

Implementado.

O Cockpit agora possui uma primeira versao de Multi-Workspace local e um Git Control Panel seguro. O AI Workbench aparece como workspace padrao mesmo sem config local, e workspaces adicionais podem ser configurados em `.aiw/workspaces.json`, que fica ignorado pelo Git.

## Multi-Workspace

- Config local ignorada: `.aiw/workspaces.json`.
- Exemplo versionado: `config/aiw-workspaces.example.json`.
- Workspace padrao:
  - id: `aiw`;
  - nome: `AI Workbench`;
  - path: `/home/joao/ai-workbench`;
  - type: `aiw`.
- Endpoints:
  - `GET /api/workspaces`;
  - `GET /api/workspaces/<workspace_id>/health`;
  - `POST /api/workspaces/active`.

O health por workspace mostra nome, path, existencia, branch atual, HEAD curto, clean/dirty, quantidade de arquivos modificados, README, docs, `package.json`, `pyproject.toml` e ultimo commit.

## Git Control Panel

O painel mostra:

- branch atual;
- HEAD curto;
- clean/dirty;
- arquivos alterados com checkboxes;
- diff resumido;
- criacao de branch local;
- checkout de branch existente quando o workspace esta limpo;
- commit local com lista explicita de arquivos.

Endpoints:

- `GET /api/git/status?workspace=aiw`;
- `GET /api/git/diff?workspace=aiw`;
- `POST /api/git/branch/create`;
- `POST /api/git/branch/checkout`;
- `POST /api/git/commit`.

## Seguranca

- Sem shell livre.
- Git roda via `subprocess.run([...])`.
- Workspace e selecionado por ID conhecido, nunca por path arbitrario.
- Branch name passa por regex segura.
- Commit message nao pode ser vazia e tem limite de tamanho.
- Commit usa staging explicito e nunca usa `git add .`.
- Commit valida arquivos contra `git status --porcelain`.
- Bloqueios:
  - `.env`;
  - `.env.*`;
  - secrets/tokens/credentials;
  - `AGENTS.md`;
  - `.aiw/context/`;
  - `.aiw/runs/`;
  - `.aiw/backups/`;
  - `.aiw/generated/`;
  - `.aiw/patches/`.
- Push via UI nao existe nesta versao.

## Limitacoes

- Sem push via UI.
- Sem deploy.
- Sem execucao de agentes em workspace externo ainda.
- Workspace config local e ignorada.
- Commit usa staging explicito.
- Branch/commit usam subprocess controlado.

## Validacoes executadas

```text
git status -sb
git log --oneline -12
git branch --show-current
python3 -m py_compile aiw_runtime/*.py
python3 -m py_compile aiw_context/*.py
bash -n scripts/aiw-cockpit
bash -n scripts/aiw-runner-agent
bash -n scripts/aiw-tool-smoke
embedded Python compile
./scripts/aiw-tool-smoke || true
AIW_AGENT_OFFLINE=1 AIW_USE_CONTEXT_PACK=1 ./scripts/aiw-runner-agent --offline || true
python3 -m aiw_context.indexer || true
project_patch_preview .env block
project_patch_preview ../outside.py block
shell_exec "git push" block
git diff --check
git --no-pager diff --stat
Cockpit HTTP smoke
```

## Proximo passo recomendado

Evoluir para execucao de agentes por workspace selecionado, mas apenas depois de:

1. adicionar allowlist explicita de workspaces externos;
2. criar sandbox por workspace;
3. separar contexto, runs e patches por workspace;
4. adicionar preview de acoes antes de qualquer escrita;
5. manter push/deploy fora da UI ate haver politica de aprovacao.
