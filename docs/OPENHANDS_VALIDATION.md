# OpenHands Validation — AI Workbench

Este documento registra validações reais do OpenHands usando o AI Workbench.

## Validação Gemini via dev-coder

Ambiente:

```text
PC: DESKTOP-S2AARAD
Modelo no OpenHands: openai/dev-coder
Gateway: LiteLLM
Alias LiteLLM: dev-coder
Provider atual: Gemini
```

Validação executada:

```text
Criar arquivo OPENHANDS_GEMINI_OK.md no workspace.
```

Resultado:

```text
Arquivo criado com sucesso pelo OpenHands.
Arquivo removido após validação.
git status --short limpo.
```

Conclusão:

```text
OpenHands -> LiteLLM -> dev-coder -> Gemini funcionando.
```

## Regra operacional

Antes de usar OpenHands em projeto real, validar:

```bash
./scripts/aiw doctor
```

```bash
./scripts/aiw matrix dev-coder dev-review dev-architect
```

Depois iniciar:

```bash
./scripts/aiw repo
```

Na UI do OpenHands, usar:

```text
Model: openai/dev-coder
Base URL: http://host.docker.internal:4000
API Key: LITELLM_MASTER_KEY local
```
