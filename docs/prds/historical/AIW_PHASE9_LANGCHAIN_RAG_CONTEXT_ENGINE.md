# PRD: Phase 9 – LangChain RAG / Context Engine

**Objetivo**

Implementar um motor de Recuperação de Contexto (RAG) baseado em LangChain que permita aos agentes do AIW acessar rapidamente a documentação interna, runbooks, ADRs, PRDs, handoffs e logs resumidos, melhorando a qualidade das respostas e diminuindo a necessidade de prompts extensos.

**Problema de Contexto**

- Agentes atualmente dependem de *prompt engineering* manual para incluir informações relevantes.
- Documentos evoluem rapidamente; copiar/colar trechos estático torna‑se desatualizado.
- Falta de mecanismo de busca semântica impede a utilização eficiente de todo o conhecimento armazenado no repositório.

**Fontes de Dados**

| Fonte | Tipo | Observação |
|-------|------|------------|
| `README.md` | Texto | Visão geral do projeto |
| `ROADMAP.md` | Texto | Estratégia de fases |
| `AGENTS/` | Texto | Definições de agentes e papéis |
| Runbooks (`docs/runbooks/`) | Texto | Procedimentos operacionais |
| ADRs (`docs/decisions/`) | Texto | Decisões arquiteturais |
| PRDs (`docs/prds/`) | Texto | Requisitos detalhados |
| Handoffs (`docs/handoffs/`) | Texto | Resumos de execuções anteriores |
| Logs resumidos (`logs/summary/`) | Texto | Métricas e resultados |
| Snapshots (`snapshots/`) | Texto/JSON | Estado de arte dos agentes |

**Arquitetura**

1. **Document Loader** – `RecursiveCharacterTextLoader` (ou `UnstructuredMarkdownLoader`) varre os diretórios acima e carrega conteúdo bruto.
2. **Chunking** – `RecursiveCharacterTextSplitter` com tamanho de chunk ~1000 tokens e sobreposição de 200 para manter contexto.
3. **Embeddings** – `OpenAIEmbeddings` (ou modelo local equivalente) gera vetores densos.
4. **Vector Store** – `FAISS` local (persistido em `./.vectorstore/aiw_rag`) para buscas rápidas.
5. **Retriever** – `FAISSRetriever` com top‑k = 5‑10 resultados.
6. **Context Pack** – Monta prompt com trechos recuperados, incluíndo fonte e trechos relevantes.
7. **Envio ao Executor** – O *Hermes Executor* recebe o prompt enriquecido e continua a execução da missão.

**Começar Simples**

- Implementar pipeline de indexação e busca offline (script `scripts/aiw-rag-index.py`).
- Atualizar periodicamente (ex.: via cron ou trigger manual) para refletir mudanças nos documentos.
- Não usar serviços externos para armazenamento de vetores; manter tudo local para evitar vazamento de segredos.

**Fine‑tuning Fora de Escopo**

- Ajustar embeddings ou treinar modelos de reranking será considerado em fases futuras (Phase 13).

**Critérios de Aceite**

- Indexador cria/atualiza vetor store sem erros.
- `search(query)` retorna trechos relevantes das fontes listadas.
- Agente pode solicitar contexto via `langchain.Retriever` e receber respostas precisas (>70% de relevância em avaliação manual).
- Não há vazamento de informações sensíveis (`git diff --check` passa limpo).
- Performance de busca < 300 ms para top‑5 resultados em repositório típico (~200 MD files).

**Riscos**

- **Contexto errado** – trechos irrelevantes podem confundir o agente; mitigado por validação humana inicial.
- **Docs desatualizadas** – índice pode ficar desalinado; mitigado por re‑indexação frequente.
- **Custo** – chamadas de embeddings (OpenAI) podem gerar custos; uso de modelo local pode ser necessário.
- **Vazamento de Secrets** – garantir que arquivos com credenciais (`.env`, `secrets/`) estejam excluídos do loader.
- **Indexação de reports grandes** – pode consumir muita memória; usar chunking adequado.

**Plano de Validação**

1. Executar script de indexação em repositório de teste.
2. Realizar buscas de controle (`search('como criar worktree')`) e validar relevância.
3. Medir latência e consumo de memória.
4. Revisar vetores gerados para garantir ausência de textos sensíveis.
5. Documentar procedimento de atualização do índice.
