# AIW Remote Agent Control Plane

## 1. Decisão
A orquestração principal dos agentes do AIW deve migrar do Telegram para um cockpit dedicado de agentes.

### Decisão inicial
- Mattermost como cockpit conversacional self‑hosted.
- Tailscale como camada de acesso privado entre celular e PC/servidor.
- Telegram permanece apenas como fallback/notificação curta.

## 2. Problema com Telegram
- Truncamento de respostas longas.
- Baixa confiabilidade como canal principal.
- Dificuldade para fluxos longos.
- Risco de processo operacional quebrar por limite de mensagem.

## 3. Objetivo real
João quer orquestrar agentes pelo celular, não editar código. O cockpit deve permitir:
- conversar com agentes;
- enviar tarefas;
- acompanhar status;
- aprovar/bloquear;
- consultar logs resumidos;
- receber alertas;
- acionar runner 24/7.

## 4. Arquitetura alvo
Fluxo: Celular → Mattermost → aiw‑bot → AIW Gateway → Task Queue → Runner 24/7 → Logs/Evidence → Resumo no Mattermost.

## 5. Canais Mattermost sugeridos
- #aiw-control
- #aiw-alerts
- #aiw-runs
- #aiw-review
- #aiw-cyber-bench
- #aiw-rnd

## 6. Comandos desejados
/aiw status
/aiw task
/aiw runs
/aiw approve
/aiw block
/aiw snapshot
/aiw budget
/aiw queue

## 7. Regras de resposta
Mattermost também não deve receber logs gigantes por padrão.
Formato padrão de resposta:
```
Status:
Task ID:
Agente:
Arquivos:
Validações:
Log:
Próxima ação:
```

## 8. Papel do Tailscale
Tailscale permite acesso privado e seguro do celular ao cockpit/serviços locais, sem expor AIW publicamente.

## 9. Relação com AIW-A1
Esta decisão é pré‑requisito para AIW-A1 — Autonomous Agents 24/7 Foundation.

## 10. MVP proposto
- Instalar Tailscale no PC e celular.
- Subir Mattermost local.
- Criar canal #aiw-control.
- Criar bot aiw‑bot.
- Criar webhook/gateway local mínimo.
- Implementar `/aiw status`.
- Implementar `/aiw task` para criar arquivo em .aiw/tasks/inbox.
- Runner L0/L1 lê a fila e registra logs em .aiw/runs.
- Mattermost recebe resumo curto.

## 11. Critérios de sucesso
- João consegue mandar tarefa pelo celular.
- O agente executa sem resposta truncada.
- Logs completos ficam em arquivo.
- Mattermost recebe só resumo.
- Nenhum commit/push automático no MVP.
- Aprovações sensíveis continuam exigindo João.
