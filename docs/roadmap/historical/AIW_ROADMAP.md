# AI Workbench Roadmap

Este roadmap define as fases atuais e futuras do AIW, considerando que a fundação essencial operacional já está finalizada.

## Concluído

* **Fundação LiteLLM/model aliases:** Base de integração com provedores estabelecida sem vazamento estrutural.
* **Tool Runtime mínimo:** Implementação customizada de tool execution via engine protegida.
* **Cockpit integration:** A interface web (Cockpit) se tornou a interface nativa real para orchestrar as runs.
* **Agent Offline:** Capacidade de dry-run do sistema sem gasto com tokens.
* **File OS seguro:** Comandos imutáveis anti-traversal para lidar com a filesystem do repo alvo.
* **Project Patch Preview:** Estratégia madura de visualização de diffs antes de mutar a codebase real.
* **Execution Harness:** Orquestração linear in-memory das rodadas do agente.
* **Tool Evidence Console:** Log visual acoplado em blocos para inspecionar tool a tool na UI.
* **Operational View:** Mission control do dashboard limpo mostrando o log cronológico do que ocorreu.
* **Navigation/Search:** Busca otimizada de runs, paths e workspaces locais.
* **Context Pack v1:** Health reporting estático com base indexada.
* **Context injection:** Mecanismo de injetar e renderizar as fontes textuais no LLM em boot time.

## Em andamento / próximo

* **Context Pack source selection/ranking:** Melhorar as heurísticas de quais arquivos submetem para a injection (RAG lexical assistido focado em peso).
* **Task/Project profiles:** Suporte robusto a múltiplos perfis operacionais com restrições delimitadas por ambiente (ERP Legacy vs Web Moderno).
* **Multi-project workspace:** Capacidade no Cockpit de rodar tasks que abraçam subdiretórios de monorepos ou front/back de modo contíguo.
* **Approval UX refinada:** Opções avançadas de diff interactivo e accept/reject per chunk (partial patch apply).
* **Git workflow local:** Commits isolados gerenciados por branch via UI sem forçar PRs sujos na branch main.
* **Worker roles:** Divisão clara no pipeline: um agente para Architecture, outro para Execution e um final para Review/Validation.
* **Docs/knowledge sync:** Rotina automática (chronos) que roda em background re-indexando o Context Pack toda vez que um branch local mudar.

## Futuro

* **RAG vetorial (Embeddings locais):** Subir banco vetorial real com pgvector ou ChromaDB apenas quando a demanda textual suprimir 100K tokens constantes e inviabilizar o prompt cache.
* **Modelos locais/Ollama:** Dar autonomia offline plena utilizando Qwen Coder ou Llama3.1 via hardware local.
* **Cyber Bench:** Workspace laboratorial estrito para debugar agent break-outs (segurança de infra).
* **Hermes/Paperclip/Ralph labs:** Standby legados; integrações complexas reativadas só em cenários cloud se necessário.
* **Cloud/team mode:** Portabilidade multi-tenant permitindo instâncias AIW em times corporativos na AWS/GCP usando auth unificada.
