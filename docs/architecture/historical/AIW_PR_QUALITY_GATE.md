# AIW PR Quality Gate — Architecture

## Objetivo

O Quality Gate de PRs é um contrato objetivo que permite avaliar a qualidade de mudanças antes do merge, assegurando que código e documentação atendam critérios mínimos de integridade, clareza e rastreabilidade. Ele opera como checklist inicial, evoluindo futuramente para automação.

## Papéis envolvidos

### Executor
- Executa mudanças dentro do escopo da tarefa.
- Garante que diffs sejam coerentes e testáveis.
- Entrega evidência completa (não opinião solta).

### Validator
- Revisa o diff e a execução dos testes.
- Aplica a régua de métricas ao código alterado.
- Identifica hard blockers e warnings.

### Integrator
- Consolida a aprovação do Validator.
- Bloqueia merges com hard blockers.
- Cria commits e PRs com handoff completo.

### Documentation Curator
- Mantém ADRs atualizados.
- Documenta decisões de qualidade.
- Preserva histórico de métricas.

## Quando o gate roda

1. **Antes do commit** — Executor verifica checklist pessoal.
2. **Antes do PR** — Validator aprova ou rejeita mudanças.
3. **Após abrir PR** — Revisão automática ou humana adicional.
4. **Antes do merge** — Integrator confirma aprovação e ausência de blockers.

## Entradas

- `git diff` — Alterações de código.
- `git diff --stat` — Estatísticas de linhas/arquivos.
- `git diff --check` — Erros de whitespace.
- Testes executados — Saída de CI ou local.
- Lint/build/typecheck — Resultado de validações estáticas.
- Arquivos alterados — Lista de paths modificados.
- Descrição da tarefa — Objetivo original da mudança.
- Riscos conhecidos — Lista explícita de preocupações.

## Saídas

- Score por métrica (0-5).
- Hard blockers identificados.
- Warnings coletados.
- Recomendação final.
- Resumo executivo.
- Checklist de validação.

## Métricas principais

| Métrica | Definição |
|---|---|
| **Maintainability** | Facilidade de manter, simplicidade, baixo acoplamento, ausência de duplicação desnecessária. |
| **Readability** | Clareza, nomes explícitos, estrutura lógica, baixo ruído, intenção visível. |
| **Reliability** | Comportamento previsível, tratamento de erro adequado, idempotência, segurança contra regressão. |
| **Testability** | Facilidade de testar, cobertura dos fluxos críticos, isolamento, testes automatizados presentes. |
| **Efficiency** | Uso razoável de recursos, evita N+1, evita chamadas repetidas, complexidade justificada. |

## Escala de pontuação

| Score | Significado |
|---|---|
| 5 | Excelente |
| 4 | Bom |
| 3 | Aceitável |
| 2 | Fraco |
| 1 | Bloqueante ou quase bloqueante |
| 0 | Não avaliável / sem evidência |

## Regra de aprovação inicial

- Nenhuma métrica abaixo de 3.
- Nenhum hard blocker presente.
- Testes relevantes executados ou justificativa clara.
- Diff coerente com escopo da tarefa.
- Documentação atualizada quando necessário.

## Hard blockers

- Syntax error.
- Teste crítico falhando.
- Segredo exposto (API keys, passwords).
- Alteração fora de escopo sem justificativa.
- Remoção de segurança.
- Quebra de contrato público.
- Migração destrutiva sem rollback.
- Código não determinístico em fluxo crítico.
- Bypass de validação/autorização.
- Ausência total de evidência.