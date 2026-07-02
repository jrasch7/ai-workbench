# AIW Agent Capability Roadmap

O objetivo deste roadmap é orientar as próximas sprints para construir, passo a passo, a infraestrutura fundamental de execução e contexto (Capability Layer) do AI Workbench, preparando o terreno antes de habilitar modelos reais via Ollama ou provedores remotos.

## AIW-CAP-01 — Capability Registry v1
Criar um registro básico estático para definir os esquemas (JSON-schema) e contratos operacionais (policy, limits, IO) de cada ferramenta ou ação que o agente pode utilizar no repositório.

## AIW-CAP-02 — Context/RAG Local Index v1 (✅ Concluído)
Implementar a fundação real de indexação de arquivos utilizando busca semântica, garantindo capacidade local via indexadores eficientes e vetores para suportar consultas complexas em código e doc.
*Nota: A fundação léxica e estrutural de chunking, manifest e busca local foi entregue nesta sprint. Embeddings vetoriais ficam como evolução futura.*

## AIW-CAP-03 — Context Pack Builder v1
Criar uma estrutura responsável por montar e consolidar o contexto de execução (snippets, logs, documentação) e injetá-lo na requisição de maneira eficiente para o modelo, respeitando janelas de tokens.

## AIW-CAP-04 — Tool Registry v1 (✅ Concluído)
Estender o Capability Registry implementando instâncias dinâmicas e roteamento de execução segura em tempo de execução para filesystem, shell, git e outras funcionalidades utilitárias.
*Nota: A fundação (schemas estáticos, validação e manifests) foi entregue nesta sprint. A orquestração ativa de roteamento será concluída junto com o Agent Loop.*

## AIW-CAP-05 — CodeAct Sandbox v1
Desenvolver um orquestrador primitivo para lidar iterativamente com a execução de shell, arquivos de log, e persistência das modificações efetuadas (action + observação) criando a ponte entre comandos e feedbacks.

## AIW-CAP-06 — Agent Iterative Loop v1
Implementar o ciclo real de repetição (ReAct / Devin-like) para permitir ao agente planejar, ler, criar patchs e validar de maneira contínua, usando o Tool Registry e o Sandbox do CodeAct até que conclua seu objetivo.

## AIW-CAP-07 — Browser/Web Tool Lab v1
Integrar as capacidades iniciais de acesso externo controlado à internet, como captura do status de tickets remotos, ler repositórios não nativos ou realizar scraping seguro de documentações em tempo real.

## AIW-CAP-08 — Devcontainer Sandbox v1
Implementar isolamento forte de host via Devcontainers (ou Docker Sandbox), rodando o agente de forma efêmera sem riscos para o ambiente hospedeiro do usuário.

## AIW-CAP-09 — E2E Agent Harness Smoke v1
Garantir o fluxo End-to-End da camada Capability usando mocks robustos, provando que o Capability Registry, Sandbox e Loop iterativo funcionam com segurança em modo pipeline offline.

## AIW-CAP-10 — Local Model Provider Lab
Conectar o orquestrador (Agent Loop, Tool Registry, Context Pack) a instâncias reais de modelos de linguagem via provedor Ollama (Local) / LiteLLM, ativando inteligência nas ações dentro da camada de segurança comprovada nos passos anteriores.
