# ADR: Cockpit as Primary Interface

**Status:** Proposed

## Contexto

- O AI Workbench (AIW) abandonou o Paperclip como executor, removendo a camada visual de gerenciamento que o Paperclip fornecia.
- O Cockpit já existe como UI operacional para criar missões, monitorar runs e exibir logs, mas ainda não cobre toda a experiência de desenvolvimento/debug que um painel visual completo oferece.
- LangGraph Studio e LangSmith fornecem ferramentas de visualização/debug, mas são orientadas a desenvolvedores e não ao fluxo completo de operação da equipe.
- Open Agent Platform (OAP) está em avaliação como potencial acelerador de orquestração, mas ainda não foi testado em produção.

## Decisão

1. **Cockpit** será a **interface principal** para todos os usuários (operacionais, gestores e engenheiros) em produção. Todas as telas de dashboard, runs, análise, handoff e validação estarão disponíveis nele.
2. **LangGraph Studio / LangSmith Studio** serão usados **apenas** como ferramentas auxiliares de desenvolvimento e depuração, não como UI de produção.
3. **LangSmith** será integrado para **tracing, observabilidade e avaliação** (Phase 10). Não substituirá o Cockpit, mas alimentará métricas que o Cockpit pode exibir.
4. **Open Agent Platform** será avaliado em **laboratório** como referência e possível futuro acelerador, mas **não será adotado como padrão** até a conclusão de um smoke‑test interno.
5. **Paperclip** permanece **fora do caminho crítico**; pode ser mantido apenas como documentação de arquitetura histórica ou referência conceitual.

## Motivo da Escolha

- **Controle total**: o Cockpit está sob total controle da equipe, permite customização de UI/UX adaptada ao fluxo de Nivela/SisOpERP.
- **Integração**: o Cockpit já se integra ao Hermes Executor, ao repositório Git e à camada de memória Obsidian, facilitando a implementação de contratos de handoff/validation.
- **Menor dependência SaaS**: reduzir a dependência de serviços externos críticos (Paperclip) aumenta a robustez e a segurança.
- **Flexibilidade**: ferramentas como LangGraph Studio e LangSmith podem ser usadas livremente por engenheiros sem impactar usuários finais.
- **Risco controlado**: a avaliação do OAP em laboratório permite experimentar sem afetar a produção.

## Consequências Positivas

- UI única e consistente para usuários finais.
- Redução de superfície de ataque ao eliminar dependência externa.
- Capacidade de evoluir a UI de forma incremental (Phase 7.5 → Phase 10).
- Melhor rastreabilidade dos artefatos (handoff, validation) dentro do Cockpit.

## Consequências Negativas

- Necessidade de investimento de desenvolvimento para expandir o Cockpit nas fases subsequentes.
- Ferramentas auxiliares (LangGraph Studio, LangSmith) exigem treinamento adicional para engenheiros.
- O OAP pode ficar subutilizado se o smoke‑test falhar.

## Alternativas Consideradas

| Alternativa | Prós | Contras |
|-------------|------|----------|
| **Retornar ao Paperclip** como executor e UI | UI pronta, integração automática | Violação das regras de segurança, dependência SaaS, perda de controle sobre execução local |
| **Usar somente LangSmith** como UI completa | Observabilidade avançada | LangSmith não fornece UI de gerenciamento de runs, handoffs, nem controlos de agentes; foco em métricas, não operação |
| **Usar somente LangGraph Studio** como UI | Depuração visual rica | Falta de funcionalidades de gerenciamento de missões, controle de usuários, integrações com Git/Obsidian |
| **Adotar Open Agent Platform agora** | Potencial aceleração de orquestração | Ainda não testado, risco de integrar código não maduro; requer tempo de avaliação |
| **Construir UI do zero sem aproveitar nada** | Total liberdade de design | Duplicação de esforço, perda de componentes já existentes no Cockpit |

## Critérios para mudar a decisão para Accepted

- Aprovação do ADR por pelo menos dois engenheiros senior.
- Prototipagem de tela mínima (Dashboard + Runs) concluída e revisada.
- Não há impedimentos de segurança (ex.: secrets expostos) ao integrar Cockpit com Hermes.
- Plano de implementação (roadmap) aprovado e priorizado nas próximas sprints.
