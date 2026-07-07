# ROADMAP Evidence Map

## 1. Objetivo
Este arquivo é a etapa obrigatória anterior à recriação do `ROADMAP.md`.

## 2. Fontes consultadas
| Fonte | Papel | Observação |
|-------|-------|------------|
| README.md | Visão geral do AIW | Contém links para documentos principais |
| docs/HERMES_CONTEXT_QUALITY_HARNESS.md | Protocolo de evidência | Define a necessidade de Evidence Map antes de Roadmap |
| docs/HERMES_SELF_IMPROVEMENT_GOVERNANCE.md | Governança de auto‑melhoria | Regras sobre promoção de skills |
| docs/HERMES_SKILL_PROMOTION_WORKFLOW.md | Fluxo de promoção de skills | Detalha revisão humana |
| docs/HERMES_OPERATIONAL_RELIABILITY.md | Operacional reliability | Guia de validações e guardrails |
| skills/hermes/telegram-smoke-tests/SKILL.md | Skill de smoke test | Confirma funcionamento do gateway Telegram |
| skills/hermes/git-safe-workflow/SKILL.md | Skill de workflow Git seguro | Define regras de commit e push |
| docs/obsidian/ | Camada de conhecimento Obsidian | Arquivos de vault e templates |

## 3. Claims confirmados
| Claim | Fonte | Evidência | Status | Ação |
|-------|-------|-----------|--------|------|
| AIW é bancada/fábrica de IA do ecossistema Nivela | README.md | Descrição do projeto | confirmado | incluir no roadmap |
| AIW não é produto comercial imediato | README.md | Escopo do AIW | confirmado | incluir |
| Obsidian como camada de conhecimento | docs/HERMES_CONTEXT_QUALITY_HARNESS.md | Requisitos de Knowledge Layer | confirmado | incluir |
| Git como fonte versionada | docs/HERMES_CONTEXT_QUALITY_HARNESS.md | Hierarquia de verdade | confirmado | incluir |
| Hermes como runtime de agentes | docs/HERMES_CONTEXT_QUALITY_HARNESS.md | Protocolo de operação | confirmado | incluir |
| self‑improvement permitido | docs/HERMES_SELF_IMPROVEMENT_GOVERNANCE.md | Regras de criação de skills | confirmado | incluir |
| promoção silenciosa de skills proibida | docs/HERMES_SELF_IMPROVEMENT_GOVERNANCE.md | Regra explícita | confirmado | incluir |
| skills locais são drafts até revisão | docs/HERMES_SELF_IMPROVEMENT_GOVERNANCE.md | Regra de revisão | confirmado | incluir |
| Telegram Gateway já testado/smoke | skills/hermes/telegram-smoke-tests/SKILL.md | Smoke test aprovado | confirmado | incluir |
| Obsidian smoke validado | docs/HERMES_CONTEXT_QUALITY_HARNESS.md | Evidência de smoke | confirmado | incluir |
| scripts de sync do Obsidian existentes | docs/HERMES_CONTEXT_QUALITY_HARNESS.md | Listados como ferramentas | confirmado | incluir |
| Cyber Bench como bancada autorizada e planejada | docs/HERMES_CONTEXT_QUALITY_HARNESS.md | Mencionado como ferramenta | confirmado | incluir |
| Ollama/modelos locais como laboratório planejado | docs/HERMES_CONTEXT_QUALITY_HARNESS.md | Ring 2 sugestão | confirmado | incluir |
| Paperclip como control plane experimental de agentes | docs/HERMES_CONTEXT_QUALITY_HARNESS.md | Listado em matriz | confirmado | incluir |
| hermes-paperclip-adapter | docs/HERMES_CONTEXT_QUALITY_HARNESS.md | (nenhuma evidência encontrada) | sem evidência | pendente |
| Ralph como harness por PRD | docs/HERMES_CONTEXT_QUALITY_HARNESS.md | Mencionado | confirmado | incluir |
| Ralph TUI | docs/HERMES_CONTEXT_QUALITY_HARNESS.md | (nenhuma evidência encontrada) | sem evidência | pendente |
| Dev Containers como sandbox planejado | docs/HERMES_CONTEXT_QUALITY_HARNESS.md | Ring 2 | confirmado | incluir |
| Provedores premium/fallbacks (OpenRouter, Anthropic, OpenAI, Google Gemini) | docs/HERMES_MODEL_MATRIX.md | Listados | confirmado | incluir |
| Ferramentas de segurança (Semgrep, Nuclei, OWASP ZAP, Burp Suite, CAI, PentAGI, PentestGPT) | docs/HERMES_CONTEXT_QUALITY_HARNESS.md | Mencionadas | confirmado | incluir |
| Nivela Core / Store / Conta como ecossistema alvo | README.md | Referências ao ecossistema | confirmado | incluir |

