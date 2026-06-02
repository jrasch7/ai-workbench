# Agents — AI Workbench

Este documento resume os papéis formais dos agentes da bancada.

## Fluxo recomendado

```text
Architect -> Executor -> Validator -> Integrator
```

## Architect

Arquivo:

```text
agents/architect/AGENT.md
```

Responsável por diagnóstico, plano, escopo, riscos e critérios de aceite.

Não implementa.

## Executor

Arquivo:

```text
agents/executor/AGENT.md
```

Responsável por implementar alterações pequenas dentro do escopo.

Não commita e não faz push.

## Validator

Arquivo:

```text
agents/validator/AGENT.md
```

Responsável por revisar diff, executar validações e aprovar ou reprovar.

Não implementa feature nova.

## Integrator

Arquivo:

```text
agents/integrator/AGENT.md
```

Responsável por commit, push, PR e handoff final somente quando autorizado.

## Regra central

Nenhum agente é fonte de verdade sozinho.

A fonte de verdade é Git, testes, logs, build, lint e comportamento observado.

## Uso prático

Para tarefa real:

1. Selecionar Project Context.
2. Criar Task Brief.
3. Architect quebra o plano quando necessário.
4. Executor implementa.
5. Validator revisa.
6. Integrator consolida.
