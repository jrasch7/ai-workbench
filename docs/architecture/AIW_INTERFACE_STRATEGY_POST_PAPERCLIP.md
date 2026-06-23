# AIW Interface Strategy Post-Paperclip

## Problema

A remoção do Paperclip como executor/exposição visual elimina a camada pronta de *dashboard* / *org‑chart* / *agent manager* que antes servia como interface de observabilidade e de gerenciamento de agentes. Sem um substituto, os usuários perdem uma visão consolidada das runs, dos agentes ativos, das métricas e dos artefatos de handoff, o que dificulta a validação e o acompanhamento das execuções automatizadas.

## Decisão Arquitetural

| Componente | Papel na Estratégia | Racional |
|------------|---------------------|----------|
| **AIW Cockpit** | Interface operacional principal. Exibe dashboards, listas de runs, detalhes de execução, handoffs, validações e controles de agentes e provedores. | Controle total sobre UI/UX, integração estreita com Hermes (executor local) e com o repositório Git. Permite customização para o fluxo da equipe (Nivela, SisOpERP). |
| **LangGraph Studio / LangSmith Studio** | Ferramenta de desenvolvimento e depuração visual. Permite criar, editar e inspeccionar fluxos de LangGraph, monitorar estados, entradas/saídas de nós. | Fornece um *debugger* visual avançado sem impactar produção; uso opcional por engenheiros. |
| **LangSmith** | Plataforma de observabilidade, tracing, avaliações e métricas de desempenho de agentes. Pode ser configurada como serviço externo ou local. | Excelente para *e‑vals* e *observability* (Phase 10) sem precisar de um executor externo. |
| **Open Agent Platform (OAP)** | Ambiente de laboratório para experimentar integrações de agentes‑a‑serviço e orquestração avançada. | Avaliado em sandbox; não será adotado como padrão antes de um *smoke test* bem‑sucedido. |
| **Paperclip** | Mantido apenas como referência conceitual/documental. Não executa código nem controla UI. | Evita dependência de SaaS crítico enquanto preserva a documentação de arquitetura histórica. |

## Mapa de Telas Necessárias no AIW Cockpit

| Tela | Descrição | Fase de Implementação |
|------|-----------|----------------------|
| **Dashboard** | Visão geral de métricas, estado dos agentes, status de runs recentes. | Phase 7.5 (MVP) |
| **Runs** | Lista paginada de todas as execuções com filtros por agente, data, status. | Phase 7.5 |
| **Run Detail** | Detalhes de uma run: metadata, log, diff, handoff, validações. | Phase 7.5 |
| **Analysis** | UI para acionar análise, exibir diff summary, visualizar resultados de LangGraph. | Phase 7.5 |
| **Handoff** | Renderização do `handoff.md` com recomendações e próximos passos. | Phase 7.5 |
| **Validator** | Exibição de `validation.json`, lista de falhas, botão de aprovação/rejeição. | Phase 7.5 |
| **Agents** | Catálogo de agentes definidos, status (idle, running, erro), métricas de uso. | Phase 8 |
| **Missions** | Gerenciamento de missões/agendas, criação de novas missões, histórico. | Phase 8 |
| **Providers** | Visão dos provedores configurados (OpenAI, Anthropic, etc.) e seu estado de saúde. | Phase 11 |
| **Knowledge / RAG Status** | Estado do índice RAG (tamanho, última atualização, erros). | Phase 9 |
| **Settings** | Configurações do Cockpit, integração com Hermes, credenciais de provedores (sem secrets). | Phase 5 (existente) |

## Riscos

1. **Sobrecarga de UI** – Muitas telas podem atrasar entregas; mitigado por roadmap incremental.
2. **Dependência de SaaS (LangSmith, OAP)** – Falhas externas podem impactar a observabilidade; mitigado por fallback local e uso opcional.
3. **Sincronização de contratos** – Mudanças nos artefatos (handoff, validation) podem quebrar a UI; mitigado por ADRs versionados.
4. **Segurança de dados** – Exposição inadvertida de secrets nos logs; mitigado por `git diff --check` e política de auditoria.

## Sequência Incremental

1. **Phase 7.5 – UI de Análise** (Dashboard, Runs, Run Detail, Analysis, Handoff, Validator).
2. **Phase 8 – Worktree/Sandbox Visual** (Agents, Missions).
3. **Phase 9 – RAG/Knowledge Visual** (Knowledge status, integração com LangChain).
4. **Phase 10 – Observability** (Integração LangSmith, métricas avançadas).
5. **Phase 11 – Provider Router UI** (Providers, configuração de roteamento).
6. **Laboratório OAP** – Prototipar integração opcional após validação das fases anteriores.

Esta estratégia garante que a interface do AIW siga um caminho controlado, evoluindo de um MVP de análise para um cockpit completo, sem reintroduzir Paperclip como executor.
