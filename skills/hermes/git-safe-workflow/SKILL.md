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

Commit e push sao acoes bloqueadas por padrao.

Nunca faca commit sem autorizacao explicita do usuario na tarefa atual.

Nunca faca push sem autorizacao explicita do usuario na tarefa atual.

Se o usuario pedir commit/push automatico sem revisao de diff, recuse e explique o fluxo seguro.

Ao explicar o fluxo, sempre deixe claro que commit e push so podem ocorrer depois de autorizacao explicita.

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

## Hermes Operational Reliability Protocol

### 1. Progress updates
Para tarefas que envolvam Git, edição de arquivos, validações, inspeção de múltiplos arquivos ou duração provável maior que 60 segundos, envie atualizações de progresso textuais no formato:

* **PROGRESS 1/N** — Iniciando tarefa e confirmando escopo.
* **PROGRESS 2/N** — Diretório e Git verificados.
* **PROGRESS 3/N** — Arquivos inspecionados.
* **PROGRESS 4/N** — Alterações aplicadas.
* **PROGRESS 5/N** — Revisando diff/status.
* **PROGRESS 6/N** — Rodando validações.
* **PROGRESS 7/N** — Preparando handoff final.

*Typing não conta como progress update.*

### 2. Regra de evidência
Inclua a frase **"Sem evidência, não aconteceu."** em todas as descrições de etapas. Não declare execução, validação, diff limpo, teste verde, commit ou push sem saída real, status real ou evidência objetiva.

### 3. Git status obrigatório
Antes de qualquer alteração:

```
git status --short
```
Se houver alterações fora do escopo, declare **BLOCKED** ou **NEEDS_REVIEW** e interrompa.

Depois da alteração, execute sequencialmente:

```
git status --short

git diff --stat

git diff --check
```
Revise os arquivos alterados antes de prosseguir.

### 4. Arquivos untracked
Documente que `git diff --stat` não mostra arquivos não rastreados. Para arquivos novos, siga:

* Use `git status --short` para visualizá‑los.
* Confirme a existência com `test -f <path>` ou `ls <path>`.
* Quando precisar ver diff de um novo arquivo sem fazer stage, use `git add -N <path>`.

### 5. Commit e push
Reforce que commit e push são bloqueados por padrão e só podem ocorrer com autorização explícita na tarefa corrente.

* Antes de commit, revise `git status --short`, `git diff --stat` e valide todas as regras aplicáveis.
* Antes de push, confirme branch, estado limpo após commit e ausência de secrets no diff.
* Nunca commite secrets, arquivos `.env`, tokens, credenciais ou arquivos temporários.

### 6. Falha de ferramenta/comando
Se `read_file`, `write_file`, comandos de shell ou operações Git falharem:

* Não repita a mesma ação em loop.
* Não ignore o erro.
* Declare **BLOCKED**.
* Reporte o erro real.
* Sugira próximo passo.

### 7. Estados finais
Toda tarefa deve terminar com um dos seguintes estados:

* **DONE**
* **NEEDS_REVIEW**
* **BLOCKED**
* **NO_CHANGES**

### 8. Handoff final obrigatório
O handoff final deve conter:

* Status final.
* Arquivos criados/alterados.
* Comandos executados.
* Evidências/saídas reais.
* Validações realizadas.
* Riscos identificados.
* Pendências restantes.
* `git status --short` final.
* Próximo passo recomendado.
* Se commit/push foi feito ou não (deve ser **não** neste caso).

### 9. Validação obrigatória da skill
Ao terminar, execute:

```
git status --short

git diff --check

git diff --stat

grep -n -E "PROGRESS|Typing não conta|Sem evidência|git diff --stat|git add -N|BLOCKED|NEEDS_REVIEW|NO_CHANGES|commit|push" skills/hermes/git-safe-workflow/SKILL.md
```
Revise se nenhum token, secret, `.env` ou credencial entrou no diff.

### 10. Reporte final (handoff)
Inclua todas as seções descritas em **8. Handoff final obrigatório**.


Ao final, reporte:

- arquivos alterados;
- resumo da mudanca;
- comandos de validacao executados;
- resultado de `git status --short`;
- resultado de `git diff --stat`;
- riscos ou pendencias;
- se houve commit;
- se houve push.
