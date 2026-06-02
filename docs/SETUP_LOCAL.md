# Setup Local — AI Workbench

Este guia descreve como subir o AI Workbench em um novo ambiente local.

## Pré-requisitos

- Windows com WSL2 habilitado.
- Ubuntu rodando em WSL2.
- Git configurado com acesso ao GitHub.
- Docker Engine instalado dentro do Ubuntu.
- `uv` instalado.
- OpenHands instalado via `uv tool install openhands --python 3.12`.

## Clonar o repositório

```bash
git clone git@github.com:jrasch7/ai-workbench.git
```

```bash
cd ~/ai-workbench
```

## Criar o arquivo local de ambiente

```bash
cp .env.example .env
```

Edite o `.env` e preencha as chaves necessárias. O arquivo `.env` nunca deve ser commitado.

Variáveis principais:

```text
LITELLM_MASTER_KEY=chave local usada para acessar o gateway LiteLLM
OPENROUTER_API_KEY=
GROQ_API_KEY=
```

## Subir o gateway LiteLLM

```bash
./scripts/aiw gateway
```

O LiteLLM deve ficar disponível em:

```text
http://localhost:4000
```

A UI do LiteLLM, quando disponível, fica em:

```text
http://localhost:4000/ui
```

## Validar modelos expostos pelo LiteLLM

```bash
./scripts/aiw models
```

Aliases esperados:

```text
dev-fast
dev-balanced
dev-large
dev-openrouter-free
dev-coder
```

## Subir o OpenHands

```bash
./scripts/aiw start sandbox-test
```

A UI do OpenHands deve abrir em:

```text
http://127.0.0.1:3000
```

## Configuração do modelo no OpenHands

Na UI do OpenHands, use:

```text
Modelo personalizado: openai/dev-coder
URL base: http://host.docker.internal:4000
Chave API: valor de LITELLM_MASTER_KEY
```

O LiteLLM expõe o alias interno `dev-coder`. O OpenHands usa `openai/dev-coder` porque se conecta ao LiteLLM como endpoint OpenAI-compatible.

## Fluxo validado

```text
OpenHands GUI → LiteLLM local → OpenRouter → sandbox Docker → arquivo criado no workspace
```

## Observações importantes

- O OpenRouter funcionou melhor via `api_base: https://openrouter.ai/api/v1` usando provider OpenAI-compatible.
- O adapter direto `openrouter/...` no LiteLLM apresentou instabilidade/reset de conexão neste ambiente.
- Modelos grátis do OpenRouter podem retornar `429` por limite upstream.
- Free tier serve para validar a arquitetura, mas não deve ser tratado como base confiável para produção.
- Para uso sério, o projeto deve evoluir para fallbacks de modelos/provedores e pelo menos um agregador confiável com crédito.
