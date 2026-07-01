# AIW Patch Review Gate

## Resultado

O Patch Review Gate atua como uma barreira de segurança operacional antes do `apply` de qualquer patch sugerido pela AI. Ele avalia o status dos arquivos modificados, os testes requeridos (Validation Plan) e o histórico de execuções para determinar se o patch está seguro para ser aplicado.

## Readiness status

O status do Gate pode ser um dos seguintes:
- `ready`: Todos os comandos obrigatórios do plano de validação passaram. Sem regressões detectadas.
- `needs_validation`: Faltam testes obrigatórios, ou o plano de validação ainda não foi executado.
- `failed`: Pelo menos um comando obrigatório falhou.
- `regressed`: Uma regressão foi detectada (ex: um comando que passava no snapshot anterior, agora falha).
- `partial`: Alguns comandos foram executados, mas faltam outros para cobrir o plano.
- `docs_only`: Patch altera apenas arquivos de documentação (Markdown), não exigindo validação técnica severa.
- `applied`: O patch já foi aplicado.
- `rolled_back`: O patch foi revertido (rollback).
- `unknown`: Status desconhecido ou falha na leitura.

## Checklist

O Checklist avalia:
1. **Patch metadata**: Verifica se o artefato do patch existe e possui `changed_files`.
2. **Validation plan**: Verifica se o plano de validação existe e define comandos aplicáveis.
3. **Required commands**: Verifica se todos os comandos listados no plano foram executados com sucesso (sem falhas ou pendências).
4. **Regression check**: Garante que os testes executados não apresentaram regressão de status ou piora severa de performance comparado ao snapshot base.

## Readiness score

A pontuação de "Readiness" reflete quão maduro e seguro está o patch:
- +20 pontos por Metadata válida.
- +20 pontos por Plano de Validação criado.
- +20 pontos se todos os comandos foram executados.
- +25 pontos se não houver falhas.
- +15 pontos se não houver regressões.
Total: 100 pontos para um patch perfeito.
Patches `docs_only` recebem 70 pontos diretos.
Score máximo de 40 para falhas e 35 para regressões.

## Apply reviewed

Para aplicar o patch validado, utilize o endpoint `POST /api/workspaces/<workspace_id>/patches/<patch_id>/apply-reviewed`.
- Requer confirmação explícita no payload (`confirm: true`).
- Bloqueia automaticamente qualquer patch que não possua status `ready` ou `docs_only`.
- O apply é delegado ao sistema de `project_patch_apply` nativo, garantindo total segurança (nenhum script shell livre, nenhum git push, nenhum vazamento de .env).

## Integração com Validation Plan Snapshots

O Gate extrai todas as suas métricas de execução a partir dos **Validation Plan Snapshots**. Um snapshot contém a foto exata do plano gerado e de todas as execuções e comparações (`executions.json`, `comparison.json`). O Review Gate simplesmente consolida esses artefatos numa métrica binária (aprova / reprova).

## Cockpit

No painel (Bancada) do AIW Cockpit:
- O Review Gate possui uma seção própria detalhada logo abaixo do diff unificado.
- Exibe o status consolidado, a pontuação e os checkboxes (passed/failed) de cada item do checklist.
- O botão de "Aplicar" antigo foi substituído por uma versão integrada ao Gate, impedindo o apply de patches incompletos (`needs_validation`, `failed`, `partial`, `regressed`).

## Segurança

- sem auto-apply;
- apply exige confirmação;
- sem commit;
- sem push;
- sem shell livre;
- sem leitura de .env.

## Limitações

- score heurístico;
- sem override manual avançado (não é possível forçar o apply de patches quebrados, pelo menos não nesta v1);
- docs-only ainda exige confirmação (a v1 não tem auto-apply, nem para docs);
- apply reviewed usa o patch flow existente;

## Validações executadas

- Testes de parser (syntax error);
- Testes de validações via pytest, mocha, bash -n;
- Smokes manuais.

## Próximo passo recomendado

Expandir a heurística de score para verificar cobertura de mutação de testes (verificando se o patch não quebrou testes intencionalmente).

## Test Coverage Intent

O [Patch Test Coverage Intent](AIW_PATCH_TEST_COVERAGE_INTENT.md) penaliza ou bonifica o Readiness Score.

## Coverage Report

O gate avalia pontuações reais com base no [Coverage Report Adapter](AIW_COVERAGE_REPORT_ADAPTER.md).

Também pode verificar dados do [Coverage Run Capture](AIW_COVERAGE_RUN_CAPTURE.md).

Inclui check nativo do [Coverage Baseline and Diff](AIW_COVERAGE_BASELINE_DIFF.md).

Inclui check nativo do [Changed Lines Coverage](AIW_CHANGED_LINES_COVERAGE.md).
