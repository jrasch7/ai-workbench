# AIW Context / RAG Local Index v1

Este runbook detalha o funcionamento do **Context / RAG Local Index v1**, o sistema de recuperação e indexação local (léxica) utilizado pelo AI Workbench.

## Objetivo do Context / RAG Local Index

O objetivo deste mecanismo é varrer o repositório do usuário, mapear os arquivos úteis e fatiar ("chunkar") seus conteúdos em segmentos textuais para buscas semânticas simplificadas (léxicas nesta v1). Ele fornece a fundação do RAG (Retrieval-Augmented Generation) para que o agente possa obter contexto do projeto sem estourar o limite de tokens dos LLMs.

## O que esta versão faz

- Vare todo o projeto iterativamente.
- Aplica exclusão rígida e determinística sobre artefatos, dependências compiladas e arquivos sensíveis (ex: `.env`, `litellm.yaml`).
- Executa o "chunking" por arquivo (tamanhos de aprox. 4000 caracteres, com sobreposição de 200).
- Gera estimativa simples de tokens (`chars // 4`).
- Produz metadados persistentes: `manifest.json`, `files.json` e `chunks.jsonl`.
- Permite pesquisa local via busca léxica nativa com pontuação simples (term match e path match).

## O que esta versão NÃO faz

- **Não implementa Embeddings**: Esta versão foca em validação de pipeline e segurança. Nenhuma API de modelo (OpenAI, Ollama) é consultada para vetorização.
- **Não usa Bancos de Dados Vetoriais**: Ferramentas como FAISS, ChromaDB ou LanceDB foram deixadas para iterações futuras para minimizar a complexidade inicial.

## Como rodar a indexação

Pode ser executada isoladamente ou disparada pelos componentes de core do AIW:

```bash
python3 -m aiw_context.indexer --workspace aiw
```

## Como rodar a busca local

A busca pode ser testada via CLI para auditar como os chunks estão sendo retornados:

```bash
python3 -m aiw_context.search --workspace aiw --query "agent dispatcher" --limit 5
```

## Onde ficam os artifacts

Todo o resultado da indexação fica agrupado no escopo da respectiva workspace:
`.aiw/workspaces/<workspace_id>/context/`

Arquivos gerados:
- `manifest.json`: Informações agregadas sobre o índice (quantidade de arquivos, ignorados, timestamps).
- `files.json`: Lista de todos os caminhos indexados.
- `chunks.jsonl`: Arquivo linha a linha (JSON Lines) contendo o conteúdo literal fatiado com offsets.
- *(Opcional/Legado)* `search-index.json` e `context-pack.json`: Mantidos para compatibilidade com a fase inicial do AIW Runner.

## Quais arquivos são ignorados

Para garantir segurança e performance, o indexador possui uma blocklist hardcoded:
- Diretórios completos: `.git`, `node_modules`, `dist`, `build`, `coverage`, `reports`, `logs`, `__pycache__`, `.aiw/`
- Arquivos exatos: `.env`, `.env.*`, `AGENTS.md`, `config/litellm.yaml`
- Extensões binárias e grandes: `.pyc`, `.pyo`, `.sqlite`, `.db`, `.zip`, `.tar`, `.gz`, `.png`, `.jpg`, `.jpeg`, `.webp`, `.pdf`

*Segurança Adicional:* Arquivos ou chunks cujos nomes ou textos contenham cadeias de segredo conhecidas (ex: `api_key`) são explicitamente barrados ou mascarados.

## Como isso será usado pelo Context Pack Builder

Na próxima sprint, o `Context Pack Builder` vai deixar de ser um pacote fixo (`docs/` + `README`) e vai adotar o `search.py` criado aqui para extrair apenas os chunks relevantes à Task Atual, montando dinamicamente um arquivo com escopo limitado aos tópicos de interesse do Agente.

## Como isso será usado pelo futuro Agent Loop

O agente iterativo do AIW, quando se encontrar preso ou precisar de conhecimento aprofundado de um arquivo sem abri-lo inteiro via Tool (`file_read`), acionará uma Tool delegada do Registry (ex: `rag_search_local`) para consultar dinamicamente a codebase e entender o terreno.

## Por que Embeddings e Ollama ficam para depois?

O objetivo principal da arquitetura do AIW é provar que a infraestrutura (Dispatcher, Registry, Chunking, Evidencing, Worker Loop) é robusta, segura e funcional *offline*, sem acoplamento cego à IA. A adição da IA vetorial é trivial depois que a máquina engrenar.
