# AIW Cockpit Tool Evidence Console

## Resultado

Implementado.

O AIW Cockpit agora mostra evidencias por chamada de ferramenta no detalhe de cada run, com cards amigaveis e resumo operacional. A mesma leitura sanitizada tambem fica disponivel em um endpoint local controlado para inspecao do run.

## UX adicionada

- Bloco `Evidencias das ferramentas` no detalhe do run.
- Resumo do run com:
  - modo online/offline/legacy;
  - total de tools;
  - sucessos;
  - falhas;
  - patches propostos;
  - patches aplicados.
- Cards por tool com:
  - nome da ferramenta;
  - status humano: sucesso/erro;
  - entrada resumida;
  - resultado resumido;
  - erro, quando existir;
  - dados tecnicos apenas em `<details>Avancado</details>`.
- Para `shell_exec`, o card destaca comando seguro, status, exit code, stdout e stderr resumidos.
- Para `project_patch_preview`, o card destaca arquivo alvo, status do patch, motivo e botoes apply/rollback quando aplicaveis.
- A Bancada de Execucao passou a usar badges derivados do parser de evidencias:
  - `Tools`;
  - `Patches`;
  - `Failed Tool`;
  - `Offline`;
  - `Applied`.

## Como os traces sao lidos

O parser le artefatos locais do run, quando existirem:

- `tool-traces.jsonl`;
- `messages.json`, para timeline do detalhe;
- `.aiw/patches/*.json`, para enriquecer status de patch;
- `status.json`, para identificar modo offline.

Regras:

- linhas invalidas em `tool-traces.jsonl` sao ignoradas;
- ausencia de traces nao quebra a pagina;
- runs offline com evento `offline_dry_run` aparecem como evidencia;
- raw tecnico fica colapsado em `<details>`;
- o endpoint `GET /api/runs/<run_id>/evidence` retorna apenas a estrutura sanitizada.

## Seguranca e masking

O Cockpit nao aceita comandos do usuario nesse fluxo e nao executa ferramentas. Ele apenas le evidencias ja gravadas em `.aiw/runs`.

O parser mascara:

- campos cujo nome contenha `key`, `token`, `secret`, `password` ou `api_key`;
- valores textuais que contenham `.env`, `LITELLM_MASTER_KEY`, `api_key`, `client_secret` ou `private_key`;
- raw JSON tecnico antes de renderizar na UI ou responder pela API.

Restricoes mantidas:

- nao le `.env`;
- nao altera `.env`;
- nao altera `config/litellm.yaml`;
- nao usa OpenHands;
- nao integra Hermes;
- nao instala dependencias novas;
- nao libera shell irrestrito.

## Validacoes executadas

```text
git status -sb
git log --oneline -8
python3 -m py_compile aiw_runtime/*.py
bash -n scripts/aiw-cockpit
bash -n scripts/aiw-runner-agent
bash -n scripts/aiw-tool-smoke
embedded Python compile
AIW_AGENT_OFFLINE=1 ./scripts/aiw-runner-agent --offline || true
./scripts/aiw-tool-smoke || true
project_patch_preview .env block
project_patch_preview ../outside.py block
shell_exec "git push" block
git diff --check
git --no-pager diff --stat
Cockpit HTTP smoke
```

## Limitacoes

- Nao e RAG real.
- Depende dos artefatos locais do run.
- Provider upstream pode falhar, mas offline mode permite smoke local.
- A associacao de patch com run depende do `patch_id` registrado no trace.

## Proximo passo recomendado

Evoluir a Bancada de Execucao para controlar o Tool Runtime minimo diretamente na UI:

1. Exibir chamadas `directory_list`, `file_read` e `shell_exec` em tempo mais proximo do real.
2. Criar filtros por tool/status.
3. Adicionar comparacao entre runs.
4. Conectar a futura camada de contexto/RAG sem misturar com runtime de execucao.
5. Criar evals locais antes de qualquer fine-tuning.
