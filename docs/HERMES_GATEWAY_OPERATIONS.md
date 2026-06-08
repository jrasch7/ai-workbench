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

## Padrao de progresso pelo Telegram

Durante tarefas com multiplas etapas, o Hermes deve enviar mensagens curtas de progresso, para evitar que o usuario fique sem retorno enquanto o agente trabalha.

Exemplos esperados:

```text
Status: verificando diretorio e Git.
Status: inspecionando configuracao, sem alterar arquivos.
Status: validacao concluida, preparando handoff.
```

Esse comportamento deve ser mantido especialmente em tarefas de Git, validacao, debug, planejamento, alteracao de arquivos e execucao via terminal.

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

## Operational Reliability and Telegram Task Health

### 1. Typing não conta
- O indicador de typing no Telegram não conta como progress update.
- Progress update precisa ser mensagem textual curta, por exemplo:
  `PROGRESS 1/N — Iniciando tarefa e confirmando escopo.`

### 2. Quando considerar a tarefa travada
- Se não houver typing e não houver progress update por vários minutos.
- Se o agente parar em `PROGRESS 1/N` ou `PROGRESS 2/N` sem handoff.
- Se o tmux mostrar erro de tool loop, `repeated_exact_fail`, erro de `read_file`/`write_file` ou interrupção de API.
- Se o agente imprimir comandos sem saída real e não entregar handoff.

### 3. Como diagnosticar o gateway
```
bash
# Listar sessões tmux
 tmux ls
# Capturar últimos 120 linhas dos logs da sessão hermes-aiw
 tmux capture-pane -t hermes-aiw -p -S -120 | tail -120
# Verificar status do repositório
 cd /home/joao/ai-workbench && git status --short
```

### 4. Como interpretar erros comuns
- **Unrepairable tool_call arguments for write_file** – indica falha de chamada de ferramenta que requer correção antes de prosseguir.
- **Tool read_file returned error** – falha ao ler arquivo, pode ser caminho errado ou permissões.
- **repeated_exact_fail** – loop de falha exata, geralmente indica bug no agente.
- **Interrupted during API call** – interrupção externa, pode ser rede ou limites de API.
- **Telegram fallback IP warnings** – avisos de fallback de IP, normalmente não bloqueantes.
- **Auxiliary Nous unavailable** – serviço auxiliares indisponível, pode degradar funcionalidades mas não impede operação básica.

> Warnings de Nous/Telegram fallback podem não ser bloqueantes, mas `read_file`/`write_file`/`repeated_exact_fail` são sinais de falha operacional.

### 5. Quando reiniciar
- Reiniciar gateway quando a sessão tmux está viva, mas o agente parou sem handoff.
- Reiniciar depois de atualizar `SOUL.md` ou regras do profile.
- Não reiniciar no meio de tarefa com alterações não revisadas sem antes checar `git status`.

### 6. Checklist pós-restart
- Confirmar tmux ativo.
- Enviar teste simples pelo Telegram.
- Confirmar diretório padrão `/home/joao/ai-workbench`.
- Confirmar que o agente não diz que repo não existe antes de checar o diretório certo.
- Confirmar que progress update textual aparece em tarefa controlada.

### 7. Estados finais obrigatórios
Toda tarefa via Telegram deve terminar com um dos seguintes estados:
- `DONE`
- `NEEDS_REVIEW`
- `BLOCKED`
- `NO_CHANGES`

### 8. Regra de evidência
Sem evidência, não aconteceu.

### 9. Cautela atual
Telegram ainda deve ser tratado com cautela para tarefas de edição até passar em teste de continuidade, progress updates e handoff com evidência.
