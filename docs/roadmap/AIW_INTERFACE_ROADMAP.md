# AIW Interface Roadmap

## Visão geral

Este roadmap descreve a evolução planejada da interface do AI Workbench (AIW) a partir do ponto em que o Paperclip foi removido do caminho crítico. Cada fase entrega funcionalidades incrementais que permitem ao Cockpit evoluir de um MVP de análise (Phase 7.5) para um cockpit completo com observabilidade, gerenciamento de provedores e integração com plataformas externas.

---

### Phase UI-0 – Inventário do Cockpit Atual

- **Objetivo**: Documentar o estado atual do Cockpit (telas existentes, endpoints, dados suportados).
- **Entregáveis**:
  - Lista de telas e componentes já presentes.
  - Mapa de dependências com Hermes, LangGraph e Git.
- **Dependências**: Nenhuma.
- **Critério de pronto**:
  - Documento Markdown entregue em `docs/architecture/`.
  - Revisado por pelo menos um engenheiro senior.
- **Riscos**: Nenhum risco significativo.

---

### Phase UI-1 – Consolidar Shell / Dashboard

- **Objetivo**: Implementar a tela "Dashboard" que consolida métricas globais (runs hoje, erros, status de agentes).
- **Entregáveis**:
  - UI Dashboard responsiva.
  - API backend que agrega contadores a partir dos metadados de runs.
- **Dependências**: UI existente do Cockpit, camada de métricas (Phase 6).
- **Critério de pronto**:
  - Dashboard exibe dados corretos em tempo real.
  - Testes unitários cobrem a agregação.
- **Riscos**:
  - Overhead de chamadas frequentes; mitigado por caching curta.

---

### Phase UI-2 – Run Detail com Logs

- **Objetivo**: Tela de detalhe de run que apresenta `metadata.json`, log bruto, diff summary e botão de download.
- **Entregáveis**:
  - Página Run Detail.
  - Visualização de logs com realce de "ERROR"/"WARNING".
  - Link para download do patch completo.
- **Dependências**: Phase UI-1, contrato de artefatos definido em `AIW_ANALYSIS_HANDOFF_VALIDATOR_CONTRACTS.md`.
- **Critério de pronto**:
  - Todos os artefatos listados carregam sem erro.
  - Botão de download gera arquivo correto.
- **Riscos**:
  - Logs muito grandes podem travar a UI; mitigado por paginação.

---

### Phase UI-3 – Analysis / Handoff / Validator

- **Objetivo**: Integrar as telas de Analysis, Handoff e Validator dentro da Run Detail, permitindo aprovação/rejeição.
- **Entregáveis**:
  - Seção de Diff Summary editável.
  - Renderizador de `handoff.md` com Markdown.
  - Checklist de `validation.json` com status colorido.
  - Botões **Aprovar**/**Rejeitar** que gravam `analysis.json`.
- **Dependçês**: UI-2 + contratos de data.
- **Critério de pronto**:
  - Aprovação cria commit versionado.
  - Validação falha desabilita aprovação.
- **Riscos**:
  - Condições de corrida entre UI e Git; mitigado por lock de arquivo.

---

### Phase UI-4 – Agent / Provider Status

- **Objetivo**: Tela que exibe catálogo de agentes ativos e provedores configurados, com indicadores de saúde.
- **Entregáveis**:
  - Lista de agentes (nome, estado, última execução).
  - Lista de provedores (OpenAI, Anthropic, etc.) com teste de ping.
- **Dependências**: UI-3, integração com Provider Router (Phase 11 futura).
- **Critério de pronto**:
  - Dados atualizados a cada ciclo de run.
  - UI indica provedor offline em vermelho.
- **Riscos**:
  - Latência ao checar provedores externos; usar cache de 30s.

---

### Phase UI-5 – Worktree / Sandbox Visual

- **Objetivo**: Visualizar worktrees criados (Phase 8) dentro do Cockpit, permitindo inspeção de arquivos antes de merge.
- **Entregáveis**:
  - Lista de worktrees ativos com caminho, branch e status.
  - Botão "Abrir" que abre visualização de arquivos (read‑only).
- **Dependças**: UI-4, implementação worktree (Phase 8).
- **Critério de pronto**:
  - Usuário pode explorar arquivos sem modificar.
  - Integração com Git diff.
- **Riscos**:
  - Exposição acidental de segredos; garantir que worktrees nunca contenham `.env`.

---

### Phase UI-6 – RAG / Knowledge Visual

- **Objetivo**: Exibir status do índice RAG (tamanho, última atualização, erros) e permitir busca simples de documentos.
- **Entregáveis**:
  - Dashboard de vetor store (FAISS ou similar).
  - Campo de busca de texto que utiliza o retriever configurado.
- **Dependças**: Phase UI-5, script de indexação (Phase 9).
- **Critério de pronto**:
  - Busca retorna resultados dentro de 300ms.
  - Dashboard mostra última data de reindex.
- **Riscos**:
  - Custo de embeddings externos; mitigado por modelo local.

---

### Phase UI-7 – Observability / Evals com LangSmith (ou alternativa local)

- **Objetivo**: Integrar LangSmith (ou substituto local) para exibir traces, latência, custo e resultados de evals.
- **Entregáveis**:
  - Tela "Observability" com lista de traces por run.
  - Métricas de custo/tempo por agente.
- **Dependças**: Phase UI-6, conta LangSmith configurada.
- **Critério de pronto**:
  - Usuário pode filtrar traces por agente/data.
  - Falhas de comunicação com LangSmith são tratadas graciosamente.
- **Riscos**:
  - Dependência externa; fallback para logs locais se API falhar.

---

### Phase UI-8 – Avaliar Open Agent Platform (OAP)

- **Objetivo**: Laboratório de integração com OAP para orquestração avançada de agentes e possível aceleração de fluxos.
- **Entregáveis**:
  - Prototipo de conectação OAP (sandbox).
  - Relatório de resultados de smoke‑test (performance, compatibilidade).
- **Dependças**: Phases anteriores concluídas, especialmente UI-7 para observabilidade.
- **Critério de pronto**:
  - Smoke‑test concluído com sucesso (todos os testes < 5s, sem erros críticos).
  - Decisão documentada se OAP será adotado ou descartado.
- **Riscos**:
  - Integração inesperada com APIs proprietárias; mitigado por isolamento de rede.

---

## Estratégia de Entrega Incremental

1. **MVP (Phase UI-3)** será entregue junto com a PRD `AIW_COCKPIT_INTERFACE_MVP.md` (já criada). Ele cobre Dashboard, Runs, Run Detail e aprovação.
2. **Iterações** subsequentes adicionam visualização de Worktree, RAG e Observability, permitindo que cada nova tela reutilize contratos já existentes.
3. **Feedback Loop**: a cada fase, a equipe revisa métricas de usabilidade e ajusta o design antes de avançar.

Este roadmap garante que, mesmo sem Paperclip, o AIW mantenha uma interface rica, controlada e segura, evoluindo de forma alinhada com as prioridades de produto.
