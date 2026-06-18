# AIW Local Monolith MVP

## 1. Decisão

O AI Workbench deve continuar evoluindo localmente neste PC, sem depender de cloud neste momento.

O modelo inicial é um monólito local bem estruturado:

- fila local de tarefas;
- política por tarefa;
- runner local;
- logs e evidências em `.aiw/runs`;
- scripts simples;
- integração futura com Hermes, Ralph Loop, Paperclip e cockpit web.

## 2. Objetivo

Permitir que o AIW execute tarefas L0/L1 de forma controlada, com rastreabilidade e sem depender de respostas longas no Telegram.

## 3. Escopo do MVP

Este MVP não executa LLM ainda.

Ele cria a base operacional:

- `scripts/aiw-status`;
- `scripts/aiw-task-create`;
- `scripts/aiw-runner-once`;
- `.aiw/tasks`;
- `.aiw/runs`;
- `.aiw/state`.

## 4. Fila de tarefas

Filas locais:

- `inbox`;
- `running`;
- `blocked`;
- `review`;
- `done`;
- `failed`.

Arquivos de tarefa são runtime local e não devem ser commitados.

## 5. Runs

Cada execução deve criar uma pasta em `.aiw/runs`.

A pasta de run deve conter:

- `task.md`;
- `summary.md`;
- `status.json`;
- `commands.log`;
- `validation.log`.

## 6. Níveis permitidos no MVP

Permitidos:

- L0 — somente leitura;
- L1 — documentação, relatório, evidência e organização local.

Bloqueados:

- commit;
- push;
- deploy;
- secrets;
- `.env`;
- produção;
- ações destrutivas.

## 7. Próxima evolução

Depois deste MVP:

1. plugar Hermes/LiteLLM;
2. criar policy parser mais forte;
3. integrar Ralph Loop;
4. integrar Paperclip;
5. criar cockpit web local;
6. criar Cloudflare Tunnel quando o PC principal estiver disponível.

## 8. Critérios de sucesso

- criar tarefa local;
- listar status;
- executar runner uma vez;
- gerar run;
- não versionar runtime;
- bloquear níveis fora do MVP;
- manter Git limpo exceto arquivos estruturais.
