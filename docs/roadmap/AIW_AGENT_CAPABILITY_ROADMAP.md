# AIW Agent Capability Roadmap

O objetivo deste roadmap é orientar as próximas sprints para construir, passo a passo, a infraestrutura fundamental de execução e contexto (Capability Layer) do AI Workbench, preparando o terreno antes de habilitar modelos reais via Ollama ou provedores remotos.

## AIW-CAP-01 — Capability Registry v1
Criar um registro básico estático para definir os esquemas (JSON-schema) e contratos operacionais (policy, limits, IO) de cada ferramenta ou ação que o agente pode utilizar no repositório.

## AIW-CAP-02 — Context/RAG Local Index v1 (✅ Concluído)
Implementar a fundação real de indexação de arquivos utilizando busca semântica, garantindo capacidade local via indexadores eficientes e vetores para suportar consultas complexas em código e doc.
*Nota: A fundação léxica e estrutural de chunking, manifest e busca local foi entregue nesta sprint. Embeddings vetoriais ficam como evolução futura.*

## AIW-CAP-03 — Context Pack Builder v1 (✅ Concluído)
Criar uma estrutura responsável por montar e consolidar o contexto de execução (snippets, logs, documentação) e injetá-lo na requisição de maneira eficiente para o modelo, respeitando janelas de tokens.
*Nota: A primeira versão offline e orçada foi implementada para extrair dados da busca local e gerar packs json/md auditáveis.*

## AIW-CAP-04 — Tool Registry v1 (✅ Concluído)
Estender o Capability Registry implementando instâncias dinâmicas e roteamento de execução segura em tempo de execução para filesystem, shell, git e outras funcionalidades utilitárias.
*Nota: A fundação (schemas estáticos, validação e manifests) foi entregue nesta sprint. A orquestração ativa de roteamento será concluída junto com o Agent Loop.*

## AIW-CAP-05 — CodeAct Sandbox v1 (✅ Concluído)
Desenvolver um orquestrador primitivo para lidar iterativamente com a execução de shell, arquivos de log, e persistência das modificações efetuadas (action + observação) criando a ponte entre comandos e feedbacks.
*Nota: Executor host-sandbox best-effort implementado com validação de padrões, confirmação obrigatória, timeout, captura truncada e artifacts por run.*

## AIW-CAP-06 — Agent Iterative Loop v1 (✅ Concluído)
Implementar o ciclo real de repetição (ReAct / Devin-like) para permitir ao agente planejar, ler, criar patchs e validar de maneira contínua, usando o Tool Registry e o Sandbox do CodeAct até que conclua seu objetivo.
*Nota: A v1 offline/manual foi entregue com CLI foreground, dry-run, execute confirmado, artifacts rastreaveis, consulta ao Capability Registry, Capability Policy `local_offline_v1`, path hygiene em UI/API/artifacts novos, contexto minimo ou Context Pack existente, mock planner deterministico, Cockpit read-only com historico/detalhe de run, e CodeAct com acao fixa segura. Planejamento por LLM e autonomia ficam para iteracoes futuras.*

### AIW-CAP-06.4 — Regression Harness + Isolation Boundary v1 (✅ Concluído)
Adicionar smoke offline para travar os contratos do Agent Iterative Loop: CLI, dry-run, execute confirmado, bloqueios de policy, path hygiene, traversal e Cockpit read-only opcional.
*Nota: O comando `./scripts/aiw-agent-loop-regression-smoke --workspace aiw` grava evidencias em `.aiw/workspaces/<id>/agent-loop-regression/runs/<run_id>/` e registra a fronteira de isolamento sem LLM real, sem GitHub/Jira write, sem daemon persistente e sem `shell=True`.*

### AIW-OPS-01 — Safe Search Guard v1 (✅ Concluído)
Adicionar `./scripts/aiw-safe-search` como busca textual operacional com `--paths` obrigatorio, bloqueio de secrets/artifacts e output relativo ao repo.
*Nota: O guard substitui buscas manuais perigosas como `grep -R ... .` quando houver risco de varrer `.env`, config sensivel, `.aiw/` ou diretórios amplos.*

## AIW-CAP-07 — Isolation Boundary + Devcontainer Gate v1 (✅ Concluído)
Adicionar um gate explicito para decidir se operacoes podem continuar no perfil atual `host_best_effort`.
*Nota: Fixed CodeAct offline confirmado continua permitido; dynamic CodeAct, LLM planner, shell, rede externa e external write ficam bloqueados. O gate registra `stronger_isolation_required` para LLM/codigo dinamico e exige devcontainer ou VM antes de qualquer LLM real.*

## AIW-CAP-08 — Devcontainer Sandbox v1
Implementar isolamento forte de host via Devcontainers (ou Docker Sandbox), rodando o agente de forma efêmera sem riscos para o ambiente hospedeiro do usuário.
*Nota: A primeira etapa entregue e o Runtime Gate v1: uma decisao metadata-only que aponta `host_best_effort`, `devcontainer`, `docker` ou `vm` sem iniciar nenhum runtime. Apenas `host_best_effort` segue permitido; `devcontainer` e requerido para codigo dinamico, LLM, shell, rede externa e external write.*

## AIW-CAP-09 — E2E Agent Harness Smoke v1
Garantir o fluxo End-to-End da camada Capability usando mocks robustos, provando que o Capability Registry, Sandbox e Loop iterativo funcionam com segurança em modo pipeline offline.

## AIW-CAP-10 — Local Model Provider Lab
Conectar o orquestrador (Agent Loop, Tool Registry, Context Pack) a instâncias reais de modelos de linguagem via provedor Ollama (Local) / LiteLLM, ativando inteligência nas ações dentro da camada de segurança comprovada nos passos anteriores.
