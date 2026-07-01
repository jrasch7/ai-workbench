# AIW GitHub Worker Policy Integration

## Resultado

O **Integration Worker CLI** agora consulta a **External Worker Policy** antes de executar qualquer comando de edição externa, como o `gh pr edit`. Isso consolida a barreira offline do AI Workbench, impedindo que requisições acidentais vazem para sistemas terceiros (GitHub/Jira).

## O que mudou

Anteriormente, o `aiw-integration-worker` apenas verificava as flags manuais (`--execute --confirm-external-send --pr-number`).
Agora, ele importa e executa o `can_worker_execute` da camada de Policy antes de invocar o comando local (`gh`).

Se a Policy retornar `allowed: False`, o attempt log registra o bloqueio com status `"blocked"` detalhando o motivo (ex: "Worker github_pr_edit is disabled" ou "Background mode is blocked").

## Worker manual

O AIW continua totalmente operado por humanos. Nenhuma chamada de API, Daemon ou Scheduler envia PRs ou comentários sozinhos. Toda tentativa de push exige invocação da CLI:

`./scripts/aiw-integration-worker --workspace aiw --item <id> --execute --confirm-external-send --pr-number 123`

## External Worker Policy

As verificações da Policy bloqueiam estritamente:
- Ações globais (`enabled: false`)
- Tentativas em Background (`allow_background: false`)
- Chamadas a partir da interface web (`allow_ui_execution: false`)
- Workers não catalogados ou não autorizados (`name: github_pr_edit`)
- Ações banidas no configuration profile (`blocked_actions: ["push", "merge"]`)

## Fluxo permitido

O fluxo saudável para editar uma PR agora é:
Outbox item ready → CLI manual → flags explícitas → **policy check** → gh pr edit (somente se permitido) → attempt log (succeeded) → external_sent true (somente após sucesso).

## Fluxos bloqueados

A política e a CLI propositalmente bloqueiam:
- UI execution;
- Background execution;
- Daemon/cron runners;
- Schedulers;
- git push, PR create, PR merge, issue comment;
- Jira e acesso nativo a GitHub API sem `gh`.

## Segurança

- **Policy default deny**: Sem override expresso em `aiw-workspaces.json`, a policy falha de forma segura (nega tudo).
- **shell=False**: `subprocess.run` do Integration Worker jamais injeta strings como scripts shell bash completos, ele exige array seguro de argumentos.
- **Sem `.env`**: Nenhum dado sensível de token é lido. O `gh` precisa estar autenticado via user-level keychain ou global token pré-fornecido pelo SO.
- **Sem secrets em logs**: Tentativas recusam se o `payload.md` vazar strings como `LITELLM_MASTER_KEY` ou `SECRET_`.

## Limitações

- Por enquanto, suporta apenas `github_pr_edit` (target `github_pr`, kind `pr_summary`).
- Nenhum daemon ativo monitorando webhook;
- Nenhum Jira.
- Nenhum mecanismo de merge automático (merge manual exigido no portal/GitHub UI).
