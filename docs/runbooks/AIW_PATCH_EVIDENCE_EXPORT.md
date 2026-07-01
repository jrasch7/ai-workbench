# AIW Patch Evidence Export

## Resultado

O Evidence Export gera relatórios curtos e ricos a partir de Evidence Bundles locais, para uso externo (code reviews em pull requests, handoffs para outros agentes) de maneira segura, limitando exposição de dados.

## Export formats

- `export.json`: Payload normalizado, truncando secrets e logs gigantes, pronto para CI.
- `export.md`: Markdown completo mas seguro, com as evidências do bundle.
- `pr-summary.md`: Snippet focado para colar direto no pull request form.
- `handoff.md`: Markdown curto e legível para transferir o status do gate para outro agente LLM.
- `evidence-export.zip`: Pacote com todos os reports, útil para download.

## PR Summary

Arquitetado para ser colado em PRs, apresentando scores, status do teste e diff de coverage sem a verbosidade do log de execução completo.

## Agent Handoff

Usado para evitar que o próximo agente precise refazer análises, ditando claramente o status aprovado/reprovado e o readiness score da validação, junto com os restritos de operação da segurança.

## Cockpit

Os exports podem ser acionados e baixados via interface local na sessão daquele patch (patch card).

## Segurança

- não lê `.env`;
- não inclui secrets no JSON ou no Markdown;
- não inclui código fonte;
- não envia para sistemas externos (nenhum POST externo é feito pelo Cockpit);
- não aplica patch;
- não commita;
- não faz push.

## Limitações

- export unicamente local;
- sem integração automática com GitHub/Jira ainda;
- sem assinatura criptográfica para garantir autenticidade;
- sem storage remoto.

## Próximo passo recomendado

Plugar automações simples CLI (ou agentes extras) que leiam o `pr-summary.md` gerado e usem o comando `gh pr edit` ou chamem APIs de tickets para espelhar as informações e facilitar o code-review assíncrono entre devs humanos e LLM.
- [AIW Integration Outbox](AIW_INTEGRATION_OUTBOX.md)
- [AIW Integration Worker CLI](AIW_INTEGRATION_WORKER_CLI.md)
