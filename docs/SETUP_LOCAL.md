# Setup Local — AI Workbench

Este guia descreve como subir o AI Workbench em um novo ambiente local.

## Pré-requisitos

- Windows com WSL2 habilitado.
- Ubuntu rodando em WSL2.
- Git configurado com acesso ao GitHub.
- Docker Engine instalado dentro do Ubuntu.
- `uv` instalado.
- Python 3 disponível para os scripts locais.

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

## Subir o AIW Cockpit

```bash
./scripts/aiw cockpit
```

A interface própria do AIW deve abrir em:

```text
http://127.0.0.1:8765
```

O Cockpit é o caminho operacional principal para criar tasks, acompanhar runs, revisar evidências e evoluir a bancada própria.

## Fluxo validado

```text
AIW Cockpit / scripts → task local → AIW runner → LiteLLM `dev-coder` → run com evidências
```

## OpenHands

OpenHands fica depreciado neste fluxo. Pode permanecer como laboratório histórico ou comparação pontual, mas não é requisito de setup local e não deve ser usado como caminho operacional do AIW.

## Observações importantes

- Histórico: OpenRouter permanece disponível como provider de laboratório/fallback, mas não é o backbone operacional atual.
- O adapter direto `openrouter/...` no LiteLLM apresentou instabilidade/reset de conexão neste ambiente.
- Modelos grátis/laboratório podem retornar `429` por limite upstream.
- Free tier serve para validar a arquitetura, mas não deve ser tratado como base confiável para produção.
- Para uso sério, o projeto deve evoluir para fallbacks de modelos/provedores e pelo menos um agregador confiável com crédito.
