# AI Workbench

AI Workbench é uma bancada local de engenharia de software assistida por agentes de IA.

O objetivo do projeto é construir uma infraestrutura própria, controlável e extensível para desenvolvimento de software com agentes autônomos, inspirada em plataformas como Devin, Manus e ambientes CodeAct, mas com foco em liberdade operacional, controle de custos, múltiplos provedores de LLM e adaptação profunda aos projetos reais do usuário.

Este projeto não é uma instalação do OpenHands. A direção atual é construir uma bancada/interface própria, o AIW Cockpit, com LiteLLM como gateway central de modelos, runtime local controlado, evidências auditáveis e uma camada de organização chamada AI Workbench.

## Visão

A visão do AI Workbench é criar um ambiente onde agentes de IA consigam:

* entender projetos reais de software;
* executar tarefas de desenvolvimento;
* editar arquivos com segurança;
* validar mudanças;
* rodar comandos e testes;
* gerar relatórios;
* atuar como executor, validador e integrador;
* trabalhar com múltiplos modelos e provedores;
* reduzir dependência de plataformas comerciais com limites rígidos;
* futuramente operar em ambiente cloud para uso por uma equipe.

O foco é montar uma plataforma séria de engenharia, não apenas um chatbot de código.

## Motivação

O projeto nasceu da necessidade de ter uma infraestrutura de IA mais livre, customizável e adequada a cenários reais de desenvolvimento.

O usuário trabalha simultaneamente em:

* uma startup SaaS/ERP chamada Nivela;
* um ERP legado consolidado em ambiente empresarial;
* projetos de migração, modernização, automação e engenharia de software;
* fluxos com agentes de IA, validação, GitHub, CI/CD e deploy.

Ferramentas como Cursor, Cline, Continue e Aider são úteis, mas funcionam mais como ferramentas individuais. O objetivo do AI Workbench é ir além: criar um cockpit unificado, com agentes capazes de produzir, validar e integrar trabalho real em projetos de software.

## Arquitetura atual

A arquitetura local é composta por:

```text
AI Workbench
├── AIW Cockpit
│   └── Interface própria para criar tasks, acompanhar runs e revisar evidências
│
├── AIW Runner / Tool Runtime
│   └── Execução local controlada, logs, validações e artefatos de run
│
├── LiteLLM
│   └── Gateway local para aliases de modelo por papel
│
├── Provedores LLM
│   └── Hugging Face Router, NVIDIA NIM, OpenRouter/Groq como laboratório ou fallback
│
├── LangGraph / contexto
│   └── Orquestração determinística e recuperação de contexto
│
├── Docker
│   └── Base para sandbox/workspaces quando necessário
│
└── scripts/aiw
    └── Comando local para operar gateway, cockpit, tasks, runs e validações
```

## Fluxo validado

O pipeline operacional atual é:

```text
AIW Cockpit / scripts
→ task local
→ AIW runner / tool runtime
→ LiteLLM via alias operacional
→ workspace controlado
→ run com logs, evidências, validação e handoff
```

Um teste histórico validou que o gateway LiteLLM conseguia acionar modelo e criar arquivo em workspace:

```text
workspaces/sandbox-test/project/STATUS.md
```

Com o conteúdo:

```md
# Status

AI Workbench conectado ao LiteLLM via aliases estáveis, atualmente roteados para Hugging Face Router e NVIDIA NIM.
```

## Estrutura do projeto

