# AIW Agent Run Queue

## Resultado

O **Agent Run Queue** atua como uma esteira manual que absorve os *Patch Intents* (gerados via `Integration Inbox` a partir do GitHub Intake) e os transforma em lotes de execução explícitos para o Agente offline. A fila em si não dispara background jobs nem crons, ela apenas formaliza o estado do sistema e delega a um humano a aprovação do início do job via CLI.

## Queue items

Cada item da fila é gerado usando:
`./scripts/aiw-agent-queue --workspace <ws_id> --from-inbox <inbox_item_id>`

Ou na aba Agent Run Queue do painel `Harness` do Cockpit.

Eles começam no status `draft`, e não contêm chamadas acopladas a provedores de LLM. 

## Task prompt

Na conversão da Inbox para a Queue, três arquivos estruturados são gravados localmente em disco para instruir um eventual Agente Executor (em `.aiw/workspaces/*/agent-queue/<id>/`):
1. `task.md`: O Prompt base contendo os requisitos solicitados.
2. `constraints.md`: Restrições rígidas do AIW repassadas ao sistema.
3. `plan.md`: Plano simplificado injetado na memória inicial do Agente.

## Offline execution

A execução só acontece manualmente usando:
`./scripts/aiw-agent-queue --workspace <ws> --item aq-... --run-offline --confirm`

Isso aciona o `./scripts/aiw-runner-agent --offline` (ferramenta determinística que testa ferramentas de context index, sem LiteLLM) e monitora a saída nativamente com um timeout estrito usando `subprocess`. 

Os status vão de `ready` -> `running` -> (`completed`|`failed`).

## Cockpit

No Cockpit UI, os itens ganham visibilidade total, podendo ser avançados para `ready` ou removidos da fila (`dismissed`) via formulários estritos, mas em nenhum cenário a interface despacha o script bash.

## Segurança

- Sem **daemon**: os processos só vivem enquanto a CLI estiver sendo executada;
- Sem **cron**: execuções dependem do humano iniciar localmente;
- Sem LLM remoto acionado (proteção inicial, focada no agente de fallback offline);
- Sem auto-apply: O agente no máximo vai criar um patch e deixar parado;
- `.env` é evitado ativamente pelas regras enviadas ao agente e isolamento.

## Limitações

- Execução limitada ao modo **offline** nesta primeira versão.
- A requisição para o Agente (Run Queue) só suporta um item simultâneo, não possuindo workers paralelos (é bloqueante na CLI).
- Sem repetição autônoma (retry) se o agente falhar por timeout.

## Próximo passo recomendado

Finalmente introduzir a **Background Agent Queue v2** acionando o Agent via LiteLLM de verdade (`--run-llm`) usando a CLI manual, deixando que o LiteLLM crie de fato as propostas de patch para os tickets do GitHub importados!
