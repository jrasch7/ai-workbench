# AIW Development Guides

These guides explain how to extend the platform according to the target architecture.

**Para uso real de desenvolvimento hoje (não extensão):** veja a seção "Como usar o AIW para desenvolvimento real hoje" no README.md raiz. O fluxo principal é via **Cockpit** → formulário do **Loop Iterativo do Agente** (escolha de **Perfil de Agente**, modelo OpenRouter, submit com Execução Real, veja `execution_trace` + Preview de Alterações + botão "Aplicar patch seguro" com feedback inline).

Refatorações precisas suportadas: o planner instrui `file_read` + emissão de `old_text`/`new_text` exatos. Smoke de regressão cobre o fluxo completo editar → preview → apply → validate.

## Provider Guides
- [Adding a Model Provider](adding-model-provider.md)
- [Adding an Execution Provider](adding-execution-provider.md)
- [Adding a Context Provider](adding-context-provider.md)

## Other
- [Creating an Agent Profile](adding-agent-profile.md) — perfis dirigem o Loop Iterativo do Agente, roteamento e Provedor de Execução.
- [Model Router & AUTO Mode](model-router.md)
- [Contributing to the Experiment Lab](experiment-lab.md)
- [Cockpit Interfaces](cockpit-interfaces.md) — consumo de interfaces + fluxo do Loop via UI.
