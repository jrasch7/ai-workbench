# AIW Context Engineering

## Visão Geral
Esta página descreve a engenharia de contexto que suporta a **Phase 7.6 – Context Resilience / Auto‑Compaction**. O objetivo é separar claramente os diferentes tipos de "memória" que o agente AIW utiliza e definir como eles são armazenados, atualizados e consumidos.

## Tipos de Contexto
| Tipo | Propósito | Fonte de Verdade | Persistência |
|------|-----------|------------------|--------------|
| **Prompt Context** | Texto enviado ao modelo para gerar a próxima resposta. | Construído a partir de arquivos de resumo e do estado da run. | Efêmero – gerado a cada chamada ao modelo.
| **Memória Curta** | Histórico recente de mensagens da sessão (últimas N mensagens). | Memória do modelo + `compact_summary.md`. | Mantido em memória apenas enquanto o run está ativo.
| **Memória Longa** | Histórico completo de toda a sessão, incluindo todas as iterações. | `metadata.json` + `commands.log` + `outputs.log`. | Persistido em disco no diretório da run.
| **Run State** | Estado de execução completo (artefatos, diffs, validações). | Artefatos de run no diretório `reports/aiw‑runs/<run_id>/`. | Persistido em disco; a única fonte de verdade para retomar.
| **Handoff** | Resumo final entregue a outro operador ou a um novo run. | `handoff.md` gerado a partir de `compact_summary.md`. | Persistido em disco.
| **RAG (Retrieval‑Augmented Generation)** | Busca de documentos externos para enriquecer o prompt. | Repositório Git / base de conhecimento local. | Consultado sob demanda; não persistido.

## Regras Fundamentais
1. **O modelo não é fonte de verdade** – quaisquer fatos críticos (código, commits, configurações) devem ser verificados contra Git ou disco.
2. **Git/disco são a única fonte de verdade** – todos os artefatos de run são gravados no sistema de arquivos.
3. **Prompt deve ser fino** – apenas o que for estritamente necessário para a próxima operação deve ser incluído.
4. **Carregamento sob demanda** – quando o agente precisa de contexto histórico, ele lê os arquivos relevantes (`metadata.json`, `diff.patch`, `validation.json`).

## Arquitetura de Contexto
```
+---------------------+        +-------------------+        +-------------------+
| Prompt Builder      | -----> | Compact Summary   | -----> | Resume Prompt     |
+---------------------+        +-------------------+        +-------------------+
        ^                              ^                          ^
        |                              |                          |
        |                              |                          |
+---------------------+        +-------------------+        +-------------------+
| Run State Store     | <----- | Handoff Summarizer| <----- | Model Fallback    |
+---------------------+        +-------------------+        +-------------------+
        |
        v
+---------------------+
| Context Pack Builder|
+---------------------+
        |
        v
+---------------------+
| Git / Disk Backend |
+---------------------+
```
- **Context Pack Builder**: Constrói o conjunto de arquivos (prompt, diffs, logs) que será enviado ao modelo.
- **Run State Store**: Diretório `reports/aiw‑runs/<run_id>/` contendo todos os artefatos descritos no documento de requisitos.
- **Handoff Summarizer**: Gera `handoff.md` e `compact_summary.md` a partir do run state.
- **Resume Prompt Generator**: Cria `resume_next_prompt.md` usando somente a informação essencial.
- **Model Fallback Policy**: Detecta falhas de taxa (429) e troca para modelo secundário, anotando a troca em `metadata.json`.

## Integrações Futuras
### LangGraph Checkpointing
- LangGraph poderá usar o **Run State Store** como backend de checkpoint, permitindo que a graph retome a partir de um ponto salvo.
- Cada checkpoint será serializado como `checkpoint_<step>.json` dentro do diretório da run.

### LangChain RAG
- O RAG buscará documentos relevantes nos diretórios `reports/aiw‑runs/` e `docs/` para fornecer contexto adicional ao modelo.
- As consultas serão registradas em `outputs.log` para auditabilidade.

---
*Este documento fornece a base arquitetural para a resiliência de contexto no AIW.*