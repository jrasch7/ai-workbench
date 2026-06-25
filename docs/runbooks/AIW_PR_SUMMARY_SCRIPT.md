# AIW PR Summary Script — Runbook

## Purpose

Documenta o contrato futuro do script `scripts/aiw-pr-summary` que gerará sumários de PR com base no Quality Gate.

## Contrato do script (não implementado)

```
scripts/aiw-pr-summary [opções]
```

## Saída padrão (Markdown)

```markdown
# PR Summary

## 1. Objetivo
[Descrição curta da tarefa]

## 2. Arquivos alterados
[Lista de arquivos modificados]

## 3. Mudanças principais
[Resumo técnico das alterações]

## 4. Testes e validações
- [ ] Testes executados
- [ ] Lint/typecheck
- [ ] Build

## 5. Quality Gate

| Métrica | Score | Evidência | Observações |
| --- | ---: | --- | --- |
| Maintainability |  |  |  |
| Readability |  |  |  |
| Reliability |  |  |  |
| Testability |  |  |  |
| Efficiency |  |  |  |

## 6. Hard blockers
[Lista vazia se não houver]

## 7. Riscos
[Lista de riscos conhecidos]

## 8. Recomendação
APPROVE / REQUEST_CHANGES / NEEDS_HUMAN_REVIEW
```

## Parâmetros futuros

```bash
scripts/aiw-pr-summary --base origin/main --format markdown
scripts/aiw-pr-summary --base origin/main --json
scripts/aiw-pr-summary --base origin/main --output reports/pr-summary.md
```

## Comandos a coletar

```bash
git status --short
git diff --check
git diff --stat
git diff --name-only
git diff
```

## Proibições

- NÃO enviar dados sensíveis para modelo externo sem redaction.
- NÃO analisar arquivos `.env`.
- NÃO incluir secrets no resumo.
- NÃO mascarar falhas.
- NÃO aprovar PR automaticamente.

## Integração futura

- O script será chamado pelo Validator antes do PR.
- O Integrador usará a saída para decisão de merge.
- O Cockpit exibirá o Quality Gate visualmente.