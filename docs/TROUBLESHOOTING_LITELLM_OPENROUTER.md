# Troubleshooting — LiteLLM e OpenRouter

Este documento registra problemas encontrados ao integrar LiteLLM, OpenRouter e OpenHands no AI Workbench.

## 1. OpenRouter direto funciona, mas LiteLLM reseta conexão

Sintoma:

```text
curl: (56) Recv failure: Connection reset by peer
```

Diagnóstico feito:

- Docker estava funcionando.
- LiteLLM estava em execução.
- `/v1/models` respondia normalmente.
- OpenRouter direto respondia usando `https://openrouter.ai/api/v1/chat/completions`.
- LiteLLM resetava conexão usando configurações com `openrouter/...`.

Solução aplicada:

Usar OpenRouter como endpoint OpenAI-compatible no `config/litellm.yaml`:

```yaml
- model_name: dev-coder
  litellm_params:
    model: openai/openai/gpt-oss-120b:free
    api_base: https://openrouter.ai/api/v1
    api_key: os.environ/OPENROUTER_API_KEY
```

O OpenHands deve continuar usando:

```text
openai/dev-coder
```

## 2. OpenRouter free retorna 429

Sintoma:

```text
Provider returned error
code: 429
is temporarily rate-limited upstream
```

Causa:

Modelos grátis do OpenRouter dependem de provedores upstream. Eles podem ficar saturados, retornar `429`, ou trocar de provider conforme disponibilidade.

Impacto:

- O ambiente local pode estar correto e ainda assim o modelo grátis falhar.
- O erro pode variar entre modelos como Kimi, Qwen, Llama, GPT-OSS, GLM ou outros.

Solução temporária:

- Testar outro modelo grátis.
- Aguardar alguns minutos.
- Usar `openrouter/free` diretamente apenas para diagnóstico.

Solução séria futura:

- Configurar fallback no LiteLLM.
- Usar um agregador confiável com pequeno crédito.
- Separar aliases por finalidade: `dev-fast`, `dev-coder`, `dev-review`, `dev-premium`.

## 3. OpenHands usa o modelo errado

Sintoma:

A UI mostra outro modelo no topo, por exemplo:

```text
gpt-5.5
```

Correção:

Na configuração da UI do OpenHands:

```text
Modelo personalizado: openai/dev-coder
URL base: http://host.docker.internal:4000
Chave API: valor de LITELLM_MASTER_KEY
```

## 4. Sandbox não cria arquivos no workspace

Sintoma:

```text
PermissionError: [Errno 13] Permission denied: /workspace/conversations
```

Correção aplicada em workspaces descartáveis:

```bash
cd ~/ai-workbench/workspaces/sandbox-test && mkdir -p conversations project bash_events && chmod -R a+rwX . && chmod 777 . conversations project bash_events
```

## 5. Porta presa por sandbox antigo

Sintoma:

```text
Bind for 0.0.0.0:<porta> failed: port is already allocated
```

Correção:

```bash
cd ~/ai-workbench && ./scripts/aiw stop
```

Se necessário:

```bash
docker rm -f openhands-app 2>/dev/null || true
```

```bash
docker rm -f $(docker ps -aq --filter name=oh-agent-server) 2>/dev/null || true
```

## 6. Validar gateway LiteLLM

```bash
cd ~/ai-workbench && ./scripts/aiw models
```

Teste de chat:

```bash
cd ~/ai-workbench && bash -lc 'set -a; source .env; set +a; curl --max-time 90 -sS http://localhost:4000/v1/chat/completions -H "Authorization: Bearer $LITELLM_MASTER_KEY" -H "Content-Type: application/json" --data-binary @/tmp/aiw-test.json | python3 -m json.tool'
```

Resposta esperada:

```text
AI Workbench OK
```

## 7. Parar tudo

```bash
cd ~/ai-workbench && ./scripts/aiw stop
```