```text
ai-workbench/
├── config/
│   └── litellm.yaml
│
├── scripts/
│   └── aiw
│
├── workspaces/
│   └── sandbox-test/
│
├── logs/
├── context/
├── agents/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Comando principal

O projeto usa o script `aiw` como ponto único de controle local.

Exemplos:

```bash
./scripts/aiw start sandbox-test
./scripts/aiw cockpit
./scripts/aiw local-status
./scripts/aiw run-once
./scripts/aiw status
./scripts/aiw logs
./scripts/aiw stop
```

A meta é que o usuário não precise memorizar comandos internos de Docker, LiteLLM, runtime local ou variáveis de ambiente.

## Modelos e provedores

O LiteLLM funciona como gateway local e expõe aliases internos como:

```text
dev-fast
dev-balanced
dev-large
dev-coder
dev-review
dev-architect
dev-fallback
```

Clientes OpenAI-compatible, quando necessários, usam o prefixo `openai/`:

```text
openai/dev-coder
```

O AIW Cockpit e os scripts devem preferir aliases por papel (`dev-coder`, `dev-review`, `dev-architect`) em vez de depender de nomes crus de provedores.

Perfis de modelo:

```text
dev-fast      → tarefas simples e fallback leve
dev-balanced  → raciocínio geral e validação intermediária
dev-large     → tarefas maiores e arquitetura
dev-coder     → desenvolvimento padrão
dev-review    → revisão e validação
dev-architect → decisões estruturais
dev-fallback  → contingência operacional
dev-premium   → arquitetura, refatorações grandes e tarefas críticas
```

## Segurança

Este projeto deve seguir regras rígidas de segurança:

* nunca commitar `.env`;
* nunca commitar chaves de API;
* nunca expor tokens no histórico do Git;
* separar `.env.example` de `.env`;
* manter workspaces e logs fora do versionamento quando contiverem dados sensíveis;
* revisar qualquer arquivo antes de enviar para GitHub;
* não montar repositórios com secrets diretamente sem controle;
* preferir aliases de modelos via LiteLLM em vez de chaves diretas na UI.

## Estado atual

Status atual do projeto:

* Docker Engine no WSL2 funcionando;
* LiteLLM rodando em container;
* aliases operacionais roteados para pool validado;
* modelo `dev-coder` validado via scripts/gateway;
* AIW Cockpit como interface própria em evolução;
* runner local com tasks/runs/evidências;
* sandbox Docker funcionando;
* criação de arquivo real validada;
* script `scripts/aiw` em consolidação;
* próximo passo: evoluir o Tool Runtime mínimo estilo Manus/Devin/CodeAct.

## Roadmap

### Fase 1 — Fundação local

* [x] Instalar Docker Engine no WSL2
* [x] Instalar e validar LiteLLM
* [x] Integrar pool Hugging Face Router / NVIDIA NIM
* [x] Integrar OpenRouter como provider de laboratório/fallback
* [x] Validar tool calling via LiteLLM
* [x] Validar criação de arquivo em workspace controlado
* [x] Consolidar `scripts/aiw`
* [x] Criar AIW Cockpit MVP
* [x] Criar `.gitignore` seguro
* [x] Publicar primeira versão no GitHub

### Fase 2 — Bancada própria de engenharia

* [x] Criar logs de execução
* [x] Criar fluxo de validação
* [x] Criar AIW Cockpit como workspace operacional bonito e funcional
* [x] Criar contexto base do AI Workbench (Context Pack v1)
* [x] Busca Lexical Local via cache de indexação
* [x] Injeção de Context Pack no Agent Runner
* [ ] Criar agentes/papéis específicos refinados: executor, validator e integrator
* [ ] Criar profiles para Nivela, SisOpERP e outros projetos

### Fase 3 — Tool Runtime mínimo

* [x] Criar `directory_list`
* [x] Criar `file_read`
* [x] Criar `shell_exec` controlado
* [x] Registrar logs/evidências por tool call
* [x] Adicionar `file_write` restrito
* [x] Adicionar `file_patch` com diff auditável
* [x] Integrar tools ao AIW Cockpit
* [x] Implementar Tool Evidence Console
* [x] Fluxo de aprovação de patches seguro (Preview, Apply, Rollback)

### Fase 4 — Projetos reais

* [ ] Integrar workspace do Nivela
* [ ] Integrar workspace do SisOpERP
* [ ] Criar regras por projeto com `AGENTS.md`
* [ ] Padronizar comandos de teste por projeto
* [ ] RAG lexical assistido melhorado / ranking de Context Pack
* [ ] Multi-project workspace na Cockpit

### Fase 5 — Plataforma interna

* [ ] Aprovação humana mais refinada
* [ ] Integração futura Hermes somente quando fizer sentido
* [ ] Autenticação e permissões de usuários
* [ ] Rodar em servidor/cloud

## Filosofia

O AI Workbench deve ser tratado como uma plataforma de engenharia, não como um experimento solto.

A prioridade é construir algo:

* confiável;
* simples de iniciar;
* fácil de auditar;
* seguro com secrets;
* extensível;
* barato de operar;
* forte o suficiente para projetos reais;
* adaptado ao modo de trabalho do usuário.

O objetivo final é ter uma infraestrutura própria de IA para engenharia de software, capaz de aumentar drasticamente a produtividade sem depender de uma única ferramenta, um único provedor ou uma única interface comercial.

## Licença

Licença a definir.

## Operational Documentation

Core docs for operating the AI Workbench:

- [Engineering Bench](docs/ENGINEERING_BENCH.md)
- [Infra Runbook](docs/INFRA_RUNBOOK.md)
- [Project Contexts](docs/PROJECT_CONTEXTS.md)
- [Agents](docs/AGENTS.md)
- [Operational Workflow](docs/OPERATIONAL_WORKFLOW.md)
- [Model Strategy](docs/MODEL_STRATEGY.md)
- [Role Aliases](docs/ROLE_ALIASES.md)
- [OpenHands Historical Validation](docs/OPENHANDS_VALIDATION.md)
- [Hermes Adoption Plan](docs/HERMES_ADOPTION_PLAN.md)
- [Hermes Project Rules](HERMES.md)
- [Hermes Telegram Investigation](docs/HERMES_TELEGRAM_INVESTIGATION.md)
- [Hermes Gateway Operations](docs/HERMES_GATEWAY_OPERATIONS.md)
- [Local Setup](docs/SETUP_LOCAL.md)
- [LiteLLM/OpenRouter Troubleshooting](docs/TROUBLESHOOTING_LITELLM_OPENROUTER.md)

Operational assets:

- [Nivela Context](context/projects/NIVELA.md)
- [SisOpERP Web Context](context/projects/SISOPERP_WEB.md)
- [Task Templates](context/templates/)
- [Agent Profiles](agents/)
