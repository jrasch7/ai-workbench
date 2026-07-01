# AIW Agent Queue Foreground Dispatcher

## Resultado

O **Agent Queue Foreground Dispatcher v1** permite processar continuamente a Agent Queue em modo foreground no terminal, consultando metadados locais de `dispatch.json` e repassando o trabalho para o Agent Queue CLI que, por fim, isola as chamadas para o Offline Runner ou o LLM Execution Guard. Ele unifica o processamento de "Patch Intents" de forma 100% controlada e supervisionada.

## Por que não é daemon

Assim como o Foreground Worker Loop (que lida com envios e integrações), o Dispatcher de Agentes precisa rodar visivelmente, permitindo interrupção instantânea (Ctrl+C). Não existem jobs cron escondidos consumindo a chave da API do LLM em background silenciosamente.

## Dispatch metadata

O `dispatch.json` na fila (`agent-queue/<id>/dispatch.json`) é mandatório. Sem ele, mesmo um item `ready` será ignorado e marcado como `blocked`.

Exemplo de configuração (Offline mode):
`./scripts/aiw-agent-queue --workspace aiw --item aq-xxxxx --set-dispatch --dispatch-mode offline --confirm`

Exemplo de configuração (LLM mode):
`./scripts/aiw-agent-queue --workspace aiw --item aq-xxxxx --set-dispatch --dispatch-mode llm --model dev-coder --confirm`

## Dry-run

Rodando `./scripts/aiw-agent-dispatcher --workspace aiw --once`, o dispatcher vai encontrar os itens `ready`, vai validar se eles possuem `dispatch.json`, e vai registrar uma entrada `would_run_offline` ou `would_run_llm` nos `attempts` sem invocar efetivamente o agente.

## Execute mode

`./scripts/aiw-agent-dispatcher --workspace aiw --once --execute --confirm-agent-dispatcher`

Se validado, ele engatilha o CLI:
`./scripts/aiw-agent-queue --workspace aiw --item aq-xxxxx --confirm [--run-offline | --run-llm --confirm-llm --model X]`

## Separação de Responsabilidades

- **Dispatcher**: Encontra itens, varre a fila, checa dispatch params, gerencia modo bulk (once/watch), salva Run metrics.
- **Agent Queue CLI**: Acionado pelo dispatcher, ele interage especificamente com aquele `queue_item_id`, invoca o Python subprocess do runner real com restrições e timeout, parseando stdout e stderr para o `attempt_id`.
- **LLM Guard**: Presente no Runner de Agent, ele garante que apenas o modelo permitido no `llm_execution` seja validado no ambiente.

## Segurança

- dry-run por padrão;
- execute exige `--confirm-agent-dispatcher`;
- sem execução via UI;
- `shell=False` no subprocesso;
- sem daemon, cron, ou background scheduler.
