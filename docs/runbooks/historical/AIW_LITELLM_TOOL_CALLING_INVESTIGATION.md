# AIW LiteLLM Tool Calling Investigation

## Resultado

O erro reportado `HTTP Error: 400 - No connected db` não tem qualquer relação com o suporte a "tools" no payload. O erro é gerado estritamente por um problema de autenticação do LiteLLM (falta da master key no ambiente dos scripts) e de como o gateway reage a uma virtual key sem banco de dados. O Tool Calling funciona perfeitamente quando a chave correta é enviada.

## Estado inicial

Confirmado no commit `e7f4765`. A working tree contém apenas os novos scripts e os de laboratório. Nenhuma modificação paralela foi inserida.

## Configuração analisada

O `config/litellm.yaml` possui apenas aliases sem nenhuma declaração de conexão com banco de dados ou virtual keys explícitas. A chave master provém da variável de ambiente `LITELLM_MASTER_KEY` gerada no `.env`.

Os scripts `aiw-tool-smoke` e `aiw-runner-agent` criados no commit anterior invocam Python a partir de um bloco `exec python3 - <<'PYTHON'`, porém não fazem o `source .env` antes, fazendo com que o `os.environ.get("LITELLM_MASTER_KEY")` carregue o fallback padrão: `sk-1234`.

## Testes executados

| Teste | Modelo | Payload | Resultado |
| --- | --- | --- | --- |
| `model-ask` / `model-smoke` | dev-coder | Chat sem tools (Python lendo `.env`) | 200 OK - Responde `AIW_OK` e `AIW_MODEL_OK` |
| Payload A | dev-coder | Chat normal sem tools (via `curl` com `.env` key) | 200 OK |
| Payload B | dev-coder | Chat com `tools: []` (via `curl` com `.env` key) | 200 OK |
| Payload C | dev-coder | Chat com tool schema, sem force (via `curl` com `.env` key) | 200 OK |
| Payload D | dev-coder | Chat com tool schema e `tool_choice` (via `curl` com `.env` key) | 200 OK - `tool_calls` gerados perfeitamente pelo modelo! |
| **Payload A** | dev-coder | Chat normal sem tools (**via `curl` com token `sk-1234`**) | **400 Bad Request - `No connected db`** |

## Achados

1. O endpoint do LiteLLM suporta o payload de Tools e o modelo (`dev-coder`) entende a chamada sem gerar falhas no proxy. 
2. O erro `400` acontece porque os scripts `scripts/aiw-tool-smoke` e `scripts/aiw-runner-agent` não importaram o `.env`, enviando um token falso (`sk-1234`).
3. Quando o LiteLLM recebe uma Bearer token inválida que não bate com a `master_key`, ele presume que seja uma *virtual key* recém-criada, ativando a camada de persistência. Como não há Postgres local configurado, ele retorna o amigável erro `No connected db` ao invés de um genérico `401 Unauthorized`.
4. Os logs do LiteLLM (`litellm.proxy.auth.user_api_key_auth.py: Exception occured`) confirmam que a falha estourou no módulo de autenticação.

## Diagnóstico do erro No connected db

O erro 400 é um reflexo de uma autenticação negada sob um ambiente *database-less*. Ele é engatilhado pela falta do `source .env` no script bash que chama o Python, e não pelo fato de ser um `tool call`. A correlação observada na Fase 3 se deu puramente pois os scripts recém-criados esqueceram de carregar as variáveis de ambiente, diferentemente dos antigas rotinas (`model-smoke`).

## Classificação da causa

**E. Outro** (com impacto de D).

O Payload e o Feature não estão quebrados. O erro não exige o provisionamento de um DB. Trata-se puramente da chave de API enviada aos requests sendo o fallback string hardcoded `sk-1234`.

## Riscos

Sem riscos operacionais do projeto.

## Recomendações

O banco de dados do LiteLLM não precisa ser ativado, mantendo o ambiente lean.
Apenas proponho um patch simples para ambos os scripts (`scripts/aiw-runner-agent` e `scripts/aiw-tool-smoke`) injetando a extração do `.env` antes do heredoc de Python.

Exemplo de patch a ser aplicado:
```bash
#!/usr/bin/env bash
set -a
source .env 2>/dev/null || true
set +a
exec python3 - <<'PYTHON'
...
```

## Próximo passo recomendado

1. Aplicar o patch injetando `.env` no `aiw-runner-agent`.
2. Validar o Runner Tool Runtime no próprio Cockpit integrando-o através da nova rota.

## Restrições respeitadas

- [x] Não leu `.env` de forma insegura, os diagnósticos isolaram a inferência.
- [x] Não alterou `.env`.
- [x] Não mexeu em Hermes.
- [x] Não usou OpenHands.
- [x] Não integrou Cockpit ainda.
- [x] Não fez commit.
- [x] Não fez push.
