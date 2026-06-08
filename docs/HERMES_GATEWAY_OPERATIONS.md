# Hermes Gateway Operations

Este documento explica como operar o Hermes Gateway do AI Workbench no PC `DESKTOP-S2AARAD`.

## Objetivo

Manter o Hermes disponivel via Telegram enquanto o PC/WSL estiver ligado, usando `tmux` em vez de servico systemd.

## Estado atual

- Profile Hermes: `aiworkbench`.
- Plataforma remota inicial: Telegram.
- Discord fica para fase futura.
- Gateway roda em `tmux`.
- Sessao tmux padrao: `hermes-aiw`.
- Script de start: `scripts/hermes-gateway-start`.
- Atalho Windows: `Start Hermes AIW.cmd` na Area de Trabalho.

## Iniciar pelo terminal

```bash
cd ~/ai-workbench && ./scripts/hermes-gateway-start
```

O script e idempotente:

- se o gateway ja estiver rodando, nao duplica;
- se a sessao tmux existir mas o gateway estiver parado, recria a sessao;
- se estiver tudo parado, inicia `hermes gateway run` dentro do tmux.

## Iniciar pelo atalho

Na Area de Trabalho do Windows, clique em:

```text
Start Hermes AIW.cmd
```

Esse atalho abre o WSL, entra em `~/ai-workbench` e executa o script `scripts/hermes-gateway-start`.

## Ver status do gateway

```bash
cd ~/ai-workbench && hermes gateway status --deep
```

Resultado esperado quando estiver rodando:

```text
Gateway is running
```

## Ver sessoes tmux

```bash
tmux ls
```

Resultado esperado:

```text
hermes-aiw
```

## Abrir logs ao vivo

```bash
tmux attach -t hermes-aiw
```

Para sair dos logs sem parar o Hermes:

```text
Ctrl+B depois D
```

## Parar o gateway

Entre na sessao:

```bash
tmux attach -t hermes-aiw
```

Pare com:

```text
Ctrl+C
```

Depois saia do tmux ou feche a sessao.

## Reiniciar o gateway

```bash
cd ~/ai-workbench && ./scripts/hermes-gateway-start
```

Se precisar matar a sessao manualmente:

```bash
tmux kill-session -t hermes-aiw
```

Depois inicie de novo:

```bash
cd ~/ai-workbench && ./scripts/hermes-gateway-start
```

## Regras de seguranca

- Nao usar `sudo hermes gateway install` neste momento.
- Nao instalar gateway como servico systemd ainda.
- Nao expor token Telegram em chat, logs ou Git.
- Nao commitar `.env`.
- Nao permitir commit/push automatico pelo agente.
- Manter `TELEGRAM_ALLOWED_USERS` restrito ao usuario autorizado.
- Validar `git status --short` apos testes reais via Telegram.

## Limitacoes conhecidas

O `tmux` mantem o gateway vivo enquanto a instancia WSL estiver ativa.

Se o Windows ou o WSL reiniciar completamente, clique novamente no atalho `Start Hermes AIW.cmd` para religar o Hermes.

## Validacao rapida

1. Clique no atalho ou rode o script.
2. Verifique status:

```bash
cd ~/ai-workbench && hermes gateway status --deep
```

3. Envie no Telegram:

```text
oi
```

4. Confirme que o Hermes responde.

5. Confira Git:

```bash
cd ~/ai-workbench && git status --short
```
