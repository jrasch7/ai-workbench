# AIW Cockpit Navigation and Local Search

## Resultado

Implementada camada inicial de navegação por projetos/tasks e busca lexical puramente local no AI Workbench Cockpit, mantendo arquitetura serverless-like do bash/python e sem dependências externas.

## UX adicionada

- Navegação por projeto/task: seção "Projetos e tarefas (Workspace)" consolidando dados do branch, git HEAD e runs.
- Filtros persistentes: Estado de filtros e query de busca salvos via `localStorage`, mantendo tudo state-free no server.
- Busca lexical local: caixa de busca e modal/lista de resultados no frontend, servida por `GET /api/search?q=...`.
- Context Pack Health v1.1: Agora mede quantidade de documentos indexáveis, runs, patches e informa se a busca local está disponível ou não.

## Escopo da busca

A busca percorre os seguintes escopos do `.aiw/` e diretório raiz:
- Resumos de runs (`summary.md`, `tool-traces.jsonl`, `commands.log`)
- Tasks nas diversas filas (inbox, running, etc.)
- Patches propostos e razões (`.aiw/patches/*.json`)
- Documentação na pasta `docs/` e `README.md` raiz.

## Segurança e masking

- Todas as respostas mascaram informações sensíveis baseadas nas keywords de masking do AI Workbench (keys, tokens, secrets, .env, LITELLM_MASTER_KEY).
- A busca restringe-se aos diretórios seguros e filtra respostas de forma que secrets não sejam exportados para a API REST e `.env` nunca retorne nos resultados.
- AUI continua usando as diretivas de escape em HTML (`html.escape`) e sanitização rigorosa.

## Validações executadas

- Syntax check Python e Bash (`bash -n`).
- Execução de Embedded Python compilando com `exec`.
- Teste de dry-run agent offline.
- Tool smoke test passando todos os guardrails.
- Rejeição ativa de path transversal (`../`) e bloqueio em `.env` e pushes de git.
- Teste HTTP com sucesso e preservação do HTML original do Cockpit.

## Limitações

- Busca lexical simples implementada em Python nativo.
- Sem embeddings de texto ou RAG vetorial.
- Sem provider externo ou bibliotecas complexas para NLP.
- Indexação e busca feitas on-the-fly sem cache indexado contínuo.
- Foco em um projeto único por enquanto (repositório atual local do AIW).

## Próximo passo recomendado

Considerar evolução para indexação contínua leve baseada em cache JSON (como Whoosh ou BM25 local), e eventualmente implementar memory state para agents em contexto vetorial (RAG) assim que aprovada a arquitetura.
