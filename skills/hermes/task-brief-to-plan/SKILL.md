# Task Brief to Plan

Use esta skill quando o usuario trouxer uma tarefa, ideia, bug, melhoria ou fase de projeto que precise ser planejada antes da execucao.

## Objetivo

Transformar um pedido bruto em um plano tecnico claro, seguro e executavel.

Esta skill deve ser usada antes de alterar arquivos, especialmente em tarefas de engenharia, arquitetura, refactor, debug, migracao, infraestrutura, integracao, financeiro, multi-tenant, seguranca ou automacao.

## Regra central

Nunca pule direto para implementacao quando a tarefa ainda nao estiver clara.

Primeiro produza um plano.

## Saida obrigatoria

A resposta deve conter as secoes abaixo.

### Entendimento da tarefa

Explique o que o usuario quer em linguagem objetiva.

Se houver ambiguidade, declare a ambiguidade.

### Objetivo tecnico

Defina o resultado tecnico esperado.

### Escopo permitido

Liste o que pode ser alterado.

### Fora do escopo

Liste o que nao deve ser alterado nesta rodada.

### Arquivos ou areas provaveis

Liste arquivos, diretorios, modulos ou servicos que provavelmente precisam ser analisados.

Se nao souber ainda, diga que precisa investigar antes.

### Plano de execucao

Quebre em passos pequenos e verificaveis.

Cada passo deve ter objetivo claro.

### Validacoes previstas

Liste comandos, testes, lint, smoke, diff ou verificacoes manuais esperadas.

Nunca invente validacoes que nao existem.

### Riscos

Liste riscos tecnicos, funcionais, operacionais, de seguranca, dados, custo ou regressao.

### Criterios de aceite

Liste como saberemos que a tarefa foi concluida com sucesso.

### Necessita confirmacao?

Diga se pode seguir ou se precisa de confirmacao do usuario antes de executar.


## Regra anti-alucinacao operacional

Ao planejar integracoes externas, ferramentas, comandos, APIs, providers, Telegram, GitHub, Docker, cloud, gateway, billing ou seguranca:

- nao invente comandos, flags, campos de config ou capacidades;
- se nao tiver certeza, marque como `precisa verificar`;
- diferencie fato conhecido, inferencia e hipotese;
- recomende consultar documentacao oficial antes de executar;
- nao cite configuracoes sensiveis como se estivessem confirmadas;
- nao assuma que um recurso existe apenas porque seria conveniente.

Se o plano depender de comportamento especifico de ferramenta externa, inclua uma secao chamada `Pontos que exigem verificacao`.


## Regra para ferramentas externas nao verificadas

Quando a tarefa envolver uma ferramenta externa ou recurso ainda nao verificado, como Telegram, GitHub, Docker, cloud, API de provider, gateway, billing, OAuth, webhook, MCP ou seguranca:

- nao liste comandos concretos como se fossem certos, exceto comandos ja confirmados no ambiente atual;
- nao liste nomes de campos de config como se fossem certos sem verificar arquivo, help local ou documentacao oficial;
- nao use exemplos de outras plataformas como se fossem da ferramenta atual;
- nao transforme hipotese em instrucao executavel;
- nao diga que algo e suportado se ainda nao foi confirmado;
- produza primeiro um plano de investigacao;
- inclua uma secao `Fatos confirmados no ambiente atual`;
- inclua uma secao `Hipoteses nao confirmadas`;
- inclua uma secao `Comandos seguros para investigar`;
- inclua uma secao `Nao executar ainda`.

Se a documentacao oficial nao foi consultada na tarefa atual, diga explicitamente: `Documentacao oficial ainda nao consultada nesta tarefa`.

Se um comando ou campo de configuracao nao foi verificado por `--help`, arquivo local, config atual ou documentacao oficial, marque como `nao confirmado`.


## Regra de comandos e campos confirmados

Em planos de investigacao, comandos, flags, nomes de campos de config, variaveis de ambiente, endpoints, webhooks, permissoes e modos de aprovacao so podem ser citados como instrucao concreta quando houver evidencia.

Evidencias aceitas:

1. o comando foi executado ou inspecionado na sessao atual;
2. o comando apareceu em `--help` local;
3. o usuario forneceu explicitamente;
4. a documentacao oficial foi consultada na tarefa atual;
5. um arquivo local de config/documentacao do projeto confirma o nome.

Se nao houver evidencia, escreva `nao confirmado`.

Nao escreva exemplos como `gateway.telegram.*`, `approvals.mode`, `security.redact_secrets`, `BOT_TOKEN`, webhook automatico, intents, OAuth, rate limit ou campos semelhantes como se fossem reais sem verificacao.

Quando a tarefa pedir plano de investigacao, nao inclua passo de execucao. Inclua apenas comandos seguros para investigar, preferencialmente `--help`, `config show`, `config path`, `status`, `doctor` ou leitura de documentacao local.

Se o usuario pedir para configurar algo externo sem pesquisa/documentacao, a resposta deve parar em investigacao e pedir confirmacao antes de executar qualquer configuracao.

## Regras

- Nao altere arquivos durante o planejamento.
- Nao faca commit.
- Nao faca push.
- Nao leia ou exponha secrets.
- Nao assuma acesso a provider pago, ambiente externo ou credenciais.
- Se a tarefa envolver risco alto, recomende dividir em fases.
- Se a tarefa envolver Git, combine com a skill git-safe-workflow.
- Se a tarefa for finalizada, combine com a skill engineering-handoff.

## Quando usar

Use para:

- planejar fase de projeto;
- decompor tarefa grande;
- preparar prompt para executor;
- revisar arquitetura;
- organizar debug;
- preparar integracao;
- planejar alteracao em Nivela, SisOpERP Web ou AI Workbench.
