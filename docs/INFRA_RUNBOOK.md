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

O comando valida Docker, Docker daemon, Docker Compose, arquivo .env, LITELLM_MASTER_KEY, LiteLLM e os scripts locais quando estiverem disponíveis.

### Subir apenas o gateway LiteLLM

```bash
./scripts/aiw gateway
```

Use quando quiser testar modelos antes de executar tasks pelo Cockpit ou runner.

### Listar modelos expostos pelo LiteLLM

```bash
./scripts/aiw models
```

Aliases esperados:

```text
dev-fast
dev-balanced
dev-large
dev-coder
dev-review
dev-architect
dev-fallback
```


### Alias oficial de código

```bash
./scripts/aiw smoke dev-coder
```

`dev-coder` é o alias operacional para tarefas de código. Atualmente ele está roteado para Hugging Face Router com Kimi Code.

Aliases com nome de provedor, como `dev-gemini-coder` e `dev-openrouter-free`, existem para teste, comparação e laboratório.

### Testar chat do modelo via LiteLLM

```bash
./scripts/aiw smoke dev-coder
```

Use este comando depois de `gateway` e `models` para validar se o alias realmente responde chat, sem envolver a interface.

Resultado esperado:

```text
OK: model smoke passed for dev-coder
```

Se retornar `429`, timeout ou erro de provider, o problema está no modelo/provedor e não necessariamente no Cockpit ou runner.
### Testar matriz de modelos via LiteLLM

```bash
./scripts/model-pool-smoke
```

Use este comando para validar mais de um alias de modelo sem envolver a interface.

Resultado esperado:

```text
Passed: 2
Failed: 0
```

Se algum alias falhar, a falha deve ser tratada como problema de chave, provider, rate limit, timeout ou roteamento de modelo antes de culpar o agente.

### Abrir o AIW Cockpit

```bash
./scripts/aiw cockpit
```

Use para operar a bancada própria em:

```text
http://127.0.0.1:8765
```

### Abrir o próprio repositório AI Workbench

```bash
./scripts/aiw repo
```

Use para evoluir a própria bancada.

Use quando o fluxo exigir workspace local controlado. O caminho principal de operação é o Cockpit/runner; comandos herdados de sandbox devem ser tratados como legado até serem substituídos pelo Tool Runtime próprio.

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

## OpenHands legado

OpenHands não é caminho operacional do AIW. Referências antigas ficam como histórico/laboratório opcional e não devem ser usadas para validar a bancada principal.

## Problemas conhecidos

### Sandbox legado preso em Waiting for sandbox

Causas prováveis:

- container antigo do oh-agent-server;
- permissão em conversations;
- conversa antiga quebrada reaberta pela UI;
- pasta temporária criada como root;
- imagem ou runtime legado instável.

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

E quando `./scripts/aiw cockpit` inicia a interface própria em `127.0.0.1:8765` sem erro.
