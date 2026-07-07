# Snapshot AIW — 2026-06-29

## Estado Git

- Branch: `main`
- HEAD: `549e647 feat(aiw): inject context pack into agent runner`
- Remote sync: Sincronizado `main == origin/main` (sem drifts em aberto).

## O que existe hoje

A bancada de desenvolvimento AI Workbench é uma realidade operacional. Não somos mais dependentes de OpenHands ou instâncias externas genéricas. Construímos nosso próprio **AIW Cockpit** e o **Agent Runner**. O sistema roda perfeitamente em Offline/Dry-run mode, tem controle sobre Context Packs auditáveis locais, bloqueia mutações destrutivas indesejadas na file tree e rastreia o uso de tools evidenciando na UI.

## Cockpit

O Cockpit (`scripts/aiw-cockpit`) é um web server python embutido hiper-otimizado e seguro. Ele atende requisições de navegação do projeto, listagem de Workspaces, monitoramento da Inbox de tarefas e possui um **Mission Control / Operational View** e **Search Box**. Ele não requer compilação NPM ou dependências extras, operando fluidamente com requisições JSON.

## Agent Runner

O script de runner (`scripts/aiw-runner-agent`) lida com as Tasks. Funciona plugado no gateway do LiteLLM (`AIW_LLM_ENABLED=1`) para iterações com modelos state-of-the-art ou em modo `--offline`. Em modo offline, simula iterações e a estrutura do projeto sem gasto computacional. Recebe injeções de contextos locais (`AIW_USE_CONTEXT_PACK=1`) como prepends no prompt. 

## Tool Runtime

Motor estrito e isolado (em `aiw_runtime`). Funções base disponíveis:
- `directory_list` e `file_read`: Leitura de read-only do ambiente.
- `shell_exec`: Roda binários/comandos desde que não seja blacklisted (como `git push` ou comandos de fuga).
- `file_write` e `file_patch`: Bloqueio contra diretórios de runtime (`.aiw`), ocultos e paths acima da raiz (`../`).

## File OS / Patch Flow

As mutações via agente em código legado são engessadas para máxima segurança via:
1. `project_patch_preview`: O agente envia o diff pretendido. Retorna ID e cria cache.
2. *Cockpit Handoff*: O usuário enxerga o código proposto na Interface.
3. `project_patch_apply`: Acionado via UI. Aplica o patch no sistema e faz Backup auto (rollback ready).
4. `project_patch_rollback`: Retorna perfeitamente ao estado original se corrompido.

## Context Pack

Camada lexica (`aiw_context/indexer.py`).
1. Lê o diretório de documentações e runbooks sem encostar em `.env` ou chaves privadas.
2. Substitui patterns de secrets achados e trunca descrições brutas.
3. Grava um snapshot sob `.aiw/context/context-pack.json` indexando tudo.
4. O frontend consome ele e o runner extrai snippets para injeções rápidas on-the-fly (`best_effort_rebuild`).

## Segurança

- Arquivo `.env` 100% blindado contra reads, patches e shell calls.
- Segredos (`LITELLM_MASTER_KEY`) isolados do parser do agente.
- O agente atua sob guardrails e aprovações interativas, com rollback instantâneo de arquivo.

## Runbooks importantes

O manual operacional agora mora em `docs/runbooks/README.md` catalogado em categorias (Cockpit, Runtime, Arquitetura). Consulte-os para estender endpoints, mexer no parser de markdown ou ajustar regras de Tooling.

## Como continuar em outro chat

Forneça esse arquivo como contexto primário para o novo LLM ou injete sua leitura. Você está com a fundação pronta e a arquitetura inteira está selada contra mutações não controladas. Foque nos próximos passos ou execute tasks através da própria UI em `http://localhost:4000`.

## Próximos passos recomendados

1. **RAG assistido:** O Context Pack hoje só faz prefix manual de textos; o próximo passo é melhorar a rankeação local lexical sem precisar de bancos vetoriais.
2. **Workers hiperespecializados:** Evoluir as capabilities de `dev-architect` via multi-turn roles.
3. **Multi-Project Workspace:** Deixar a ferramenta pronta para lidar não só com pastas avulsas mas workflows corporativos reais baseados em repos dependentes.
