# AIW Workspace Onboarding

## Resultado

Implementado.

O Cockpit agora possui onboarding controlado para workspaces externos e validacao de profile sem executar comandos de teste.

## Onboarding UI

A secao Workspaces inclui o painel `Adicionar workspace` com:

- nome;
- ID seguro;
- path local absoluto;
- tipo opcional: `python`, `node`, `mixed`, `docs`, `unknown`.

O backend revalida tudo antes de salvar.

## Workspace config local

Workspaces externos sao salvos em `.aiw/workspaces.json`, que permanece ignorado pelo Git. O workspace `aiw` continua existindo como default mesmo sem config local.

Remover um workspace remove apenas a entrada da config local. O projeto alvo e os artifacts scoped nao sao apagados.

## Stack detection

A deteccao e read-only e nao chama comandos externos. Ela verifica arquivos publicos como:

- `package.json`, locks Node;
- `pyproject.toml`, `requirements.txt`, `setup.py`;
- `Dockerfile`, `docker-compose.yml`;
- arquivos Markdown.

`.env` nunca e lido. A validacao informa apenas se `.env` existe.

## Profile validation

O endpoint `GET /api/workspaces/<workspace_id>/profile/validate` retorna:

- status do profile;
- `safe_roots`;
- `source_roots`;
- `blocked_paths`;
- `test_commands`;
- existencia dos source roots;
- validacao dos comandos de teste contra allowlist;
- warnings.

Test commands sao apenas validados nesta fase. Nenhum teste e executado.

Execucao assistida dos comandos validados foi adicionada em `docs/runbooks/AIW_PROFILE_TEST_RUNNER.md`.

## Seguranca

- nao le `.env`;
- nao executa comandos arbitrarios;
- nao apaga projetos;
- nao faz push;
- nao faz auto-commit;
- nao faz auto-apply;
- bloqueia paths amplos demais como `/`, `/home`, `/home/joao`, `/tmp` e `/mnt`;
- bloqueia path dentro de `.git`.

## Limitacoes

- test commands sao apenas validados;
- execucao real de testes fica para proxima milestone;
- workspaces externos ainda exigem acao humana;
- validacao de duplicidade de path bloqueia por seguranca.

## Validacoes executadas

Ver relatorio final da fase para saidas consolidadas.

## Proximo passo recomendado

Implementar execucao assistida de test commands com preview, allowlist por profile, logs por workspace e aprovacao humana antes de qualquer acao mutavel.
