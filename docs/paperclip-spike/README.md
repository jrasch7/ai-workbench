# Paperclip Control Plane Spike

## Objetivo

Avaliar o Paperclip como control plane visual para o AI Workbench, mantendo o AIW/Hermes como camada de execução, diagnóstico e integração operacional.

## Estado atual

- Branch: `spike/paperclip-control-plane`
- Paperclip vendorizado em `vendor/paperclip` para replicação via Git
- `.aiw/lab/` permanece fora do Git apenas para clones temporários, caches, bancos e testes locais
- Paperclip local pode rodar em `http://127.0.0.1:3100` via `./scripts/paperclip-dev`
- Onboarding iniciado com organização `Nivela Ecosystem`
- Adapter testado: `Hermes Agent`
- Hermes CLI oficial instalado via `pipx`
- Hermes CLI detectado em `/home/joao/.local/bin/hermes`
- Hermes Agent versão validada: `v0.16.0`
- Paperclip agora encontra o Hermes CLI, mas ainda alerta ausência de modelo/API key

## Decisão de arquitetura

Paperclip não substitui imediatamente o AIW. Ele deve ser tratado como control plane:

- Paperclip: empresa, agentes, tarefas, runs, visualização, governança
- AIW: scripts locais, task queue, doctor, cockpit, approve/reject, run history
- Hermes: execução agentic, gateway, Telegram/progress updates, adapters futuros

## Observação importante

O Hermes Agent do Paperclip é o Hermes Agent oficial da Nous Research, instalado via Python/pipx como CLI `hermes`.

Ele não é a mesma coisa que o Hermes Gateway já existente no AIW.

## Próximos passos

1. Configurar um provider remoto barato/grátis para Hermes neste PC.
2. Priorizar provedores chineses/OAuth quando possível.
3. Não configurar modelos locais neste PC.
4. Replicar o stack local no PC principal para Ollama/vLLM/modelos open-source.
5. Criar adapter ou bridge Paperclip -> AIW quando o control plane estiver validado.
