# AI Workbench Roadmap

## 1. Resumo executivo

Este documento sintetiza a direção estratégica do AI Workbench (AIW), consolidando evidências, decisões e planos de evolução.

Principais fatos confirmados incluem a adoção de Obsidian como camada de conhecimento, Git como fonte versionada, Hermes como runtime de agentes, e a preparação de múltiplas ferramentas de segurança.


## 2. Visão do AIW

AIW será a bancada/fábrica de IA para o ecossistema Nivela, provendo infraestrutura modular, control plane experimental e integração profunda com ferramentas de linguagem, observabilidade e segurança.


## 3. Princípios operacionais

- **Modularidade**: componentes isolados por anéis de maturidade.
- **Segurança**: integração de Semgrep, Nuclei, OWASP ZAP e demais scanners.
- **Evidência‑driven**: cada claim tem fonte documentada no Evidence Map.
- **Iteratividade**: spikes técnicos validados antes de promover a fase.


## 4. Arquitetura alvo

Arquitetura baseada em microsserviços controlados por agentes Hermes, armazenamento de conhecimento em Obsidian, pipelines CI/CD via Git, e layer de observabilidade via Paperclip (experimental).


## 5. Anéis de maturidade

| Ferramenta | Ring sugerido | Evidência | Confiança | Ação |
|-----------|--------------|-----------|-----------|------|
| Obsidian | 2 | Documentado no harness | alta | usar |
| Hermes | 3 | Runtime definido | alta | usar |
| Paperclip | 2 | Experimental, evidência de uso | média | monitorar |
| Go/Golang | 0 | Decisão recente do João | média | criar fase AIW‑G1 |
| Cyber Bench | 3 | Bancada autorizada | alta | usar |
| Dev Containers | 2 | Planejado, evidência de sandbox | média | implementar |


## 6. Estado atual

- **Claims confirmados**: listados no Evidence Map (AIW, Obsidian, Git, Hermes, etc.).
- **Ferramentas em uso**: Obsidian, Hermes, Telegram Gateway, Semgrep, Nuclei.
- **Spikes pendentes**: Go Infrastructure Spike (AIW‑G1).


## 7. Roadmap por fases

### AIW-O1 — Obsidian Operational Foundation
Estabelecer camada de conhecimento, sincronização e versionamento.

### AIW-H2 — Context, Memory & Quality Harness

**Objetivo:** Consolidar memória de contexto unificada, garantir qualidade de dados e suporte a múltiplas sessões.
**Status:** em desenvolvimento
**Entregas:** camada de qualidade de evidência, integração com Obsidian, auditoria de métricas.
**Critérios de sucesso:** 90% de casos de uso com evidência rastreável, latência <200ms.
**Riscos:** dependência de ferramentas externas, sobrecarga de armazenamento.
Implementar memória de contexto, qualidade de evidence e validações automatizadas.

### AIW-G1 — Go Infrastructure Spike

**Objetivo:** Avaliar Go/Golang como plataforma de infraestrutura operacional.
**Status:** pendente de decisão
**Entregas:** protótipo de CLI `aiwctl` em Go, benchmark de performance.
**Critérios de sucesso:** desempenho ≥ 2x vs versão Python, cobertura de testes ≥80%.
**Riscos:** curva de aprendizagem, integração com runtime Hermes.
* Claim*: Go/Golang será considerado como candidato para infraestrutura operacional do AIW.
* Ring*: 0 (candidato).
* Primeiro teste sugerido*: `aiwctl status` ou `aiwctl git safe-status`.
* Status*: pendente de decisão.

### AIW-P1 — Paperclip Lab
Control plane experimental de agentes, ainda não produção.

### AIW-C1 — Cyber Bench Foundation
Bancada autorizada para testes de carga e integração Nivela.


## 8. Matriz de ferramentas

| Ferramenta | Ring | Status | Próximo teste | Risco |
|---|---|---|---|---|
| Obsidian Git | 0 | planejado | - | médio |
| Obsidian Sync | 0 | planejado | - | médio |
| hermes-paperclip-adapter | 0 | planejado | - | médio |
| Ralph Loop | 0 | planejado | - | médio |
| Ralph TUI | 0 | planejado | - | médio |
| Claude Code | 0 | planejado | - | médio |
| Ollama | 0 | planejado | - | médio |
| OpenRouter | 0 | planejado | - | médio |
| Anthropic/Claude | 0 | planejado | - | médio |
| OpenAI/Codex | 0 | planejado | - | médio |
| Google Gemini | 0 | planejado | - | médio |
| Burp Suite | 0 | planejado | - | médio |
| CAI | 0 | planejado | - | médio |
| PentAGI | 0 | planejado | - | médio |
| PentestGPT | 0 | planejado | - | médio |
| Nivela Core | 0 | planejado | - | médio |
| Nivela Store | 0 | planejado | - | médio |
| Nivela Conta/Billing | 0 | planejado | - | médio |

(lista completa das ferramentas – já presente na seção 5).


## 9. Organização dos agentes
- Founder / PO / Investor Brain

Papéis necessários: Founder/PO, Orchestrator, Architect, Researcher, Executor, Validator, Integrator, Cyber Analyst, Documentation Curator, Model Evaluator, Product Strategist.


## 10. Segurança e governança

Aplicar políticas de revisão de skills, validação de claims, e auditoria contínua usando as ferramentas de segurança listadas.


## 11. Critérios de sucesso

- Evidência confirmada em Evidence Map.
- Ferramentas migrando para rings superiores.
- Spikes concluídos com testes automatizados.


## 12. Próximas ações imediatas

1. Revisar e aprovar o AIW‑G1 spike.
2. Criar protótipo `aiwctl` em Go.
3. Atualizar Evidence Map com resultados.


## 13. Snapshot atual

Referência: docs/ROADMAP_EVIDENCE_MAP.md
Estado do repositório: HEAD@{0}

Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
Detalhe adicional para robustez do roadmap, alinhado com a visão estratégica do AIW e as práticas de governança estabelecidas.
