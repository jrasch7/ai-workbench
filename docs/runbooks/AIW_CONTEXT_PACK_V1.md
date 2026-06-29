# AIW Context Pack v1

## Resultado

Implementação da camada do Context Pack auditável (v1) e de Cache Local do Search Index no AI Workbench Cockpit, adicionando o pacote em `/api/context/pack` e habilitando busca lexical veloz (`/api/search?q=...`) baseada no cache sem quebrar as restrições originais do sistema.

## Search Index Cache

O índice de busca é gerado localmente sem provedores externos sob `.aiw/context/search-index.json`. 
Ele extrai e salva snippets de resumos das execuções de agents (runs), propostas de modificações (patches), relatórios de tasks e de toda a documentação da pasta `docs/` e `README.md`.
Na UI do Cockpit, é possível acionar o Rebuild manual ou checar via API. Se o cache não estiver disponível no momento da busca, a varredura direta via shell script é chamada como fallback sem impacto na experiência de pesquisa.

## Context Pack

O Context Pack (`.aiw/context/context-pack.json`) contém os contadores consolidados e as meta-informações do head/branch atual e metadados de documentações chave (runbooks, roadmap e arquitetura), facilitando o RAG futuro ou análises diagnósticas das pastas `docs/`. O endpoint `/api/context/pack` provê os dados formatados em JSON puro.

## Endpoints

- `GET /api/context/status`: Entrega as estatísticas de saúde do ambiente (checks se os scripts, configs de litellm, modelo de agente estão sadios) com adição dos totais de runs indexadas e status do cache.
- `POST /api/context/rebuild`: Reconstrói atomicamente o Context Pack e o Search Index cache varrendo e escaneando o sistema e truncando resumos em um limite em memória local.
- `GET /api/context/pack`: Retorna a carga com o Context Pack serializado (docs/arquivos com path e resumo rápido).
- `GET /api/search?q=...`: Motor de pesquisa unificado que agora consome o cache local otimizado (`source: "cache"`) ou varredura de emergência on-the-fly (`source: "direct"`).

## Segurança e masking

- Proteção robusta contra vazamento de credenciais na indexação (palavras com `key`, `secret`, `token` em path ignorados, assim como arquivos ocultos e `.env`).
- Os recortes de texto indexados passam por filtros que substituem sentenças contendo credenciais mascaradas (`[masked]`) antes de irem pro cache.
- `.env` explícitamente barrado da varredura, leitura e cache no Indexer nativo em `aiw_context`. 

## Validações executadas

- Reestruturação de f-strings com sintaxe validada. Check python embarcado.
- Rodada de testes Offline mode da suíte smoke e Tool Smoke test aprovados integralmente sem bypass.
- Smoke de APIs testados usando curl para simular chamadas de `status`, `rebuild` e `search` comprovando mutação correta de JSONs de contexto.

## Limitações

- Busca puramente lexical e linear sobre o JSON com score via pontuações simples.
- Sem RAG vetorial real ou chunking inteligente semântico.
- Nenhuma dependência instalada, o que inibe um parser em PDF ou binário por agora.
- Indexações devem ser acionadas manualmente pelo botão reconstruir se a base estiver velha.

## Próximo passo recomendado

Ao implementar LLM contextual, o Context Pack formatado poderá ser injetado em um prompt inicial ("system prompt" pre-configurado) sem requerer pesquisa extra, ou injetar metadados para orientar um Worker de Research/Planner ao indexar o vector store. Recomendado adicionar auto-rebuild cron em runtimes pesados para aliviar requisições defasadas de usuários sem ação.
