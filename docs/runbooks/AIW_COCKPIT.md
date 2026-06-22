# AIW Cockpit Runbook

## Como iniciar

```bash
cd /home/joao/ai-workbench
# opcional: ajuste a porta via env var AIW_COCKPIT_PORT (default 8766)
python3 scripts/aiw-cockpit
```

O servidor será iniciado em `http://127.0.0.1:8766` e bind apenas em `127.0.0.1`.

## URL local

- **Cockpit UI**: `http://127.0.0.1:8766/`
- **API status**: `http://127.0.0.1:8766/api/status`
- **API runs**: `http://127.0.0.1:8766/api/runs`

## Como executar missão

1. Abra a UI no navegador.
2. No painel **Nova task** preencha a *texto da missão* e escolha o modelo (padrão `dev-gemini-fast`).
3. Clique **Criar e executar com IA** ou **Salvar na inbox**.
4. A missão aparecerá na **Inbox**; use o botão **Executar** para rodar imediatamente.

## Onde ficam logs

- Tasks são salvas em `~/.aiw/tasks/…` (ignoradas pelo .gitignore).
- Runs são gerados em `~/.aiw/runs/<timestamp>/`.
- Logs de cada run (`summary.md`, `validation.log`, `commands.log`, etc.) são mostrados na página de detalhe (`/run?path=.aiw/runs/...`).

## Limitações do MVP

- UI simples, sem autenticação.
- Apenas modelo configurado; não há suporte a múltiplas filas avançadas.
- Não persiste configuração de UI entre sessões.

## Próximos passos para virar "Devin-like"

1. **Autenticação** – integrar com o mecanismo de identidade do AIW.
2. **WebSocket / Live updates** – substituir o refresh a cada 10 s por push de eventos.
3. **Editor avançado** – permitir edição inline de tarefas.
4. **Persistência de UI** – guardar layout, filtros e preferências.
5. **Deploy opcional** – empacotar como contêiner Docker para acesso remoto seguro.
