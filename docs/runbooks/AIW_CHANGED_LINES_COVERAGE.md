# AIW Changed Lines Coverage

## Resultado

A funcionalidade de Changed Lines Coverage introduz a habilidade de analisar apenas o subconjunto de linhas que um Patch efetivamente modificou, cruzando com os relatórios de coverage gerados pelas execuções de testes. O objetivo é responder: "O código novo escrito pelo Agent está coberto por testes?"

## Changed lines

As linhas alteradas são extraídas dinamicamente dos artefatos de Patch Preview do AIW, parseando o `diff` em formato unified que a ferramenta `project_patch_preview` produz. São consideradas `added_lines` as linhas precedidas por `+` na deleção original do código, permitindo traçar onde exatamente a mudança residiu.

## Line-level coverage

Quando suportado (ex. formatos Cobertura XML e LCOV), o parser do AIW extrai a lista exata de linhas `covered` (hits > 0) e `missed` (hits == 0) de cada arquivo. 
Ao batermos a lista `added_lines` do patch contra essas duas categorias, conseguimos dizer não apenas a porcentagem média daquele arquivo, mas sim *exatamente quais das novas linhas não foram visitadas pelos testes*.

## Integração com Patch Review Gate

O Patch Review Gate agora inclui o Check `Changed lines coverage`.
Ele age de forma análoga a um Codecov de PR:
- `covered`: +8 pontos (linhas atingiram o threshold ou 100%).
- `partial`: -8 pontos (alguma linha nova foi coberta, mas outras ficaram de fora).
- `uncovered`: -15 pontos (nenhuma das linhas novas foi coberta).
- `no_line_data`: -3 pontos (caso o relatório usado de fallback não proveja dados granulares por linha).

## Cockpit

Na tela inicial do Cockpit, quando se clica no detalhe de um Patch em Review, o bloco `Changed Lines Coverage` surge detalhando cada arquivo que restou com linhas descobertas, listando inclusive o número da linha.

## Segurança

- Não executa coverage automaticamente;
- Não troca branch;
- Não instala dependências;
- Só usa artifacts locais;
- Sem shell livre;
- Sem leitura de `.env`.

## Limitações

- Parser de diff é simples e heurístico, conta estritamente com base nos headers do `@@`.
- Depende da qualidade do relatório gerado. Se o builder não soltar `<line>` tags, não teremos cruzamento.
- Sem mutation testing. O fato de passar na linha não significa asserção forte.
- Sem análise semântica profunda (ignora se a linha é um simples '}' ou uma instrução complexa).

## Próximo passo recomendado

Investigar Mutation Testing no nível de diff lines, injetando breaks intencionais apenas nas linhas identificadas pelo diff para medir robustness real do Coverage.
