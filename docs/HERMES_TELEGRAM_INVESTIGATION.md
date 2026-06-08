# Hermes Telegram Investigation

Este documento registra somente fatos confirmados localmente sobre a configuracao futura do Telegram no Hermes.

## Objetivo

Preparar a integracao Telegram do Hermes com seguranca, sem executar configuracao remota ainda e sem inventar campos, tokens, webhooks ou comandos nao confirmados.

## Estado atual

- Hermes esta instalado e funcional no PC `DESKTOP-S2AARAD`.
- Profile ativo: `aiworkbench`.
- Provider atual: OpenRouter.
- Modelo atual: `openai/gpt-oss-120b:free`.
- Telegram ainda nao esta configurado.
- Gateway esta parado.
- Sudo esta desabilitado.
- Git deve permanecer limpo antes e depois de qualquer investigacao.

## Fatos confirmados por help local

### `hermes gateway`

Comando confirmado:

```bash
hermes gateway
```

Subcomandos confirmados por `hermes gateway --help`:

- `run` — rodar gateway em foreground, recomendado para WSL, Docker e Termux.
- `start` — iniciar servico de background instalado.
- `stop` — parar servico gateway.
- `restart` — reiniciar servico gateway.
- `status` — mostrar status do gateway.
- `install` — instalar gateway como servico systemd/launchd.
- `uninstall` — desinstalar servico gateway.
- `list` — listar perfis e status de gateway.
- `setup` — configurar plataformas de mensagem.
- `migrate-legacy` — remover unidades legadas anteriores ao rename.

Opcao confirmada:

- `--accept-hooks` — aprovar shell hooks sem prompt TTY.

### `hermes gateway setup`

Comando confirmado:

```bash
hermes gateway setup
```

O help local confirmou apenas que este subcomando existe para configuracao de plataformas de mensagem.

Nao foram confirmados ainda:

- nomes de campos de config do Telegram;
- local exato onde token Telegram deve ser salvo;
- se usa polling ou webhook;
- se pede chat ID;
- quais permissoes do bot sao necessarias;
- se ha allowlist de usuarios/chats;
- se ha rate limit especifico.

### `hermes gateway status`

Comando confirmado:

```bash
hermes gateway status
```

Opcoes confirmadas:

- `--deep` — checagem profunda de status.
- `--full` ou `-l` — mostrar output completo sem truncar quando suportado.
- `--system` — mirar servico gateway de nivel system.

### `hermes pairing`

Comando confirmado:

```bash
hermes pairing
```

Subcomandos confirmados:

- `list` — mostrar usuarios pendentes e aprovados.
- `approve` — aprovar um codigo de pareamento.
- `revoke` — revogar acesso de usuario.
- `clear-pending` — limpar codigos pendentes.

Este comando parece importante para autorizacao de usuarios remotos, mas ainda nao foi testado.

### `hermes tools disable`

Comando confirmado:

```bash
hermes tools disable
```

Uso confirmado:

```bash
hermes tools disable --platform PLATFORM NAME
```

Fatos confirmados:

- permite desabilitar toolsets por plataforma;
- o default de `--platform` e `cli`;
- aceita nomes de toolsets ou ferramentas MCP.

Ainda precisa investigar quais plataformas sao aceitas para Telegram e qual nome exato da plataforma.

## Hipoteses nao confirmadas

Os itens abaixo nao devem ser usados como instrucao executavel ate verificacao por documentacao oficial, help local, setup real em ambiente controlado ou arquivo de config gerado pelo proprio Hermes:

- `gateway.telegram.*`;
- `telegram.token`;
- `telegram.allowed_chat_ids`;
- `security.redact_secrets`;
- `approvals.mode`;
- `privacy.redact_pii`;
- `BOT_TOKEN`;
- webhook automatico;
- polling;
- intents/permissoes especificas no BotFather;
- rate limit especifico;
- rotação automatica de token.

## Comandos seguros para proxima investigacao

Antes de configurar Telegram, investigar com comandos somente leitura ou prompts controlados:

```bash
hermes gateway --help
```

```bash
hermes gateway setup --help
```

```bash
hermes gateway status --help
```

```bash
hermes gateway list
```

```bash
hermes pairing --help
```

```bash
hermes pairing list
```

```bash
hermes tools list
```

```bash
hermes tools disable --help
```

```bash
hermes status
```

```bash
hermes doctor
```

## Nao executar ainda

Ainda nao executar:

- `hermes gateway setup` com token real;
- `hermes gateway install`;
- `hermes gateway start` como servico persistente;
- qualquer configuracao de Telegram com token real;
- qualquer abertura de acesso remoto;
- qualquer automacao via Telegram;
- qualquer commit/push feito pelo agente.

## Criterios para avancar para configuracao real

Antes de configurar Telegram de verdade:

1. Validar documentacao oficial ou output real do setup.
2. Confirmar onde o token sera armazenado.
3. Confirmar como funciona autorizacao de usuario remoto.
4. Confirmar como restringir acesso ao usuario correto.
5. Confirmar quais tools ficarao habilitadas para Telegram.
6. Desabilitar tools perigosas para a plataforma remota, se aplicavel.
7. Testar primeiro com tarefa sem acesso a repo real.
8. So depois permitir tarefas pequenas em repo, sem commit/push automatico.

## Decisao de plataforma remota

O `hermes gateway setup` confirmou localmente que o Hermes suporta varias plataformas de mensagem, incluindo Telegram e Discord.

Decisao atual:

```text
1. Telegram primeiro — interface pessoal/remota do usuario com Hermes.
2. Discord depois — possivel interface futura para canais, equipe, projetos e logs.
```

Motivo:

- Telegram e mais simples para uso pessoal e remoto pelo celular.
- Telegram permite iniciar com menor superficie operacional.
- Discord fica mais adequado para uma fase posterior com canais por projeto, equipe e observabilidade.

Ainda nao configurar token real nem iniciar gateway persistente antes de validar seguranca, pairing, restricao de usuario e tools permitidas.

## Decisao atual

Telegram e prioridade futura, mas ainda esta bloqueado por investigacao de seguranca.

A proxima etapa deve ser investigar o setup real/documentacao oficial e definir uma configuracao minima segura.
