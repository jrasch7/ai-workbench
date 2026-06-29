# OpenHands Historical Validation — AI Workbench

Este documento registra validações históricas do OpenHands usando o AI Workbench.

OpenHands está depreciado como caminho operacional. A interface principal do AIW é a bancada própria, o AIW Cockpit, com runner/tool runtime local, LiteLLM e evidências auditáveis. Este arquivo permanece apenas como registro de laboratório e não deve orientar execução diária.

## Validação OpenHands via dev-coder

Ambiente:

```text
PC: DESKTOP-S2AARAD
Modelo no OpenHands: openai/dev-coder
Gateway: LiteLLM
Alias LiteLLM: dev-coder
Provider atual: pool operacional validado via LiteLLM
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
OpenHands -> LiteLLM -> dev-coder -> pool operacional validado funcionando.
```

## Regra operacional atual

Para operar o AIW, validar:

```bash
./scripts/aiw doctor
```

```bash
./scripts/aiw matrix dev-coder dev-review dev-architect
```

Depois iniciar a interface própria:

```bash
./scripts/aiw cockpit
```

OpenHands não deve ser iniciado como caminho operacional.

## Hermes substituindo OpenHands no teste controlado

O teste controlado mostrou alternativas ao OpenHands. A direção atual é Cockpit próprio + runner/tool runtime local; Hermes não deve ser integrado ao runtime/cockpit sem fase específica e controlada.
