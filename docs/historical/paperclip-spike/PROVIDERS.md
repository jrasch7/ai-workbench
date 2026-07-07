# Provider Strategy — Hermes / Paperclip / AIW

## Preferência estratégica

1. Modelos locais/open-source no PC principal.
2. Provedores chineses grátis/OAuth quando disponíveis.
3. APIs chinesas baratas.
4. APIs pagas tradicionais apenas como fallback.

## Estado do PC atual

Este PC não é o PC principal e não deve ser usado para execução local pesada.

Inventário atual:

- `hermes`: instalado
- `docker`: instalado
- `qwen`: não instalado
- `ollama`: não instalado
- `vllm`: não instalado
- `nvidia-smi`: não disponível

## Candidatos remotos

| Provider | Tipo | Status |
|---|---|---|
| Qwen OAuth | OAuth / possível uso gratuito | Hermes detecta como opção, mas Qwen CLI não está instalado |
| MiniMax OAuth | OAuth | Hermes detecta como opção, precisa validar fluxo |
| Z.AI / GLM | API key | precisa validar cadastro, crédito e custo |
| Kimi / Moonshot | API key | precisa validar cadastro, crédito e custo |
| DeepSeek | API key barata | provável custo por token, não assumir grátis |
| Nous Portal | OAuth | opção integrada ao Hermes, validar limite/custo |

## Candidatos locais para PC principal

| Runtime | Uso |
|---|---|
| Ollama | modelos locais simples e rápidos de testar |
| vLLM | serving local mais profissional |
| Docker + GPU | base para infraestrutura própria |
| Qwen Coder local | candidato principal de coding open-source |
| DeepSeek Coder local | candidato forte para coding, se hardware suportar |
| GLM local | candidato a testar conforme suporte/hardware |

## Regra

Não configurar, instalar ou escolher provider no chute. Cada provider precisa passar por:

1. Evidência de instalação/autenticação.
2. Teste simples de resposta.
3. Teste dentro do Hermes.
4. Teste dentro do Paperclip.
5. Registro do custo/limite conhecido.
