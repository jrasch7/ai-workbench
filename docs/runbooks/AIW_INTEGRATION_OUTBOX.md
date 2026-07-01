# AIW Integration Outbox

## Resultado

O Integration Outbox serve como a camada final e local antes do AI Workbench enviar qualquer relatório para fora (GitHub, Jira, Slack). Ele retém um payload final, formatado e padronizado, para revisão ou uso assíncrono, mantendo controle restrito sobre o que sai da máquina.

## Outbox items

Cada Outbox Item representa uma mensagem formatada e salva localmente, contendo um estado (`draft`, `ready`, `copied`, `dismissed`). Esses itens guardam os dados de envio (Markdown e metadados JSON) originados de um `Evidence Export`.

## GitHub PR Draft

A v1 introduz o target `github_pr` com o kind `pr_summary`. Essa integração pega o snippet validado e higienizado e encapsula como um corpo de Pull Request (PR) do GitHub, salvando também um comando preview que ensina o revisor (ou um agente em background futuro) a enviá-lo usando CLI (ex.: `gh pr edit`).

## Status local

Permite manter o workflow:
- **draft**: Acabou de ser gerado, pendente de aprovação.
- **ready**: Conferido e autorizado a ser enviado para fora.
- **copied**: O revisor humano informou que copiou para a área de transferência e colou na UI.
- **dismissed**: Arquivado, não serve mais.

Nenhum desses status faz o envio externo por conta própria nesta versão!

## Cockpit

Um item da Integration Outbox é renderizado dentro do Patch Card no AI Workbench Cockpit, incluindo botões para mudar seu estado, visualizar o corpo final (payload.md) e ver o bash comand de preview (command-preview.sh).

## Segurança

- **não** chama GitHub API;
- **não** chama Jira API;
- **não** executa `gh`;
- **não** envia dados externos via POST HTTP ou processos secundários;
- **não** lê `.env`;
- **não** inclui secrets;
- **não** inclui código fonte completo;
- **não** commita no repositório;
- **não** faz push no remoto.

## Limitações

- outbox unicamente local;
- sem envio automático (requer cópia manual ou invocação via CLI posterior);
- sem background worker implementado;
- sem integração remota real.

## Próximo passo recomendado

Implementar um CLI de *Flush* ou Background Worker seguro (ex.: `aiw-outbox-sync`) que fique lendo os items com status `ready` e execute as integrações declaradas usando autenticações via variáveis de ambiente da máquina local, ou conectar isso com um agente Hermes sob escopo explícito.
- [AIW Integration Worker CLI](AIW_INTEGRATION_WORKER_CLI.md)
- [AIW GitHub Intake CLI](AIW_GITHUB_INTAKE_CLI.md)
- [AIW Agent Run Queue](AIW_AGENT_RUN_QUEUE.md)
