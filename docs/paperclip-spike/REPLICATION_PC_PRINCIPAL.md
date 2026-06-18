# Replicação no PC Principal

## Objetivo

Levar o spike Paperclip + Hermes + AIW para o PC principal, onde será possível testar modelos locais.

## O que deve ir para o Git

- Documentação do spike
- Scripts de bootstrap
- Scripts de verificação
- Plano de integração
- Configurações template sem segredo

## O que não deve ir para o Git

- `.aiw/lab/paperclip`
- `.env`
- `~/.hermes/.env`
- Tokens
- API keys
- Banco local do Paperclip
- Logs com segredo

## Checklist futuro no PC principal

1. Clonar/puxar `ai-workbench`.
2. Instalar Node/pnpm conforme versão do AIW/Paperclip.
3. Instalar Hermes Agent via pipx.
4. Subir Paperclip local.
5. Instalar runtime local: Ollama ou vLLM.
6. Baixar primeiro modelo open-source de coding.
7. Configurar Hermes para provider local.
8. Testar Hermes direto.
9. Testar Paperclip -> Hermes.
10. Criar primeiro adapter Paperclip -> AIW.
