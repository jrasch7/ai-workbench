# Git Safe Workflow

Use esta skill sempre que uma tarefa envolver leitura, alteracao, validacao, commit, push, branch, PR ou revisao de diff em um repositorio Git.

## Objetivo

Garantir que o agente trabalhe com Git de forma segura, rastreavel e revisavel.

## Regra central

Nunca trate alteracoes em repositorio como simples edicao de arquivo.

Toda alteracao em repo deve passar por:

1. estado inicial;
2. escopo permitido;
3. alteracao minima;
4. validacao;
5. diff;
6. reporte;
7. autorizacao explicita antes de commit/push.

## Fluxo obrigatorio

Antes de alterar arquivos:

```bash
git status --short
```

Depois, confirme ou declare:

- escopo permitido;
- arquivos que pretende alterar;
- arquivos que nao devem ser alterados;
- riscos conhecidos.

Durante a alteracao:

- altere somente arquivos no escopo;
- prefira a menor mudanca possivel;
- nao misture assuntos diferentes;
- nao altere `.env`, secrets, tokens, credenciais ou arquivos sensiveis.

Depois da alteracao:

```bash
git status --short
```

```bash
git diff --stat
```

Revise o diff dos arquivos alterados.

## Commit e push

Nunca faça commit sem autorizacao explicita do usuario.

Nunca faça push sem autorizacao explicita do usuario.

Quando o usuario autorizar commit, antes rode:

```bash
git status --short
```

```bash
git diff --stat
```

Quando o usuario autorizar push, confirme antes:

- branch atual;
- remote;
- ultimo commit;
- se ha secrets no diff;
- se testes/validacoes foram executados.

## Comandos proibidos sem autorizacao explicita

- `git reset --hard`
- `git clean -fd`
- `git push --force`
- `rm -rf`
- qualquer comando com `sudo`
- qualquer alteracao em `.env` ou arquivos de credenciais

## Reporte final

Ao final, reporte:

- arquivos alterados;
- resumo da mudanca;
- comandos de validacao executados;
- resultado de `git status --short`;
- resultado de `git diff --stat`;
- riscos ou pendencias;
- se houve commit;
- se houve push.
