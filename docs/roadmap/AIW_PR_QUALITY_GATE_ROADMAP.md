# AIW PR Quality Gate Roadmap

## Fase 0 — Documentação (concluída)

- Criar docs de arquitetura, ADR e runbook.
- Definir métricas oficiais.
- Publicar hard blockers.

## Fase 1 — Checklist manual

- Validator usa a régua em PRs docs/code pequenos.
- Checklist impresso em cada PR review.
- Aprendizado de padrões recorrentes.

## Fase 2 — Script local

- Criar `scripts/aiw-pr-summary`.
- Gerar Markdown e JSON.
- Coletar `diff`, `stat`, `check` automaticamente.
- Score manual inserido pelo Validator.

## Fase 3 — Integração com agentes

- Executor gera sumário automático.
- Validator revisa score e blockers.
- Integrator bloqueia merge se houver hard blocker.

## Fase 4 — Cockpit/CI

- Exibir Quality Gate no cockpit.
- Opcionalmente rodar em CI.
- Manter histórico de qualidade por projeto.

## Próximos passos imediatos

- Validar checklist manual em PRs reais.
- Coletar feedback de Validator/Integrator.