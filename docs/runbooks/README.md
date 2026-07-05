# AIW Runbooks Index

Este diretório contém os guias operacionais (Runbooks) documentando as peças, integrações e fluxos vitais do AI Workbench. 

## Cockpit (Interface & Orquestração)
- **[Cockpit Navigation & Search](AIW_COCKPIT_NAVIGATION_SEARCH.md)**: Como funciona a mecânica local de rotas, cache e pesquisa lexical.
- **[Cockpit Operational View](AIW_COCKPIT_OPERATIONAL_VIEW.md)**: Documentação sobre o dashboard principal Mission Control e gerenciamento visual da fila de tasks.
- **[Cockpit Tool Evidence Console](AIW_COCKPIT_TOOL_EVIDENCE_CONSOLE.md)**: Especificação sobre os blocos visuais de auditoria individual de ferramentas utilizadas.
- **[Cockpit Execution Harness](AIW_COCKPIT_EXECUTION_HARNESS.md)**: O mecanismo in-memory de fila que transiciona os estados (running, block, success).
- **[Cockpit Tool Runtime Integration](AIW_COCKPIT_TOOL_RUNTIME_INTEGRATION.md)**: Fluxo síncrono conectando o UI server ao core python estrito.
- **[Cockpit Tool Runtime Validation](AIW_COCKPIT_TOOL_RUNTIME_VALIDATION.md)**: Log de segurança de endpoints da integração de runtime.
- **[Cockpit Recovery Report](AIW_COCKPIT_RECOVERY_REPORT.md)**: Estratégias de bypass/safe-mode de resgate da tool.

## Agent Runner & Runtime (Core)
- **[Agent Context Injection](AIW_AGENT_CONTEXT_INJECTION.md)**: Guia de injeção automática de Context Pack (`--use-context-pack`) e RAG nativo.
- **[Agent Offline Mode](AIW_AGENT_OFFLINE_MODE.md)**: Testes de infra e pipeline sem evocar tráfego real LLM (`--offline`).
- **[Tool Runtime Phase 3](AIW_TOOL_RUNTIME_PHASE3.md)**: Definição da Sandbox estática e limites do core.
- **[Tool Runtime Validation Phase 3](AIW_TOOL_RUNTIME_PHASE3_VALIDATION.md)**: Critérios técnicos aplicados durante a compilação local da API de tools.
- **[AIW Runtime Gate](AIW_RUNTIME_GATE.md)**: Camada read-only que decide qual runtime seria necessario sem iniciar Docker, Devcontainer, VM ou LLM.
- **[AIW Execution Provider](AIW_EXECUTION_PROVIDER.md)**: Abstracao entre Agent Loop e mecanismo concreto de execucao, com CodeAct como unico provider funcional atual.
- **[PR Summary Script](AIW_PR_SUMMARY_SCRIPT.md)**: Ajudante gerador de changelogs/diffs automáticos para PRs e runs.
- **[Run Task](AIW_RUN_TASK.md)**: Fluxo e documentação base para formatação do lifecycle de uma tarefa padronizada.

## File OS & Segurança Operacional
- **[File OS Phase 3D](AIW_FILE_OS_PHASE3D.md)**: Regras definitivas contra bypass e travessia de path root em operações file_read/write.
- **[Project Write Mode Phase 3D.2](AIW_PROJECT_WRITE_MODE_PHASE3D2.md)**: Fluxo de três vias da escrita segura (`preview`, `apply`, `rollback`).

## Context & Search Layer
- **[Context Pack v1](AIW_CONTEXT_PACK_V1.md)**: O coração da indexação textual do repositório (`context-pack.json`), limitadores, sanitização e cache de pesquisa.

## Integrações Clássicas e Laboratório (Legacy/Lab)
- **[LiteLLM Tool Calling Investigation](AIW_LITELLM_TOOL_CALLING_INVESTIGATION.md)**: Debuge e investigação profunda no schema de rotas e fallbacks do proxy LiteLLM local.
