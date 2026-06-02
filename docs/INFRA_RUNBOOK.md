# Infra Runbook — AI Workbench

Este runbook descreve como operar a infraestrutura local do AI Workbench de forma previsível.

## Objetivo

Garantir que a bancada suba, pare, valide e reinicie sem depender do histórico da conversa.

Este documento é operacional. Ele existe para resolver problemas reais de ambiente, não para explicar a visão do produto.

## Comandos principais

### Diagnóstico geral

Use antes de iniciar uma sessão de trabalho.

```bash
./scripts/aiw doctor
```

O comando valida Docker, Docker daemon, Docker Compose, arquivo .env, LITELLM_MASTER_KEY, OpenHands e LiteLLM quando estiver rodando.

### Subir apenas o gateway LiteLLM

```bash
./scripts/aiw gateway
```

Use quando quiser testar modelos antes de abrir o OpenHands.

### Listar modelos expostos pelo LiteLLM

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


### Testar chat do modelo via LiteLLM

```bash
./scripts/aiw smoke dev-coder
```

Use este comando depois de `gateway` e `models` para validar se o alias realmente responde chat, sem envolver OpenHands.

Resultado esperado:

```text
OK: model smoke passed for dev-coder
```

Se retornar `429`, timeout ou erro de provider, o problema está no modelo/provedor e não necessariamente no OpenHands.
### Testar matriz de modelos via LiteLLM

```bash
./scripts/aiw matrix dev-openrouter-free dev-coder
```

Use este comando para validar mais de um alias de modelo sem envolver OpenHands.

Resultado esperado:

```text
Passed: 2
Failed: 0
```

Se algum alias falhar, a falha deve ser tratada como problema de chave, provider, rate limit, timeout ou roteamento de modelo antes de culpar o agente.

### Abrir workspace isolado

```bash
./scripts/aiw start sandbox-test
```

Use para testes descartáveis.

O workspace fica em:

```text
~/ai-workbench/workspaces/sandbox-test
```

### Abrir o próprio repositório AI Workbench

```bash
./scripts/aiw repo
```

Use para evoluir a própria bancada.

O script prepara conversations, bash_events, exclusão local em .git/info/exclude, limpeza de containers antigos do OpenHands e LiteLLM ativo.

### Abrir o diretório atual como workspace

```bash
./scripts/aiw current
```

Use dentro de projetos reais como Nivela ou SisOpERP Web.

Exemplo:

```bash
cd ~/nivela_app && ~/ai-workbench/scripts/aiw current
```

### Parar tudo

```bash
./scripts/aiw stop
```

Use ao terminar a sessão ou quando um sandbox ficar preso.

### Ver status

```bash
./scripts/aiw status
```

### Ver logs do LiteLLM

```bash
./scripts/aiw logs
```

## Configuração do OpenHands

Na UI do OpenHands, usar:

```text
Modelo personalizado: openai/dev-coder
URL base: http://host.docker.internal:4000
Chave API: valor de LITELLM_MASTER_KEY
```

## Problemas conhecidos

### Sandbox preso em Waiting for sandbox

Causas prováveis:

- container antigo do oh-agent-server;
- permissão em conversations;
- conversa antiga quebrada reaberta pela UI;
- pasta temporária criada como root;
- imagem ou runtime do OpenHands instável.

Correção padrão:

```bash
./scripts/aiw stop
```

Depois iniciar novamente com:

```bash
./scripts/aiw repo
```

### Permission denied em /workspace/conversations

O script atual prepara conversations e bash_events com permissão aberta para o sandbox.

Se acontecer manualmente:

```bash
cd ~/ai-workbench && mkdir -p conversations bash_events && chmod 777 . conversations bash_events
```

### LiteLLM responde depois de alguns segundos

Após subir o container, a primeira chamada pode falhar com connection reset. Isso não significa necessariamente falha de configuração.

Validar com:

```bash
./scripts/aiw doctor
```

Depois:

```bash
./scripts/aiw models
```

### OpenRouter free retorna 429

Modelos gratuitos do OpenRouter dependem de provedores upstream. Podem falhar por limite, lentidão ou indisponibilidade.

Free tier é laboratório, não base de produção.

## Regra operacional

A frase final do agente não é fonte de verdade.

Sempre validar com:

```bash
git status --short
```

```bash
git diff --stat
```

```bash
git diff
```

## Critério de infra pronta

A infra está pronta quando estes comandos passam:

```bash
./scripts/aiw doctor
```

```bash
./scripts/aiw gateway
```

```bash
./scripts/aiw models
```

```bash
./scripts/aiw status
```

E quando ./scripts/aiw repo abre o OpenHands montando o repositório real sem erro de permissão.
