# AIW Agent Context Injection

## Descrição
No AI Workbench, o Runner (`scripts/aiw-runner-agent`) agora possui a capacidade de injetar um contexto condensado e rico nas iterações do LLM. Esse contexto provém do **Context Pack v1**, que indexa referências cruciais como `README.md`, `runbooks`, `architecture` e relatórios passados.

## Como utilizar

Para habilitar a injeção do Context Pack, execute o agent com a flag de ambiente habilitada:

```bash
AIW_USE_CONTEXT_PACK=1 ./scripts/aiw-runner-agent
```

Se o agente rodar em modo offline, as evidências também serão salvas e o comportamento auditado com sucesso:

```bash
AIW_AGENT_OFFLINE=1 AIW_USE_CONTEXT_PACK=1 ./scripts/aiw-runner-agent --offline
```

## Mecanismo de Injeção

1. O runner invoca `build_agent_context(ROOT)` em `aiw_context.indexer`.
2. O indexador lê o cache de contexto (`.aiw/context/context-pack.json`). Se não existir, faz o rebuild de emergência e consome localmente.
3. As fontes vitais são agregadas em um grande bloco concatenado pré-inserido na prompt original (`task_content`).
4. Duas provas de execução são armazenadas na pasta da Run atual:
   - `context-used.md`: Um log legível com as marcações de documentos lidos.
   - `context-used.json`: Estrutura técnica documentando o `repo_head` e metadados de quais arquivos o Agent leu da arquitetura ou runbooks.

## Auto-Rebuild

Ao final de cada execução no `aiw-runner-agent`, chamamos silenciosamente a API `best_effort_rebuild()`. Essa função roda sincronicamente (ou assíncrona futura), indexando as modificações frescas e patches executados. Os logs desta transação ficam isolados no próprio dir da run sob `context_rebuild.log`. Nenhum erro quebrado deste script corrompe o fluxo ou estado principal do Agent.

## Restrições Preservadas

- Nenhum documento censurado (`.env`) é tocado ou cacheado.
- Segredos são barrados agressivamente.
- Providers externos NÃO são chamados para construir as árvores ou RAG vetoriais em runtime; tudo decorre do OS em varreduras estáticas limpas e eficientes.
