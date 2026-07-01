# AIW Integration Worker CLI

## Resultado

O **Integration Worker CLI** é uma ferramenta puramente CLI que tem a responsabilidade de inspecionar os pacotes salvos na `Integration Outbox` e, se instruído, realizar chamadas de sistema (usando a ferramenta externa `gh` para o GitHub PR, por exemplo) para publicá-los nos destinos corretos de forma segura e não automatizada.

## Dry-run

Por padrão, invocar a ferramenta executa no modo **dry-run**. Nenhuma chamada de rede ou execução externa real acontece. Apenas registra uma simulação na subpasta `attempts/` de que o payload passou na checagem inicial.

## Execute mode

Para que o CLI execute algo de verdade, é preciso provar a intenção passando a flag explícita `--execute` E também a confirmação extra `--confirm-external-send`.
Se o destino for um PR, `--pr-number <N>` deve ser informado. 

## GitHub PR edit

O CLI não cria PRs e não lista PRs. Ele pega o markdown empacotado em `payload.md` e usa subprocess invocando:
`gh pr edit <pr_number> --body-file <absolute_path_to_payload>`
O worker apenas executa esse comando isolado e captura o exit status.

## Attempt logs

Toda execução (seja dry-run, seja execute, seja com erro) registra um artefato JSON na subpasta `attempts/` da respectiva outbox entry. Isso provê trilhas de auditoria para saber quem enviou o quê, ou por que o comando falhou (ex.: se o `gh` cli não estava autenticado).

## Segurança

- **dry-run por padrão**;
- exige as flags destrutivas `--execute` e `--confirm-external-send` para agir;
- exige o contexto (ex. `--pr-number`);
- usa `shell=False` no Python `subprocess` para evitar shell injection via nome de payload ou PR num;
- não faz **push**;
- não **cria PR** nova automaticamente;
- não possui backend HTTP, não escuta em background nem roda pela UI (na versão atual);
- não lê nem expõe `.env`;
- não envia dados para o Jira.

## Limitações

- Por enquanto atende apenas a integração rudimentar baseada no edit do corpo de um GitHub PR;
- Exige que o binário do `gh` esteja instalado e autenticado na máquina hospedeira;
- Sem daemon em background, sem scheduler embutido (exige rodar a cada vez manual);
- Sem sistema de retry automático (deve chamar o CLI novamente).
- Sem Jira.

## Próximo passo recomendado

Avaliar se devemos migrar esse script para um daemon (Integration Sync Worker) que monitore localmente a pasta de Outbox buscando `ready` para processar a cada X minutos via cron.
- [AIW GitHub Intake CLI](AIW_GITHUB_INTAKE_CLI.md)
