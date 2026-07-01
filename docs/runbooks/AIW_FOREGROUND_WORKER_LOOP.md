# AIW Foreground Worker Loop

## Resultado

O **Foreground Worker Loop v1** permite processar continuamente a Integration Outbox em modo foreground no terminal, consultando a política e chamando comandos em lote. Ele solidifica a infraestrutura de Integração Contínua puramente local, preservando o princípio do controle humano.

## Por que não é daemon

O AIW foi desenhado para maximizar a transparência e evitar acidentes de execução autônoma. Sendo Foreground, o processo não roda escondido com `systemd`, `cron`, `tmux` ou schedulers fantasma. Ele demanda intervenção declarativa (`--watch`) e morre se fechado (Ctrl+C), evitando pushs inesperados enquanto o operador não está prestando atenção.

## Dispatch metadata

O `dispatch.json` é um metadado complementar salvo em `integration-outbox/<id>/dispatch.json`.
Ele é mandatório e informa ao worker loop quem é o alvo de fato (ex: `github_pr` e `--pr-number 123`). Sem o `dispatch.json` presente e setado como `enabled: true`, o worker loop ignora o payload, mesmo que ele esteja em `ready`.

O comando que gera e habilita isso é:
`./scripts/aiw-integration-worker --set-dispatch --pr-number 123 --confirm-dispatch`

## Dry-run

Por segurança, rodar `./scripts/aiw-worker-loop --workspace aiw --once` sempre opera em **dry-run**.
Ele escaneia a Outbox, vê os patches autorizados, cruza com a Política de Workers (Policy), valida se a policy bloquearia, mas ao invés de atirar, ele marca o attempt local com status `would_execute` sem invocar o `aiw-integration-worker` final (e sem chamar `gh`).

## Execute mode

Para executar reais modificações na PR (ou outra integração no futuro):
`./scripts/aiw-worker-loop --workspace aiw --once --execute --confirm-worker-loop`

O loop faz o check de elegibilidade e Policy. Se tudo passar, ele gera subprocesso isolado repassando a ação pro CLI `aiw-integration-worker` que fará a chamada final via `gh`.

## Watch foreground

Com `--watch --interval-seconds 30`, o processo prende o terminal rodando o ciclo inteiro (once) a cada 30 segundos, até que seja cancelado. Excelente para janelas de terminal dedicadas ao "CI Local".

## External Worker Policy

O loop obedece e repassa a verificação de `can_worker_execute` da **External Worker Policy**.
Se a aba estiver bloqueada via `.json` (`enabled: false`), o worker reportará `items_blocked += 1` e interromperá na hora a chamada daquele artefato.

## Segurança

- dry-run por padrão;
- execute exige `--confirm-worker-loop`;
- item precisa estar com status `ready`;
- dispatch explícito obrigatório;
- policy precisa permitir;
- `shell=False` no subprocesso;
- sem UI execution;
- sem daemon;
- sem cron;
- sem background;
- sem push arbitrário;
- sem merge arbitrário;
- sem Jira nativo (restrito à CLI).

## Limitações

- GitHub PR edit apenas, com gh.
- Sem retry automático nos itens falhos pelo loop.
- Sem systemd, scheduler daemon.
- Sem Jira, issue create ou merge.

Análogo ao Worker Loop, temos agora o [AIW Agent Queue Foreground Dispatcher](AIW_AGENT_QUEUE_FOREGROUND_DISPATCHER.md) com as mesmas premissas de UX local.
