# AIW Cockpit Runbook

## Como iniciar

```bash
cd ~/ai-workbench
./scripts/aiw-cockpit
```

O servidor será iniciado em `http://127.0.0.1:8765` e bind apenas em `127.0.0.1`.

## URL local

- **Cockpit UI**: `http://127.0.0.1:8765/`
- **API status**: `http://127.0.0.1:8765/api/status`
- **API runs**: `http://127.0.0.1:8765/api/runs`

## Como executar missão

1. Abra a UI no navegador.
2. No painel **Nova task** preencha o **Título** e a **Missão** (texto livre, apenas leitura).
3. Clique **Executar missão**.
4. A missão aparecerá na lista de runs com status `queued → running → succeeded/failed`.

## Onde ficam os arquivos

- Tasks: `reports/aiw-cockpit/tasks/`
- Runs (metadata, logs, etc.): `reports/aiw-cockpit/runs/`

## Limitações do MVP

- UI simples, sem autenticação.
- Apenas modelo configurado; não há suporte a múltiplas filas avançadas.
- Não persiste configuração de UI entre sessões.

## Próximos passos

1. Autenticação – integrar com o mecanismo de identidade do AIW.
2. WebSocket / Live updates – substituir o refresh a cada 10 s por push de eventos.
3. Editor avançado – permitir edição inline de tarefas.
4. Persistência de UI – guardar layout, filtros e preferências.
5. Deploy opcional – empacotar como contêiner Docker para acesso remoto seguro.
