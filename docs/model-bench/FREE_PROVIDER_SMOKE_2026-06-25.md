# AIW Free Provider Smoke — 2026-06-25

## Resultado

### Usável agora

| Provider | Endpoint/modelo | Resultado |
| --- | --- | --- |
| NVIDIA | nvidia/llama-3.3-nemotron-super-49b-v1 | OK — respondeu AIW_PROVIDER_SMOKE_OK |
| Hugging Face Router | moonshotai/Kimi-K2.7-Code | OK — respondeu AIW_HF_SMOKE_OK |
| Hugging Face Router | MiniMaxAI/MiniMax-M3 | OK — respondeu AIW_HF_SMOKE_OK |
| Hugging Face Router | deepseek-ai/DeepSeek-V4-Pro | OK — respondeu AIW_HF_SMOKE_OK |

### Não usável agora

| Provider | Resultado | Motivo |
| --- | --- | --- |
| OpenRouter free | BLOCKED | free-models-per-day zerado |
| Kimi direto | BLOCKED | conta sem saldo/quota |
| Z.AI direto | BLOCKED | sem saldo/resource package |
| Cerebras | BLOCKED | HTTP 403 error code 1010 |
| Groq | BLOCKED | HTTP 403 error code 1010 |
| Hugging Face Router / zai-org/GLM-5.2 | BAD_OUTPUT | HTTP OK, mas conteúdo vazio e finish='length' |

## Pool inicial recomendado

1. NVIDIA como primeiro provider externo fora do OpenRouter.
2. Hugging Face Router com Kimi-K2.7-Code como candidato forte para coding.
3. Hugging Face Router com DeepSeek-V4-Pro como candidato de raciocínio/código.
4. Hugging Face Router com MiniMax-M3 como fallback.
5. OpenRouter free apenas como fallback eventual, não backbone.

## Observação

GLM-5.2 continua relevante para benchmark, mas neste smoke via Hugging Face Router retornou conteúdo vazio. Não deve ser default sem ajuste/teste adicional.
