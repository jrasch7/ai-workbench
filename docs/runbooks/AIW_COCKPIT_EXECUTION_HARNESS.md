# AIW Cockpit Execution Harness

## Resultado

Implementado.

O AIW Cockpit agora tem uma bancada visual propria para acompanhar runs online, offline e legados, com um painel agregado de patch previews e um painel inicial de saude de contexto/RAG. A mudanca mantem o Cockpit como caminho principal do projeto e nao depende de OpenHands ou Hermes.

## Escopo aplicado

- Normalizacao de artefatos locais:
  - `readme.txt:Zone.Identifier` removido do tracking.
  - `*:Zone.Identifier` adicionado ao `.gitignore`.
  - `.aiw/backups/`, `.aiw/generated/` e `.aiw/patches/` ignorados.
  - `.aiw/runs/` preservado para historico operacional local.
- Cockpit visual:
  - Nova secao `Bancada de Execucao`.
  - Trilhos lado a lado para runs online/tool runtime, agent offline e one-shot legado.
  - Badges para Tools, Patch Preview, Applied, Failed e Offline.
  - Painel agregado `Alteracoes propostas` lendo `.aiw/patches/*.json`.
  - Botoes de apply/rollback reutilizando os endpoints existentes.
  - Diff tecnico em `<details>`.
  - Empty state amigavel quando nao ha patches.
- Context/RAG Health:
  - Presenca de `README.md`.
  - Presenca de `docs/`.
  - Presenca e contagem de `docs/runbooks/`.
  - Presenca de `config/litellm.yaml`, sem ler seu conteudo.
  - Presenca de `aiw_runtime/`.
  - Contagem de patches pendentes.
  - Contagem de runs locais recentes.
  - Git HEAD curto.

## Arquivos alterados

- `.gitignore`
- `scripts/aiw-cockpit`
- `docs/runbooks/AIW_COCKPIT_EXECUTION_HARNESS.md`
- `readme.txt:Zone.Identifier` removido do tracking

## Validacoes executadas

```text
git status -sb
python3 -m py_compile aiw_runtime/*.py
bash -n scripts/aiw-runner-agent
bash -n scripts/aiw-tool-smoke
bash -n scripts/aiw-cockpit
embedded Python compile
AIW_AGENT_OFFLINE=1 ./scripts/aiw-runner-agent --offline || true
./scripts/aiw-tool-smoke || true
project_patch_preview security blocks
shell_exec git push block
AIW Cockpit startup smoke
git diff --check
git --no-pager diff --stat
```

## Evidencias

Evidencias consolidadas na rodada de commit:

```text
EMBEDDED_PYTHON_OK
```

Smoke offline:

```text
STATUS: REVIEW
MODE: offline
```

Tool smoke:

```text
ALL TESTS PASSED
```

Bloqueios explicitos:

```text
project_patch_preview .env -> Acesso a .env bloqueado.
project_patch_preview ../outside.py -> Escape de diretorio bloqueado (..).
shell_exec "git push" -> Subcomando git mutavel bloqueado: push
```

Smoke do Cockpit:

```text
AIW Local Cockpit running at http://127.0.0.1:8880
HTTP/1.0 200 OK
Bancada de Execucao
Context / RAG Health
Agent Offline
Alteracoes propostas
/runner/patch/apply
/runner/patch/rollback
```

## Restricoes respeitadas

- Nao leu `.env`.
- Nao alterou `.env`.
- Nao alterou `config/litellm.yaml`.
- Nao mexeu em `~/.hermes/config.yaml`.
- Nao integrou Hermes.
- Nao usou OpenHands.
- Nao adicionou dependencias.
- Nao usou `git add .`.
- Preservou `AGENTS.md` fora do tracking.

## Riscos restantes

- O painel Context/RAG Health e apenas uma primeira leitura estrutural; ainda nao executa indexacao, retrieval, chunking ou avaliacao de qualidade de contexto.
- O painel agregado de patches depende dos JSONs gerados pelo runtime em `.aiw/patches/`. Se o diretorio estiver vazio, a UI mostra empty state.
- A associacao patch-run e exibida somente quando o JSON do patch registrar esse vinculo.

## Proximo passo recomendado

Retomar o Tool Runtime minimo estilo Manus/Devin/CodeAct:

1. Consolidar `directory_list`, `file_read` e `shell_exec` controlado na UI.
2. Exibir logs/evidencias por chamada de ferramenta.
3. Criar validacao local por run.
4. Evoluir `file_write` restrito.
5. Evoluir `file_patch` com diff auditavel.
6. Integrar o fluxo completo na Bancada de Execucao.
7. Avaliar Hermes apenas depois, como consumidor controlado, nao como runtime central.
