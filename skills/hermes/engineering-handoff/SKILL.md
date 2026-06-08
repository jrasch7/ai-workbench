# Engineering Handoff

Use esta skill ao finalizar qualquer tarefa de engenharia, documentacao, validacao, refactor, correcao, investigacao ou alteracao em repositorio.

## Objetivo

Produzir um handoff final claro, auditavel e util para o usuario revisar a entrega sem precisar reconstituir tudo pelo terminal.

## Regra central

Nunca finalize uma tarefa apenas dizendo que deu certo.

Sempre reporte evidencias.

## Formato obrigatorio

Ao final da tarefa, responda com as secoes abaixo.

### Resumo

Explique em poucas linhas o que foi feito.

### Arquivos alterados

Liste cada arquivo alterado, criado ou removido.

Se nenhum arquivo foi alterado, declare explicitamente.

### Validacoes executadas

Liste comandos executados e resultados observados.

Exemplos:

```bash
git status --short
```

```bash
git diff --stat
```

```bash
pytest
```

Nunca invente validacoes.

Se algo nao foi validado, diga que nao foi validado.

### Diff / escopo

Informe se o diff ficou restrito ao escopo combinado.

Se houve arquivo fora do escopo, pare e reporte como risco.

### Riscos

Liste riscos tecnicos, funcionais, de seguranca, de regressao ou operacionais.

Se nao houver risco conhecido, escreva: Nenhum risco conhecido alem do escopo validado.

### Pendencias

Liste o que ainda falta fazer.

Se nao houver pendencia conhecida, escreva: Nenhuma pendencia conhecida.

### Git

Informe:

- branch atual, se verificada;
- `git status --short` final;
- se houve commit;
- se houve push;
- hash do commit, se houver.

## Regras de honestidade

- Nao declare sucesso sem evidencia.
- Nao omita erro.
- Nao diga que testes passaram se eles nao foram executados.
- Nao diga que o Git esta limpo sem rodar `git status --short`.
- Nao diga que push foi feito sem evidencia.

## Quando pedir autorizacao

Antes de commit ou push, peca autorizacao explicita do usuario, salvo se a tarefa atual ja autorizou expressamente commit/push apos validacao.

## Handoff minimo aceitavel

Se a tarefa foi pequena, ainda assim entregue no minimo:

- resumo;
- arquivos alterados;
- validacoes;
- git status final;
- pendencias.
