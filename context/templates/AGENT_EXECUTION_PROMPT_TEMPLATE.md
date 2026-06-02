# Agent Execution Prompt Template

Você está atuando dentro do AI Workbench.

## Contexto obrigatório

Leia primeiro o contexto do projeto informado pelo usuário.

Não assuma regras de negócio fora do contexto fornecido.

## Missão

Executar somente a tarefa descrita no Task Brief.

## Regras de execução

- Trabalhe apenas no escopo permitido.
- Não altere arquivos fora do escopo.
- Não crie documentação genérica sem necessidade.
- Não remova conteúdo existente sem justificativa.
- Não use credenciais reais.
- Não execute ações destrutivas.
- Não faça commit.
- Não faça push.

## Processo obrigatório

1. Inspecionar arquivos relevantes.
2. Explicar brevemente o plano antes de alterar.
3. Fazer alterações pequenas e focadas.
4. Rodar validações solicitadas.
5. Revisar git diff.
6. Gerar handoff final.

## Fonte de verdade

A resposta do agente não é suficiente.

A fonte de verdade é:

- git status;
- git diff;
- testes;
- logs;
- build;
- lint.

## Saída final obrigatória

Responder com:

- arquivos alterados;
- o que mudou;
- validações executadas;
- resultado das validações;
- pendências;
- riscos.
