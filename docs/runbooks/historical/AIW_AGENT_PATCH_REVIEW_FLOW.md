# AIW Agent Patch Review & Apply Flow

## Resultado

O **Agent Patch Review & Apply Flow** é a última ponte segura de integração contínua local do AI Workbench. Ele engloba patches gerados por Agentes (na fila ou one-shots) dentro de um Lifecycle persistente. Isso conecta de forma determinística: Queue Item -> Validation Plan -> Review Gate -> Evidence Bundle -> Apply Manual.

## Lifecycle

O Lifecycle é guardado como metadata offline e read-only local (`.aiw/workspaces/*/patch-review-flow/*`). Ele armazena transições de estado (`discovered`, `linked`, `validation_required`, `review_ready`, `applied`, `rolled_back`). Ao amarrar os IDs cruzados (patch, inbox item, agent queue, agent attempts), criamos rastreabilidade fim a fim sem forçar push.

## Linking queue items to patches

Com a CLI/Cockpit, informamos que o patch gerado pertence a um `queue_item_id`.
O status do lifecycle entra em `validation_required` e as métricas do Patch Review Flow ganham vida (sendo consumidas em uma estrutura resumida única).

## Validation e Review Gate

O fluxo depende estritamente do `Validation Plan` e do `Review Gate`. O Lifecycle não executa auto-testes nem aplica overrides. Ele apenas consolida a visibilidade para a decisão humana no Cockpit, determinando se `can_apply_reviewed` é seguro (ou seja, se o gate retornou `ready` ou `docs_only`).

## Evidence Bundle

Ao executar "Apply Reviewed" na UI, o lifecycle automaticamente engatilha um `Evidence Bundle` de sucesso com status `applied`. Isso significa que o audit é inviolável e amarrado àquela alteração em disco.

## Apply reviewed

Só é habilitado caso o Cockpit identifique `gate = ready`. Quando o usuário pressiona Apply via POST (e exige explicitamente a key `confirm=true`), a rotina engatilha internamente o flow legado de segurnaça `project_patch_apply`. O patch é efetivado no *working tree*, o lifecycle transita pra `applied` e se registra o datetime seguro (`applied_at`).

## Rollback reviewed

A mesma estrutura é utilizada para `rollback`. Caso uma alteração `applied` se prove errada, o flow permite reverter (`project_patch_rollback`), mudando o lifecycle pra `rolled_back` e anotando as reasons pro Evidence Bundle (como `Manual rollback`).

## Cockpit

Na UI em "Bancada de Execução", cada card de Patch agora possui o container **Patch Review Flow**. Nele o usuário pode gerenciar os links com a fila, checar o status do Lifecycle e interagir via Form POST explícitos.
Mensagem gravada na UI reforça a tese de segurança: "Apply reviewed usa o patch flow seguro existente e exige confirmação explícita."

## Segurança

- sem execução automática;
- sem LLM pela UI;
- sem auto-apply;
- sem auto-commit;
- sem push;
- sem leitura de .env;
- usa patch flow seguro existente;
- recusa requisições HTTP sem flag explicit `confirm`.

## Limitações

- lifecycle local;
- sem override de gate (ainda);
- rollback depende da implementação legada (não refaz bundle complexo sozinho);
- sem background worker.

## Próximo passo recomendado

O ciclo de AIW está muito forte no aspecto offline e CI/CD defensivo. O proximo passo pode envolver a **Automatização de Integrações Externas Seguras** - por exemplo, background daemon restrito que possa sincronizar apenas Inbox/Outbox periodicamente, reduzindo comandos manuais de Intake, e preparando o terreno real para Continuous Agent Workflow.

A entrada deste fluxo pode ser impulsionada pelo batch do [AIW Agent Queue Foreground Dispatcher](AIW_AGENT_QUEUE_FOREGROUND_DISPATCHER.md).
