# AIW Agent Stack Overview

**Visão geral**

O AI Workbench (AIW) funciona como uma plataforma *Devin‑like* interna, orquestrando agentes de IA que executam tarefas de engenharia de software de forma controlada e rastreável.

## Camadas da pilha

1. **AIW Cockpit** – UI operacional que expõe missões, monitoramento e handoffs.
2. **Mission/Run Manager** – Agenda missões, controla ciclos de execução e coleta métricas.
3. **LangGraph Engineering Loop** – Motor de orquestração baseada em *LangGraph* que define o fluxo de etapas reproducíveis.
4. **Hermes Executor** – Executor local que roda ferramentas, scripts e comandos de shell.
5. **LangChain Context Engine / RAG** – Camada de recuperação e augmentação de contexto (document loaders, chunking, embeddings, vector store).
6. **Obsidian/Git Knowledge Layer** – Fonte de verdade documental (MD files, ADRs, PRDs) versionada via Git.
7. **Provider Router** – Seleciona provedores de modelo (OpenAI, Anthropic, etc.) e roteia chamadas.
8. **Validator/Integrator** – Valida saídas, gera diffs, cria handoffs e pode integrar mudanças.
9. **Sandbox/Worktree** – Worktrees isolados para execução segura de missões sem contaminar a branch principal.
10. **Logs/Metadata/Handoff** – Persistência de logs, metadados de execução e artefatos de entrega.

## O que **não** está incluído por enquanto

- Fine‑tuning de modelos
- Paperclip como executor de código
- Ralph (gerenciamento de recursos avançado)
- Kubernetes / orquestração de containers
- Frameworks de multi‑agente como CrewAI ou AutoGen

## Sequência recomendada de fases

| Ordem | Fase | objetivo |
|------|------|----------|
| 1 | **Phase 7.5** – UI de análise | Visualização de resultados e métricas |
| 2 | **Phase 8** – Worktree / Sandbox | Execução isolada de missões |
| 3 | **Phase 9** – LangChain RAG | Camada de recuperação de contexto |
| 4 | **Phase 10** – Evals / Observability | Avaliação automática e métricas de qualidade |
| 5 | **Phase 11** – Provider Router | Roteamento avançado entre provedores |
| 6 | **Phase 12** – Fine‑tuning (dados reais) | Treinamento de modelos customizados |

Esta arquitetura de baixo risco permite avançar a documentação e o planejamento sem tocar no código do Cockpit que ainda está em desenvolvimento no outro computador.
