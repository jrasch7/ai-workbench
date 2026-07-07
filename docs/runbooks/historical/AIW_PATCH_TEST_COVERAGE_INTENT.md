# AIW Patch Test Coverage Intent

## Resultado

O Patch Test Coverage Intent analisa heuristicamente os arquivos modificados por um patch para determinar a "intenção" de cobertura de testes. O sistema avisa o usuário (no Cockpit e no Review Gate) caso um patch altere arquivos de código, mas não altere arquivos de teste (reduzindo a pontuação no Review Gate).

## Classificação

As possíveis classificações são:
- `code_with_tests`: O patch altera código-fonte e também inclui alterações em arquivos de teste.
- `code_without_tests`: O patch altera código-fonte mas não toca em nenhum arquivo de teste.
- `docs_only`: O patch altera exclusivamente arquivos de documentação (.md, README.md, ou em `docs/`).
- `tests_only`: O patch altera exclusivamente arquivos de teste.
- `config_only`: O patch altera apenas arquivos de configuração (.json, .yaml, Dockerfile, etc).
- `mixed`: O patch altera múltiplos tipos (ex: documentação + código), onde a severidade segue a regra do código.

## Integração com Review Gate

O Test Coverage Intent é automaticamente analisado pelo Patch Review Gate (check #5) antes do apply de qualquer patch.
- Ele envia um novo check chamado "Test coverage intent".
- Status pode ser: `passed` (tem testes, é docs-only), `warning` (código sem teste) ou `info` (só config, só testes).
- O sumário do gate é expandido e inclui se faltou testes na versão.

## Score

A pontuação (Readiness Score) do Gate é ajustada pela intenção de testes:
- `code_with_tests`: +5 bônus.
- `code_without_tests`: -10 penalidade (não bloqueia).
- `tests_only`: +3 bônus.
- `config_only`: -5 penalidade.
- `mixed`: depende da ausência de testes (pode ser penalizado).
- `docs_only`: mantém sua lógica atual fixa.

## Cockpit

No Cockpit, o Review Gate agora expande uma nova seção de "Cobertura/Test Intent":
- Lista as categorias de classificação.
- Mostra a severidade.
- Detalha quais arquivos de código e quais arquivos de teste foram reconhecidos.
- Dá recomendações explícitas.
No cabeçalho do patch, foi introduzida uma tag extra visualizando imediatamente a relação (ex: "Code + tests", "Docs only").

## Segurança

- Não lê `.env`.
- Não executa testes (apenas inferência via nome dos arquivos).
- Não calcula coverage real (sem instrumentação na runtime).
- Não bloqueia apply por warning nesta versão (a decisão é informativa, via penalidade de score).
- Sem shell livre.

## Limitações

- Heurística baseada em nome/caminho: Se um projeto não usar os padrões comuns de nomenclatura (ex: `test_*.py`, `*.spec.ts`), a heurística pode falhar e penalizar patches válidos.
- Sem coverage report real: Não verifica se a linha alterada foi coberta.
- Sem mutation testing: Não avalia a eficácia dos testes contra o patch.
- Sem análise semântica profunda: Não sabe se a alteração de um teste foi só um typo ou um assert válido.

## Próximo passo recomendado

Implementar a análise de coverage real e/ou mutation testing. Ao invés de inferir a presença de testes via nomes, integrar um `pytest --cov` (ou análogo) sobre os arquivos modificados para comprovar tecnicamente a proteção.

Veja também o [Coverage Report Adapter](AIW_COVERAGE_REPORT_ADAPTER.md).
