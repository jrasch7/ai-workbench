# ADR-001: AIW PR Quality Metrics

## Status

Proposto → Aceito (2026-06-25)

## Contexto

O AI Workbench opera com agentes (Executor, Validator, Integrator) que precisam avaliar mudanças de forma objetiva antes do merge. Atualmente não há régua de qualidade padronizada.

## Decisão

O AIW adotará Quality Gate por PR com métricas oficiais iniciais:

1. **Maintainability** — Facilidade de manter e evoluir código.
2. **Readability** — Clareza e intenção explícita.
3. **Reliability** — Previsibilidade e tratamento de erro.
4. **Testability** — Cobertura e isolamento de testes.
5. **Efficiency** — Uso razoável de recursos.

O gate começa como documentação/checklist. Evolui para script. Depois para automação opcional no cockpit/agente.

## Escopo

- Métricas começam como avaliação humana guiada.
- Agentes devem entregar evidência concreta, não opinião solta.
- Avaliação humana ainda é necessária para mudanças críticas.

## Mecanismo

1. Fase 0: Documentação criada (este ADR).
2. Fase 1: Checklist manual usado por Validator.
3. Fase 2: Script `aiw-pr-summary` implementado.
4. Fase 3: Integração com agentes automatizados.
5. Fase 4: Exibição no Cockpit/CI.

## Consequências

- Aprovação recomendada requer score mínimo 3 em todas as métricas.
- Hard blockers implicam bloqueio automático.
- A régua pode ser refinada conforme práticas evoluem.