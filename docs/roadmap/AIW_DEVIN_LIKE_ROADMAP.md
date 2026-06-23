# AIW Devin-like Roadmap

## Visão geral

Este roadmap descreve a evolução planejada do **AI Workbench (AIW)** em fases, alinhado à estratégia de transformar o sistema em uma plataforma *Devin‑like* de engenharia de software assistida por IA. Cada fase tem:
- **Objetivo**: meta principal da fase.
- **Entregáveis**: artefatos produzidos.
- **Dependências**: pré‑requisitos de fases anteriores ou de infraestrutura.
- **Critério de pronto**: condições de aceitação que permitem prosseguir.

---

### Phase 0 – Base AIW

- **Objetivo**: Estrutura mínima operável (repositório, CI, agente de execução simples).
- **Entregáveis**:
  - Repositório inicial com estrutura de pastas (`docs/`, `agents/`, `scripts/`).
  - Configuração de ambiente Python (venv, dependências).
  - Primeiro agente *Executor* que executa comandos seguros.
- **Dependências**: Nenhuma.
- **Critério de pronto**:
  - `git status --short` limpo.
  - Testes de smoke (`scripts/aiw-runner-once`) passam.
  - Documentação mínima (`README.md`).

---

### Phase 5 – Cockpit MVP

- **Objetivo**: UI básica para criar, monitorar e revisar missões.
- **Entregáveis**:
  - UI web (React) simples.
  - Integração com *Mission/Run Manager*.
- **Dependências**: Phase 0.
- **Critério de pronto**:
  - Usuário pode criar missão e ver status.
  - Logs persistidos em `logs/`.

---

### Phase 6 – Monitoring

- **Objetivo**: Coleta de métricas e alertas de execução.
- **Entregáveis**:
  - Dashboard de métricas.
  - Alertas por email/Slack.
- **Dependências**: Phase 5.
- **Critério de pronto**:
  - Métricas reais exibidas.
  - Alertas disparados em falha de agente.

---

### Phase 6.5 – Hardening (não será feito neste PC)

---

### Phase 7 – Analysis / Handoff / Validator

- **Objetivo**: Analisar resultados, gerar handoffs e validar antes de merge.
- **Entregáveis**:
  - Módulo *Validator*.
  - Formato de handoff (`docs/handoffs/`).
- **Dependências**: Phase 6.
- **Critério de pronto**:
  - Handoff contém diff, logs e recomendações.

---

### Phase 7.5 – UI de Análise

- **Objetivo**: Interface visual para revisão de handoffs e métricas.
- **Entregáveis**:
  - Tela de revisão de handoffs no Cockpit.
- **Dependências**: Phase 7.
- **Critério de pronto**:
  - Usuário pode aprovar/rejeitar via UI.

---

### Phase 8 – Worktree / Sandbox

- **Objetivo**: Execução isolada de missões em *worktrees*.
- **Entregáveis**:
  - Script de criação/remoção de worktree.
  - Integração com *Run Manager*.
- **Dependências**: Phase 7.5.
- **Critério de pronto**:
  - Worktree criado/removido sem resíduos.
  - Diff gerado e handoff produzido.

---

### Phase 9 – RAG / Context Engine

- **Objetivo**: Recuperação de contexto automática usando LangChain.
- **Entregáveis**:
  - Indexador de documentos (`scripts/aiw-rag-index.py`).
  - Retriever integrado ao agente.
- **Dependências**: Phase 8.
- **Critério de pronto**:
  - Busca retorna trechos relevantes <300 ms.
  - Nenhum segredo exposto nos índices.

---

### Phase 10 – Evals / Observability

- **Objetivo**: Avaliação automática de respostas e observabilidade avançada.
- **Entregáveis**:
  - Suite de testes de qualidade (precision/recall).
  - Dashboard de observabilidade.
- **Dependências**: Phase 9.
- **Critério de pronto**:
  - Métricas de avaliação disponíveis.
  - Alertas configurados para degradação.

---

### Phase 11 – Provider Router

- **Objetivo**: Roteamento inteligente entre provedores de modelo (OpenAI, Anthropic, etc.).
- **Entregáveis**:
  - Camada de seleção baseada em custo, latência, disponibilidade.
- **Dependências**: Phase 10.
- **Critério de pronto**:
  - Sistema escolhe provedor automaticamente.

---

### Phase 12 – Telegram / Remote Control

- **Objetivo**: Controle remoto via Telegram bot.
- **Entregáveis**:
  - Bot Telegram integrado ao *Run Manager*.
- **Dependências**: Phase 11.
- **Critério de pronto**:
  - Usuário pode iniciar missão via chat.

---

### Phase 13 – Fine‑tuning / Dataset

- **Objetivo**: Treinar modelos customizados a partir de dataset real de execuções.
- **Entregáveis**:
  - Pipeline de coleta de dataset.
  - Modelo fine‑tuned.
- **Dependências**: Phase 12 + dados coletados das fases anteriores.
- **Critério de pronto**:
  - Modelo melhora métricas de avaliação em >5%.

---

*Este roadmap está alinhado com as decisões arquiteturais definidas nos ADRs e documentos de fase. Cada fase é de baixo risco e foca em documentação, isolamento e instrumentação antes de introduzir mudanças de código complexas.*
