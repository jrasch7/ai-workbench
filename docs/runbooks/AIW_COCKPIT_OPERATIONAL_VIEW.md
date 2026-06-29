# AIW Cockpit Operational View

## Resultado

Implementado.

O Cockpit evoluiu de uma bancada de evidencia para uma visao operacional inicial: filtros locais de runs, timeline por run, painel de patches mais navegavel e Context Pack Health read-only. A mudanca continua local-only, sem OpenHands, sem Hermes, sem provider externo e sem RAG vetorial.

## UX adicionada

- Filtros de runs:
  - Todos;
  - Online;
  - Offline;
  - Legacy;
  - Com tools;
  - Com patches;
  - Falhou.
- Timeline por run:
  - tarefa criada;
  - modelo iniciado;
  - tools executadas;
  - patch proposto/aplicado/revertido;
  - execucao finalizada;
  - falha upstream/timeout quando aplicavel.
- Painel de patches:
  - filtros Todos, Preview, Applied e Rolled back;
  - patch id curto;
  - arquivo alvo;
  - status;
  - motivo;
  - run associado;
  - data/hora;
  - resumo de diff;
  - diff tecnico colapsado.
- Context Pack Health:
  - status de produto: contexto bom, incompleto ou precisa atencao;
  - checks de docs, arquitetura, runbooks, roadmap, runtime e runs.

## Context Pack Health

O painel calcula tudo localmente e em modo read-only:

- README existe;
- quantidade de docs em `docs/`;
- quantidade de runbooks;
- ultimos runbooks modificados;
- quantidade de arquivos em `docs/architecture/`;
- quantidade de arquivos em `docs/roadmap/`;
- presenca de `docs/MODEL_STRATEGY.md`;
- presenca de `docs/model-bench/`;
- presenca de `config/litellm.yaml`, sem ler conteudo;
- presenca de `aiw_runtime/`;
- scripts AIW principais;
- branch atual;
- HEAD curto;
- quantidade de runs recentes;
- patches pendentes;
- ultimo run offline;
- ultimo run online.

## Seguranca

- Nao le `.env`.
- Nao altera `.env`.
- Nao imprime secrets.
- Nao altera `config/litellm.yaml`.
- Nao usa OpenHands.
- Nao integra Hermes.
- Nao chama provider externo.
- Nao cria embeddings.
- Nao mistura Context Pack com execucao de tools.
- Apply/rollback continuam restritos a `patch_id`.

## Validacoes executadas

```text
git status -sb
git log --oneline -8
git branch --show-current
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

- Ainda nao ha RAG vetorial.
- Context Pack e read-only.
- Filtros sao locais/simples.
- Provider externo pode falhar sem afetar offline mode.
- A timeline depende dos artefatos de run ja gravados.

## Proximo passo recomendado

Adicionar uma camada de navegacao operacional por projeto:

1. agrupar runs por task/projeto;
2. criar filtros persistentes por status/tool;
3. ligar Context Pack a um indice local auditavel;
4. adicionar busca lexical antes de busca vetorial;
5. criar evals de qualidade de contexto antes de fine-tuning.
