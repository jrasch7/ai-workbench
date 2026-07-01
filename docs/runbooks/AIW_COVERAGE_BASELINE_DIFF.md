# AIW Coverage Baseline and Diff

## Resultado

A funcionalidade de Coverage Baseline e Diff introduz a habilidade de comparar a cobertura de código de um Patch Preview (através do seu test-run) contra uma versão estável "promovida" do workspace, calculando Deltas por arquivo e gerais.

## Baseline

Uma Coverage Baseline é um "snapshot de confiança" contendo os resultados de cobertura de teste que consideramos ideais num dado momento. A baseline é armazenada localmente em `.aiw/workspaces/<workspace_id>/coverage-baselines/`. O AIW guarda o arquivo de ponteiro `current.json` e o histórico de cada baseline gerada.

## Promoção manual

O AIW **NÃO** roda coverage e nem troca branch automaticamente. Toda promoção de Baseline é estritamente manual:
1. O usuário executa um test-run que produz um `coverage-summary.json`.
2. O usuário clica em "Promover este coverage como baseline" na interface do Cockpit (ou via chamada na API de promote).
3. Essa ação congela os métricas daquele test-run num `baseline_id` rastreável.

## Coverage Diff

Sempre que o Patch Review Gate (ou o detalhe do Test Run) é avaliado, se o test-run possuir métricas capturadas e o workspace já possuir uma Baseline estabelecida, um Diff é gerado.

O status da comparação pode ser:
- `improved` (Delta > +1%)
- `regressed` (Delta < -1%)
- `unchanged` (Entre -1% e +1%)
- `no_baseline` (Sem baseline no workspace)
- `no_current_coverage` (Test-run analisado não extraiu métricas novas)

## Integração com Patch Review Gate

O Patch Review Gate agora expõe esse comparativo nativamente no Check "Coverage diff vs baseline". Uma regressão resulta num _score penalty_ (-10) e alerta, mas na versão atual (v1) não bloqueia imperativamente o _Apply_ de forma sozinha, atuando como um "warning forte".

## Cockpit

- O detalhe visual de um **Test Run** mostra o comparativo arquivo a arquivo.
- O detalhe visual de um **Patch Review Gate** alerta na cor amarela regressões contra Baseline.
- O card do **Workspace** apresenta o status e taxa-médias da Baseline viva atual.

## Segurança

- Não executa coverage automaticamente;
- Não troca branch;
- Não instala dependências extras na base;
- Só usa `coverage-summary.json` preexistentes já formatados, blindando contra command-injection;
- Sem shell livre;
- Sem leitura de `.env`.

## Limitações

- Baseline é local à máquina/workspace.
- A comparação de arquivos e paths é puramente heurística baseada nos keys reportados.
- Não detalha regressão de linhas precisas (sem Source-Code Diff real nas linhas tocadas).
- Não há Mutation Testing acoplado nesta v1.

## Próximo passo recomendado

Expandir o Diff para um mapeamento Source-Code, lincando arquivos analisados do coverage diretamente nas linhas que o `git diff` tocou dentro da _PR_.

Integra com o [Changed Lines Coverage](AIW_CHANGED_LINES_COVERAGE.md).
