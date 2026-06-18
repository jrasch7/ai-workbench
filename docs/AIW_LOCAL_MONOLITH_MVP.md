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

## 9. Runner contínuo local

O script `scripts/aiw-runner-watch` executa o runner em loop local.

Características:

- lê a fila `.aiw/tasks/inbox`;
- chama `scripts/aiw-runner-once`;
- respeita o intervalo `AIW_WATCH_INTERVAL`;
- suporta `AIW_WATCH_MAX_ITERATIONS` para smoke tests;
- para com `Ctrl+C`;
- não chama LLM;
- não faz commit;
- não faz push;
- não lê secrets;
- grava evidências em `.aiw/runs`.

Este é o primeiro passo para operação 24/7 local antes de integrar Hermes, Ralph Loop, Paperclip e cockpit web.

## 10. LLM adapter opcional

O script `scripts/aiw-llm-ask` é o adapter local para chamar modelos via `scripts/model-ask`.

O runner continua seguro por padrão:

- `AIW_LLM_ENABLED=0` não chama modelo;
- `AIW_LLM_ENABLED=1` chama `scripts/aiw-llm-ask`;
- `AIW_MODEL` define o modelo, com fallback `dev-gemini-fast`;
- prompts e respostas completas ficam em `.aiw/runs`;
- terminal recebe apenas resumo;
- commit, push, deploy e secrets continuam bloqueados no MVP.

Esta camada prepara a integração com Hermes, LiteLLM, Ralph Loop e Paperclip sem transformar o runner em agente autônomo irrestrito.

## 11. Executor documental L1

O runner suporta tarefas documentais L1 com `Output file`.

Fluxo:

1. `scripts/aiw-doc-task-create` cria uma tarefa em `.aiw/tasks/inbox`;
2. a tarefa declara `Task type: doc`;
3. a tarefa declara `Output file: docs/...md`;
4. `scripts/aiw-runner-once` chama o modelo quando `AIW_LLM_ENABLED=1`;
5. o modelo devolve o documento entre markers;
6. o runner extrai o documento;
7. o arquivo é gravado em `docs/`;
8. o commit continua manual.

Guardrails:

- só permite saída em `docs/*.md`;
- bloqueia path absoluto;
- bloqueia `..`;
- bloqueia `.env`;
- não faz commit;
- não faz push;
- mantém evidência completa em `.aiw/runs`.

## 12. Fallback documental

O executor documental L1 prefere documentos entre markers `---BEGIN_AIW_DOCUMENT---` e `---END_AIW_DOCUMENT---`.

Se o modelo não obedecer aos markers, o runner usa fallback seguro:

- remove linhas de transporte do `model-ask`;
- grava o Markdown bruto gerado;
- registra `doc_status=generated_without_markers_fallback`;
- mantém evidência completa no run;
- não faz commit automático.

## 13. Aprovação de run

O script `scripts/aiw-run-approve` promove um run revisado para `done`.

Fluxo:

1. lê o último run ou um run informado;
2. encontra o `Task ID`;
3. move a task de `.aiw/tasks/review` para `.aiw/tasks/done`;
4. grava `approval.md` dentro do run;
5. atualiza `status.json` para `done`;
6. não faz commit;
7. não faz push.

Este comando representa o primeiro checkpoint humano explícito do AIW Local Monolith MVP.