## 4. Claims conflitantes ou conflitantes
nenhum conflito encontrado

## 5. Claims sem evidência suficiente
| Claim | Motivo | Ação |
|-------|--------|------|
| IA completa pronta para produção | Falta teste de carga | solicitar teste de carga |
| Integração automática de skills ao Obsidian | Não há automação implementada | planejar automação |

## 6. Rings sugeridos para matriz de ferramentas
| Ferramenta | Ring sugerido | Evidência | Confiança | Ação |
|-----------|--------------|-----------|----------|------|
| Obsidian | 2 | Documentado no harness | alta | usar |
| Obsidian Git | 2 | Referido no harness | alta | usar |
| Obsidian Sync | 2 | Listado como obrigatória | alta | usar |
| Hermes | 3 | Runtime definido | alta | usar |
| Telegram Gateway | 3 | Smoke test OK | alta | usar |
| Paperclip | 2 | Experimental, evidência de uso | média | monitorar |
| hermes-paperclip-adapter | docs/HERMES_CONTEXT_QUALITY_HARNESS.md | (nenhuma evidência encontrada) | sem evidência | pendente |
| Ralph Loop | 2 | PRD mencionado | média | validar |
| hermes-paperclip-adapter | 0 | (nenhuma evidência) | baixa | pendente |
| Ralph TUI | 0 | (nenhuma evidência) | baixa | pendente |
| Dev Containers | 2 | Planejado, evidência de sandbox | média | implementar |
| Claude Code | 3 | Disponível, ainda não testado | baixa | testar |
| Ollama | 2 | Laboratório planejado | média | provisionar |
| OpenRouter | 3 | Fallback premium | alta | usar |
| Anthropic/Claude | 3 | Fallback premium | alta | usar |
| OpenAI/Codex | 3 | Fallback premium | alta | usar |
| Google Gemini | 3 | Fallback premium | alta | usar |
| Semgrep | 3 | Ferramenta de segurança listada | alta | integrar |
| Nuclei | 3 | Ferramenta de segurança listada | alta | integrar |
| OWASP ZAP | 3 | Ferramenta de segurança listada | alta | integrar |
| Burp Suite | 3 | Ferramenta de segurança listada | alta | integrar |
| CAI | 3 | Ferramenta de segurança listada | alta | integrar |
| PentAGI | 3 | Ferramenta de segurança listada | alta | integrar |
| PentestGPT | 3 | Ferramenta de segurança listada | alta | integrar |
| Cyber Bench | 3 | Bancada autorizada | alta | usar |
| Nivela Core | 3 | Ecossistema alvo | alta | usar |
| Nivela Store | 3 | Ecossistema alvo | alta | usar |
| Nivela Conta/Billing | 3 | Ecossistema alvo | alta | usar |

## 7. Decisões pendentes para João
- Aprovar lista final de ferramentas e seus Rings sugeridos.
- Autorizar inclusão de claims que ainda estão como "sem evidência" após testes adicionais.
- Confirmar se a integração automática de skills ao Obsidian será permitida.
- Validar a necessidade de testes de carga para IA completa em produção.

## 8. Próxima ação segura
Revisar este Evidence Map com João antes de criar o `ROADMAP.md`.

## 9. Addendum — Go/Golang candidate

Claim: Go/Golang será considerado como candidato para infraestrutura operacional do AIW.
Fonte: decisão recente do João nesta sessão.
Evidência: João aprovou considerar Go para CLI, gateway, supervisor, workers, adapters e healthchecks.
Status: pendente de decisão.
Ação: incluir como possível fase AIW-G1 — Go Infrastructure Spike no futuro ROADMAP.md, sem tratar Go como padrão ainda.
Ring sugerido: Ring 0.
Primeiro teste sugerido: aiwctl status ou aiwctl git safe-status.
