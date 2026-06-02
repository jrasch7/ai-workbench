# Operational Workflow — AI Workbench

Este documento define o fluxo operacional padrão da bancada.

## Objetivo

Transformar uso solto de IA em processo de engenharia auditável.

A bancada não deve depender de conversa solta, memória informal ou confiança cega no agente.

## Fluxo padrão

```text
Project Context -> Task Brief -> Architect -> Executor -> Validator -> Integrator
```

## Etapa 1 — Selecionar contexto do projeto

Antes de qualquer tarefa real, escolher o contexto correto em:

```text
context/projects/
```

Contextos atuais:

```text
context/projects/NIVELA.md
context/projects/SISOPERP_WEB.md
```

## Etapa 2 — Criar Task Brief

Usar o template:

```text
context/templates/TASK_BRIEF_TEMPLATE.md
```

O Task Brief deve conter:

- objetivo;
- problema atual;
- escopo permitido;
- fora do escopo;
- regras obrigatórias;
- critérios de aceite;
- validação obrigatória;
- handoff esperado.

## Etapa 3 — Architect

Usar quando a tarefa ainda estiver grande, confusa ou arriscada.

Perfil:

```text
agents/architect/AGENT.md
```

Saída esperada:

- diagnóstico;
- plano;
- riscos;
- escopo;
- fora do escopo;
- critérios de aceite;
- prompt para Executor.

## Etapa 4 — Executor

Usar apenas quando a tarefa estiver pequena e delimitada.

Perfil:

```text
agents/executor/AGENT.md
```

O Executor implementa, mas não commita e não faz push.

## Etapa 5 — Validator

Usar sempre após implementação.

Perfil:

```text
agents/validator/AGENT.md
```

O Validator revisa diff, executa validações e decide se a entrega está aprovada, aprovada com ressalvas ou reprovada.

## Etapa 6 — Integrator

Usar somente após validação aprovada e autorização do usuário.

Perfil:

```text
agents/integrator/AGENT.md
```

O Integrator prepara commit, push, PR e handoff final.

## Fontes de verdade

Nunca confiar apenas na resposta final do agente.

Fontes de verdade:

```text
git status
git diff
git diff --stat
testes
build
lint
logs
comportamento observado
```

## Regra para modelos fracos

Com modelo gratuito ou instável, usar apenas para:

- tarefas pequenas;
- validações simples;
- geração de rascunho;
- laboratório.

Não usar modelo fraco para:

- alteração grande;
- arquitetura crítica;
- migração;
- financeiro;
- billing;
- segurança;
- produção.

## Regra para modelos fortes

Com LLM forte, a bancada deve continuar usando o mesmo processo.

Modelo melhor não elimina validação.

Modelo melhor apenas melhora a qualidade do Architect, Executor e Validator.

## Comandos base

Diagnóstico:

```bash
./scripts/aiw doctor
```

Subir gateway:

```bash
./scripts/aiw gateway
```

Listar modelos:

```bash
./scripts/aiw models
```

Testar chat do modelo sem OpenHands:

```bash
./scripts/aiw smoke dev-coder
```

Abrir bancada no repo atual:

```bash
./scripts/aiw current
```

Abrir bancada no AI Workbench:

```bash
./scripts/aiw repo
```

Parar tudo:

```bash
./scripts/aiw stop
```

## Critério de uso em projeto real

Antes de usar em Nivela ou SisOpERP Web, é obrigatório ter:

- contexto do projeto selecionado;
- Task Brief preenchido;
- escopo pequeno;
- validações definidas;
- branch correta;
- plano de rollback quando houver risco.

## Decisão estratégica

A bancada deve evoluir para plataforma confiável.

Não aceitar fluxo que só funciona uma vez.

Não aceitar agente que altera sem validação.

Não aceitar documentação que não ajuda a operar.
