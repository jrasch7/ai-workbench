# Hermes Adoption Plan — AI Workbench

## Decisao

Hermes passa a ser o candidato principal para a camada de agente do AI Workbench.

OpenHands fica como laboratorio opcional, nao como nucleo operacional.

## Motivo

O objetivo do AI Workbench e construir uma bancada de engenharia assistida por agentes, com contexto, validacao, Git, seguranca e execucao confiavel.

OpenHands mostrou instabilidade em tarefas simples de edicao documental e nao entregou produtividade suficiente para ser o nucleo da plataforma.

Hermes parece mais alinhado com a visao porque oferece:

- operacao via Telegram;
- memoria persistente;
- skills;
- ferramentas de terminal e arquivos;
- execucao remota;
- suporte a multiplos provedores;
- MCP;
- tarefas agendadas;
- possibilidade de rodar em PC, Docker, SSH ou servidor.

## Arquitetura desejada

```text
Telegram / CLI
-> Hermes
-> AI Workbench contextos, skills e runbooks
-> LiteLLM ou provider configurado
-> Terminal / Git / testes / validacao
-> Handoff
```

## Papel do AI Workbench

O AI Workbench continua sendo a base operacional:

- documentacao;
- contextos por projeto;
- perfis de agentes;
- templates de tarefa;
- aliases por papel;
- validacao de modelos;
- runbooks;
- regras de Git;
- criterios de seguranca.

Hermes deve usar essa base, nao substituir tudo.

## Fases

### H0 — Documentar decisao

- Registrar por que OpenHands saiu do nucleo.
- Registrar por que Hermes entra como candidato principal.
- Definir riscos e criterios de teste.

### H1 — Instalacao isolada

- Instalar Hermes com cuidado.
- Validar versao e comandos basicos.
- Nao expor secrets.
- Nao misturar com repos reais antes do smoke.

### H2 — Provider inicial

- Avaliar OpenRouter, Nous Portal, Gemini free, Groq ou outro provider de baixo custo.
- Evitar depender de quota free instavel.
- Manter aliases por papel.

### H3 — Primeiro teste local

- Pedir para editar um Markdown simples.
- Validar git status.
- Validar git diff.
- Confirmar que respeita escopo.

### H4 — Backend Docker ou sandbox

- Rodar tarefas em ambiente controlado.
- Montar somente diretorios necessarios.
- Evitar acesso amplo ao HOME.
- Sem sudo.

### H5 — Telegram

- Criar bot separado.
- Autorizar somente o usuario correto.
- Testar mensagem simples.
- Testar tarefa pequena via Telegram.

### H6 — Skills proprias

Criar skills para:

- Git safe workflow;
- Validator;
- Handoff;
- Nivela;
- SisOpERP Web;
- troubleshooting;
- documentacao operacional.

### H7 — Autonomia controlada

- Tarefas agendadas;
- relatorios;
- diagnosticos;
- commit apenas com autorizacao;
- push e PR apenas com autorizacao.

## Riscos

- Expor secrets;
- dar acesso amplo demais ao PC;
- agente executar comandos destrutivos;
- custo de provider sair do controle;
- Telegram virar superficie de ataque;
- automacao commitar alteracoes ruins;
- perder rastreabilidade.

## Regras de seguranca

- Nunca colar chaves no chat.
- Nunca commitar .env.
- Nao usar sudo em tarefas de agente.
- Nao permitir push automatico no inicio.
- Nao permitir comandos destrutivos sem aprovacao.
- Sempre validar git status e git diff.
- Sempre limitar escopo da tarefa.

## Primeiro criterio de sucesso

Hermes deve conseguir executar uma tarefa que OpenHands falhou:

```text
Editar um unico arquivo Markdown existente, sem alterar mais nada, sem commit, e reportar git status e git diff.
```

## Decisao atual

Seguir com Hermes como camada de agente candidata.

Manter OpenHands apenas como laboratorio.

Continuar evoluindo o AI Workbench como base propria de engenharia.
