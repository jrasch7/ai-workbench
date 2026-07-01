# AIW End-to-End Dummy PR Smoke

Este runbook documenta o processo automatizado do Smoke Test de Integração e Ciclo de Vida ponta-a-ponta (E2E) local do AI Workbench sem depender de requisições de rede para a API do GitHub ou LLMs, garantindo a segurança do repositório em modo offline.

## Objetivo
O objetivo do Dummy PR Smoke é validar e provar que todas as peças arquiteturais locais construídas se conectam perfeitamente formando o fluxo E2E documentado. O script interliga de maneira dry-run/offline a pipeline que vai de Intake até a Integration Outbox / Worker Loop.

## Pré-requisitos
- Executado localmente dentro de WSL ou ambiente Linux que rode bash e Python 3.
- Variáveis locais da Workspace resolvíveis (default `aiw`).
- As dependências de CLI do GitHub (`gh`) não são ativadas em execução real (o teste faz bypass para gerar instâncias dummies para segurança).

## Comandos seguros
Execute o script em seu terminal:
```bash
./scripts/aiw-e2e-dummy-pr-smoke
```

## Ordem do Fluxo validada pelo Script
1. **Mock Intake**: Um intake dummy `item.json` e o artefato originado (`patch-intent`) são forjados em `integration-inbox`.
2. **Queue Creation**: Utilizando `--from-inbox`, o item é transmutado numa Task pronta dentro do `agent-queue`.
3. **Queue Dispatch Setup**: É injetado e fixado o metadado no diretório da Task usando a flag recém-criada de `--set-dispatch` instruindo execução em modo `--dispatch-mode offline`.
4. **Mark Ready**: Ativa a intenção da task mudando para `ready`.
5. **Agent Dispatcher (Dry-run)**: O `aiw-agent-dispatcher` é acionado para varredura neutra usando `--once --dry-run`.
6. **Agent Dispatcher (Execute)**: O dispatcher varre, enxerga os metadados de Offline, e propaga a execução com restrições e segurança via subprocess para o *Agent Queue CLI*.
7. **Mock Patch & Evidence**: Simula manualmente a saída do *Patch Review Flow*, injetando resumos de *Validation Plan* e um arquivo *pr-summary.md* na camada final, empacotando-os num Export do Evidence.
8. **Integration Outbox**: Um registro na Outbox é preparado consumindo os arquivos simulados acima.
9. **Set Outbox Dispatch**: O preparo da Integração bloqueia envios acidentais e força a injeção do metadado de PR vinculando com modo real.
10. **Mark Outbox Ready**: Prepara final para roteamento.
11. **Worker Loop (Dry-run)**: Finaliza avaliando políticas externas de restrição pelo Worker Loop CLI com modo neutrão varrendo Outbox com item pendente de ação, marcando sucesso de visibilidade e processamento seguro.

## Artifacts gerados
Durante o smoke local offline os artifacts são guardados sob:
`.aiw/workspaces/aiw/integration-inbox/in-dummy{ID}/`
`.aiw/workspaces/aiw/agent-queue/aq-{HASH}/`
`.aiw/workspaces/aiw/agent-dispatcher/runs/adr-{HASH}/`
`.aiw/workspaces/aiw/evidence-exports/patch-dummy{ID}/exp-dummy{ID}/`
`.aiw/workspaces/aiw/integration-outbox/out-{HASH}/`
`.aiw/workspaces/aiw/worker-loop/runs/wlr-{HASH}/`

Não *stagear* estes diretórios. O Git local ignora a pasta raiz `.aiw/`.

## Riscos
Nenhum risco. Como o fluxo é bloqueado, restrito em *offline* e as ferramentas de Intake, LLM e Worker Bypass não alteram nada real (sem permissão de rede) o smoke é 100% seguro.

## Próximos passos
- Conectar o modelo local (LLM sandbox read-only mock) para ler de fato a instrução injetada.
- Adicionar o *GitHub Action E2E* para rodar o smoke script em cada PR para garantia de continuidade.
