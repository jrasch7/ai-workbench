# AI Workbench

AI Workbench é uma bancada local de engenharia de software assistida por agentes de IA.

O objetivo do projeto é construir uma infraestrutura própria, controlável e extensível para desenvolvimento de software com agentes autônomos, inspirada em plataformas como Devin e OpenHands Cloud/Enterprise, mas com foco em liberdade operacional, controle de custos, múltiplos provedores de LLM e adaptação profunda aos projetos reais do usuário.

Este projeto não é apenas uma instalação do OpenHands. A proposta é transformar o OpenHands em um cockpit de engenharia dentro de uma arquitetura própria, com LiteLLM como gateway central de modelos, Docker como runtime/sandbox e uma camada local de organização chamada AI Workbench.

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

## Arquitetura inicial

A arquitetura local inicial é composta por:

```text
AI Workbench
├── OpenHands
│   └── Cockpit principal de agente de software
│
├── LiteLLM
│   └── Gateway local para múltiplos modelos e provedores
│
├── OpenRouter
│   └── Provedor inicial gratuito para validação do fluxo
│
├── Groq
│   └── Provedor auxiliar para testes rápidos e tarefas leves
│
├── Docker
│   └── Runtime e sandbox dos agentes
│
└── scripts/aiw
    └── Comando local para iniciar, parar, verificar status e logs
```

## Fluxo validado

O primeiro pipeline funcional validado foi:

```text
OpenHands GUI
→ modelo openai/dev-coder
→ LiteLLM local
→ OpenRouter free
→ sandbox Docker
→ criação real de arquivo no workspace
```

O teste inicial criou com sucesso o arquivo:

```text
workspaces/sandbox-test/project/STATUS.md
```

Com o conteúdo:

```md
# Status

AI Workbench conectado ao OpenRouter via LiteLLM.
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
./scripts/aiw status
./scripts/aiw logs
./scripts/aiw logs openhands
./scripts/aiw stop
```

A meta é que o usuário não precise memorizar comandos internos de Docker, LiteLLM, OpenHands ou variáveis de ambiente.

## Modelos e provedores

O LiteLLM funciona como gateway local e expõe aliases internos como:

```text
dev-fast
dev-balanced
dev-large
dev-openrouter-free
dev-coder
```

O OpenHands se conecta ao LiteLLM usando modelo OpenAI-compatible:

```text
openai/dev-coder
```

E URL base:

```text
http://host.docker.internal:4000
```

A ideia futura é expandir os perfis de modelo:

```text
dev-fast      → tarefas simples e baratas
dev-coder     → desenvolvimento padrão
dev-review    → revisão e validação
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
* OpenHands rodando localmente;
* LiteLLM rodando em container;
* OpenRouter integrado via LiteLLM;
* modelo `openai/dev-coder` validado na GUI;
* sandbox Docker funcionando;
* criação de arquivo real validada;
* script `scripts/aiw` em consolidação;
* próximo passo: transformar a bancada em um fluxo estável de uso diário.

## Roadmap

### Fase 1 — Fundação local

* [x] Instalar Docker Engine no WSL2
* [x] Instalar e validar OpenHands
* [x] Instalar e validar LiteLLM
* [x] Integrar Groq
* [x] Integrar OpenRouter
* [x] Validar tool calling via LiteLLM
* [x] Validar OpenHands criando arquivo no sandbox
* [x] Consolidar `scripts/aiw`
* [x] Criar `.gitignore` seguro
* [x] Publicar primeira versão no GitHub

### Fase 2 — Bancada de engenharia

* [ ] Criar contexto base do AI Workbench
* [ ] Criar agentes/papéis: executor, validator e integrator
* [ ] Criar padrões de tarefa
* [ ] Criar logs de execução
* [ ] Criar fluxo de validação
* [ ] Criar suporte a projetos reais
* [ ] Criar profiles para Nivela, SisOpERP e outros projetos

### Fase 3 — Projetos reais

* [ ] Integrar workspace do Nivela
* [ ] Integrar workspace do SisOpERP
* [ ] Criar regras por projeto com `AGENTS.md`
* [ ] Padronizar comandos de teste por projeto
* [ ] Criar fluxo de worktree/branch/PR
* [ ] Criar modo executor
* [ ] Criar modo validador
* [ ] Criar modo integrador

### Fase 4 — Plataforma interna

* [ ] Rodar em servidor/cloud
* [ ] Adicionar autenticação
* [ ] Adicionar controle de usuários
* [ ] Adicionar permissões por projeto
* [ ] Adicionar histórico de execuções
* [ ] Adicionar integração com GitHub
* [ ] Adicionar integração com Slack/Discord/Linear/Jira se necessário
* [ ] Criar ambiente para uso por futuros funcionários

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
- [Local Setup](docs/SETUP_LOCAL.md)
- [LiteLLM/OpenRouter Troubleshooting](docs/TROUBLESHOOTING_LITELLM_OPENROUTER.md)

Operational assets:

- [Nivela Context](context/projects/NIVELA.md)
- [SisOpERP Web Context](context/projects/SISOPERP_WEB.md)
- [Task Templates](context/templates/)
- [Agent Profiles](agents/)

