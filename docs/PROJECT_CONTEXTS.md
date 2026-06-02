# Project Contexts — AI Workbench

Este documento define como o AI Workbench deve armazenar e usar contexto de projetos reais.

## Objetivo

Cada projeto precisa ter um contexto operacional próprio antes de ser entregue a um agente.

Sem contexto, uma LLM boa ainda chuta.

Com contexto bem estruturado, a bancada consegue orientar agentes para trabalhar com menos risco.

## Estrutura

Os contextos ficam em:

```text
context/projects/
```

Projetos iniciais:

```text
context/projects/NIVELA.md
context/projects/SISOPERP_WEB.md
```

## O que cada contexto deve conter

- visão do produto;
- stack técnica;
- regras de negócio importantes;
- módulos críticos;
- comandos de validação;
- riscos conhecidos;
- o que o agente pode fazer;
- o que o agente não pode fazer;
- padrão de Git e handoff.

## Regra operacional

Antes de qualquer agente atuar em um projeto real, o prompt deve incluir:

```text
1. contexto do projeto;
2. tarefa específica;
3. escopo permitido;
4. fora do escopo;
5. validação obrigatória;
6. formato de handoff.
```

## Prioridade

Nesta fase, contexto é mais importante que automação.

O objetivo não é fazer o agente sair mexendo em tudo.

O objetivo é preparar uma base que permita, depois, usar modelos LLM melhores de forma controlada e produtiva.
