# AIW Tool Runtime Phase 3 Validation

## Resultado

APROVADO COM BLOQUEIO DE INFRA

## Escopo validado

Validação do código implementado na Fase 3 para o Tool Runtime mínimo, incluindo as definições de schemas JSON, scripts em Python para `directory_list`, `file_read`, e `shell_exec` (com as devidas regras de segurança), bem como a criação do Runner Agent `scripts/aiw-runner-agent` empacotado para passar em ferramentas do repositório, e testes e bloqueios obrigatórios associados.

## Arquivos analisados

- `aiw_runtime/schemas.py`
- `aiw_runtime/policy.py`
- `aiw_runtime/tools.py`
- `scripts/aiw-runner-agent`
- `scripts/aiw-tool-smoke`
- `docs/runbooks/AIW_TOOL_RUNTIME_PHASE3.md`
- `AGENTS.md` (Arquivo local importado - não pertence à fase em si).

## Validações executadas

- **Sintaxe**: O teste de `python3 -m py_compile aiw_runtime/*.py` e o `bash -n scripts/...` passaram em tudo sem erros.
- **Smoke das tools (Caminho feliz)**: `directory_list`, `file_read` e `shell_exec` retornaram saídas precisas em JSON. `directory_list` suprimiu as pastas não desejadas (`.git`, `.venv`, etc).
- **Smoke de bloqueios obrigatórios (Caminho triste)**: Todos os testes falharam exatamente como esperado.
- **LiteLLM / Tool calling**: Todos os modelos provados saudáveis via `model-pool-smoke`. Apenas o endpoint usando payload de tools apresentou falha.

## Evidências

### Exemplos de saídas de sucesso
```json
{
  "ok": true,
  "tool": "directory_list",
  "entries": [
    {
      "name": "scripts",
      "type": "dir"
    },
    ...
```

### Exemplos de Bloqueios Reais
```json
{
  "ok": false,
  "tool": "file_read",
  "error": "Acesso a .env bloqueado."
}
```
```json
{
  "ok": false,
  "tool": "shell_exec",
  "error": "Subcomando git mutável bloqueado: push"
}
```
```json
{
  "ok": false,
  "tool": "shell_exec",
  "error": "Comando não autorizado: rm"
}
```

## Segurança

Confirmado com evidências:
- [x] não leu `.env`;
- [x] não alterou `.env`;
- [x] não mexeu em `~/.hermes/config.yaml`;
- [x] não usou OpenHands;
- [x] não integrou Hermes;
- [x] não fez commit;
- [x] não fez push.

## Resultado dos bloqueios

- `.env`: Bloqueado corretamente (`Acesso a .env bloqueado.`)
- path traversal: Bloqueado corretamente (`Escape de diretório bloqueado (..).`)
- git push: Bloqueado corretamente (`Subcomando git mutável bloqueado: push`)
- git add: Bloqueado corretamente (`Subcomando git mutável bloqueado: add`)
- rm: Bloqueado corretamente (`Comando não autorizado: rm`)
- pipe: Bloqueado corretamente (`Operador perigoso bloqueado: |`)
- redirect: Bloqueado corretamente (`Operador perigoso bloqueado: >`)
- bash livre: Bloqueado corretamente (`bash só é permitido com -n`)

## LiteLLM 400 No connected db

Diagnóstico:
Os testes `model-smoke dev-coder`, `model-ask dev-coder`, e `model-pool-smoke` responderam `200 OK` retornando `AIW_MODEL_OK`. As configurações no `litellm.yaml` também estão puras sem indicação de banco. A falha só ocorre ao despachar payloads no formato de "Tool Calling".

Classificação:
Erro específico na feature de Tool Calling do LiteLLM local (proxy/config), não sendo um problema da implementação das ferramentas criadas nesta fase ou do modelo via chat. 

Recomendação:
Verificar a documentação do LiteLLM ou desativar flag de telemetria se aplicável, não requer reversão de código desta rodada.

## AGENTS.md

Classificação:
É um arquivo local contendo `## Imported Claude Cowork project instructions` de origem de plataformas (importação de prompt), não compõe o core do AI Workbench e não traz risco ao projeto.

Recomendação:
Ignorar e manter, podendo ser adicionado ao `.gitignore` no futuro. Não faz parte do escopo de entrega ou revisão.

## Riscos restantes

- O Runner Agent `scripts/aiw-runner-agent` não tem modo "offline/dry-run". Quando formos debugar sem LLM conectada, ele vai parar no erro de rede. Seria útil adicionar um arg `--dry-run` ou test loop.
- O LiteLLM Proxy upstream precisará ser reconfigurado e destravado antes do AIW Cockpit poder acioná-lo de fato, travando a integração visual até essa correção.

## Recomendação final

- **Pode commitar?** Sim, o código do executor atende todos os rígidos requisitos de segurança estipulados no prompt.
- **Precisa voltar ao executor?** Não.
- **Próximo passo recomendado**: Consertar o Proxy LiteLLM (lidar com erro do DB) e adicionar uma flag offline no Agent runner, seguindo depois para a integração com a UI.
