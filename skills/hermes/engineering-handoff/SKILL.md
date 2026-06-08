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

## Hermes Operational Reliability Protocol

1. **Sem evidência, não aconteceu.** O agente não pode afirmar que executou, validou ou concluiu sem saída real, status real ou evidência objetiva.
2. **Estado final obrigatório.** O handoff deve começar com exatamente um dos seguintes estados finais:
   - `DONE`
   - `NEEDS_REVIEW`
   - `BLOCKED`
   - `NO_CHANGES`
3. **Critério para DONE.** `DONE` só pode ser usado quando o escopo foi concluído e todas as validações obrigatórias passaram sem falhas.
4. **Validações falhas.** Se qualquer validação falhar, o status final não pode ser `DONE`.
5. **Uso de BLOCKED.** `BLOCKED` deve ser usado quando:
   - `git diff --check` falhar;
   - o *grep* obrigatório não encontrar os termos especificados;
   - o arquivo solicitado estiver ausente;
   - um comando não for executado;
   - uma ferramenta falhar;
   - ocorrer erro em `read_file` ou `write_file`;
   - ocorrer `repeated_exact_fail`.
6. **Conteúdo do handoff final.** O handoff deve conter:
   - status final;
   - resumo da mudança;
   - escopo solicitado;
   - arquivos criados/alterados;
   - comandos executados;
   - saídas reais;
   - validações realizadas e seus resultados;
   - riscos identificados;
   - pendências restantes;
   - `git status --short` final;
   - se `commit`/`push` foi feito ou não;
   - próximo passo recomendado.
7. **Progress updates.** Para tarefas longas, usar atualizações de progresso exatamente como:
   - `PROGRESS 1/N` — Iniciando tarefa e confirmando escopo.
   - `PROGRESS 2/N` — Diretório e Git verificados.
   - `PROGRESS 3/N` — Arquivos inspecionados.
   - `PROGRESS 4/N` — Alterações aplicadas.
   - `PROGRESS 5/N` — Revisando diff/status.
   - `PROGRESS 6/N` — Rodando validações.
   - `PROGRESS 7/N` — Preparando handoff final.
   - **Typing não conta** como progress update.
8. **Regras adicionais.**
   - `git diff --stat` não mostra arquivos *untracked*.
   - Para arquivos novos, usar `git status --short`, confirmar existência com `test -f` ou `ls`, e usar `git add -N` quando necessário.
   - Não declarar `commit` ou `push` sem evidência real.
   - Incluir termos `read_file`, `write_file` e `repeated_exact_fail` nas validações conforme necessário.


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
