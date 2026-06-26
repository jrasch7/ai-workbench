# AIW CodeAct / Manus-style Workbench Blueprint

## 1. Objetivo

Este documento define o blueprint arquitetural do AI Workbench para evoluir de uma bancada de modelos e scripts para uma workbench operacional de agentes com execução observável, inspirada em padrões de produtos como Manus, Devin e ambientes CodeAct.

O objetivo não é copiar uma ferramenta específica. O objetivo é consolidar um padrão interno do AIW para:

- executar tarefas reais em ambiente isolado;
- permitir que agentes leiam, modifiquem e validem código;
- navegar em aplicações web com browser headless;
- rodar comandos em terminal controlado;
- gerar evidências, relatórios e artefatos;
- manter segurança, rastreabilidade e governança;
- preparar integração futura com Hermes sem acoplar Hermes diretamente a provedores.

## 2. Princípio central

O AIW deve separar três responsabilidades:

    [Usuário / João]
            |
            v
    [Agent Orchestrator / Planner]
            |
            +-----------------------------+
            |                             |
            v                             v
    [LLM Raciocínio]              [Execution Sandbox]
    LiteLLM / modelos              Docker / Devcontainer / VM
            |                             |
            |                             +--> Shell OS
            |                             +--> File OS
            |                             +--> Browser OS
            |                             +--> Python CodeAct
            |                             +--> Artifact Outputs
            |
            v
    [Resposta + Evidência + Handoff]

O LLM decide, planeja e chama ferramentas. A execução real acontece em sandbox Linux controlado.

## 3. Camadas da Workbench

### 3.1 Agent Orchestrator / Planner

Responsável por receber o objetivo macro e quebrar em passos menores.

Responsabilidades:

- entender a tarefa;
- selecionar modelo via LiteLLM;
- decidir quais ferramentas podem ser usadas;
- manter estado da sessão;
- acompanhar falhas;
- pedir validação quando necessário;
- gerar handoff final com evidências;
- impedir ações fora do escopo.

O Planner não deve executar comandos diretamente no host. Ele deve encaminhar ações para uma camada de execução isolada.

### 3.2 LLM Reasoning Layer

Camada de raciocínio e decisão.

No AIW, o acesso a modelos deve passar por LiteLLM.

Padrão desejado:

    Hermes / Orchestrator -> LiteLLM aliases -> provedores reais

Aliases estáveis devem ser preferidos a nomes crus de provedores.

Exemplos:

- `dev-fast`
- `dev-coder`
- `dev-review`
- `dev-architect`
- `dev-fallback`

A escolha do provedor real pode mudar sem quebrar o agente.

### 3.3 Execution Sandbox

Ambiente isolado onde ações são executadas.

Pode começar com Docker/devcontainer e evoluir depois para isolamento mais forte.

Regras:

- nunca executar ações permissivas diretamente no host;
- não montar secrets sensíveis por padrão;
- limitar diretórios acessíveis;
- limitar rede quando possível;
- registrar comandos, saídas e arquivos alterados;
- permitir destruição/recriação do ambiente;
- separar sandbox por projeto/sessão.

### 3.4 Feedback Loop observável

A interface do AIW deve mostrar o agente trabalhando.

O usuário precisa conseguir ver:

- comandos sendo executados;
- logs em tempo real;
- testes passando/falhando;
- arquivos modificados;
- screenshots do browser;
- checkpoints;
- handoffs finais.

Esse loop visual é parte central da experiência Manus/Devin-style.

## 4. Tool OS

O AIW deve tratar ferramentas como subsistemas operacionais especializados.

### 4.1 Browser OS

Ferramentas para operar aplicações web.

| Tool | Função |
| --- | --- |
| `browser_navigate` | Abre uma URL no navegador virtual |
| `browser_click` | Clica em elementos via seletor CSS ou coordenadas |
| `browser_type` | Digita texto em inputs |
| `browser_scroll` | Rola a página |
| `browser_screenshot` | Captura a tela para inspeção visual |
| `browser_wait` | Aguarda elemento, rede ou estado |
| `browser_console` | Coleta erros do console |
| `browser_network` | Coleta falhas de rede e status HTTP |

Uso previsto:

- validar landing pages;
- testar fluxos SaaS;
- testar login, checkout e onboarding;
- capturar evidências visuais;
- reproduzir bugs de UI;
- validar responsividade.

Base técnica provável:

- Playwright;
- Chromium headless/headful;
- screenshots salvos em `reports/`;
- logs de console e network.

### 4.2 File OS

Ferramentas para operar arquivos do workspace.

| Tool | Função |
| --- | --- |
| `directory_list` | Lista diretórios e árvores do projeto |
| `file_read` | Lê arquivos |
| `file_write` | Cria ou substitui arquivos |
| `file_patch` | Aplica alterações cirúrgicas |
| `file_search` / `grep` | Busca strings no workspace |
| `file_stat` | Consulta metadados |
| `file_diff` | Mostra diff de alterações |

Regras:

- preferir patch cirúrgico a reescrita completa;
- nunca editar `.env` sem decisão explícita;
- nunca salvar secrets em docs;
- nunca usar `git add .`;
- sempre mostrar diff antes de commit;
- preservar arquivos fora de escopo.

### 4.3 Shell OS

Ferramentas para execução de terminal.

| Tool | Função |
| --- | --- |
| `shell_exec` | Executa comandos Bash no sandbox |

Uso previsto:

- instalar dependências;
- rodar testes;
- rodar builds;
- iniciar serviços;
- consultar Git;
- executar scripts do AIW;
- validar saúde do ambiente.

Regras:

- comandos destrutivos exigem proteção;
- comandos longos precisam timeout;
- comandos devem rodar no sandbox, não no host;
- logs devem ser persistidos;
- comandos com secrets não devem ser exibidos em claro;
- `git config user.name` e `git config user.email` são proibidos para agentes.

### 4.4 Python CodeAct

CodeAct é o modo em que o agente escreve e executa código Python para raciocinar, transformar dados, validar arquivos ou automatizar tarefas.

Uso previsto:

- manipular JSON/YAML/Markdown;
- gerar relatórios;
- validar schemas;
- processar logs;
- construir patches;
- criar artefatos auxiliares;
- fazer análises rápidas dentro da sessão.

Regras:

- Python deve rodar no sandbox;
- código gerado deve ser registrado;
- scripts temporários devem ir para `/tmp` ou pasta runtime ignorada;
- artefatos úteis devem ser promovidos para `docs/` ou pasta versionada após revisão;
- nada sensível deve ser serializado em logs.

### 4.5 Artifact Outputs

Ferramentas de saída para consolidar resultados.

| Tool | Função |
| --- | --- |
| `slides_generator` | Gera apresentações |
| `pdf_render` | Renderiza relatórios em PDF |
| `image_generation` | Cria assets visuais básicos |
| `markdown_report` | Consolida relatório versionável |
| `screenshot_bundle` | Agrupa evidências visuais |

Uso previsto:

- relatórios de validação;
- apresentações executivas;
- documentação visual;
- evidências de QA;
- snapshots de projeto;
- materiais de reunião.

## 5. Contrato mínimo de uma Tool

Toda tool do AIW deve ter contrato claro.

Formato conceitual:

    name: browser_navigate
    input_schema:
      url: string
    output_schema:
      ok: boolean
      status: number
      current_url: string
      evidence:
        screenshot_path: string?
        console_errors: list?
        network_errors: list?
    risk_level: low | medium | high
    requires_sandbox: true
    logs: true

Campos obrigatórios:

- nome;
- descrição;
- input schema;
- output schema;
- nível de risco;
- se exige sandbox;
- se gera evidência;
- timeout padrão;
- política de erro.

## 6. Segurança e governança

### 6.1 Regra de isolamento

Toda execução potencialmente perigosa deve ocorrer em sandbox.

Proibido no host:

- bypass de permissões;
- comandos destrutivos amplos;
- montagem de credenciais sensíveis;
- execução de ferramentas ofensivas fora de lab autorizado;
- alteração silenciosa de configuração global.

### 6.2 Secrets

Proibido registrar em docs, logs ou handoffs:

- `.env`;
- tokens;
- API keys;
- cookies;
- Authorization headers;
- chaves privadas;
- credenciais de clientes.

### 6.3 Git

Regras obrigatórias:

- `git status --short` ou `git status -sb`;
- `git diff --check`;
- `git diff --stat`;
- diff revisado antes de commit;
- stage explícito por arquivo;
- nunca usar `git add .`;
- push somente após validação.

### 6.4 Browser / Web

Regras:

- testar apenas ambientes próprios ou autorizados;
- não coletar credenciais reais sem necessidade;
- não rodar flood;
- capturar evidências sem expor dados sensíveis;
- usar contas de teste quando possível.

### 6.5 Cyber Bench

Ferramentas de segurança ofensiva ou semi-ofensiva só podem rodar dentro de escopo autorizado.

Regras:

- alvo próprio ou autorização explícita;
- sem produção salvo aprovação;
- sem credenciais reais;
- sem destruição;
- sem brute force fora de escopo;
- evidências obrigatórias;
- regras de engajamento antes do teste.

## 7. Estrutura sugerida de diretórios

Estrutura alvo:

    .aiw/
      tasks/
      runs/
      state/
      lab/

    config/
      litellm.yaml

    scripts/
      model-smoke
      model-ask
      model-pool-smoke
      aiw-run-task
      aiw-cockpit

    docs/
      architecture/
        AIW_CODEACT_MANUS_BLUEPRINT.md
      model-bench/
      runbooks/
      obsidian/
      decisions/

    reports/
      browser/
      provider-smoke/
      langgraph-smoke/
      artifacts/

Regra:

- `reports/` é runtime/local por padrão;
- evidência importante deve ser curada para `docs/`;
- docs versionados devem estar limpos de secrets.

## 8. Roadmap técnico

### Fase 1 — Blueprint e contratos

Objetivo: documentar arquitetura e contratos mínimos.

Entregas:

- blueprint CodeAct/Manus-style;
- contrato conceitual de tools;
- política de sandbox;
- matriz inicial de tools;
- critérios de segurança.

### Fase 2 — LiteLLM como camada de modelos

Status atual:

- LiteLLM rodando em Docker Compose;
- `/v1/models` validado;
- `model-smoke` validando `message.content`;
- `model-ask` validado;
- `model-pool-smoke` criado;
- pool inicial com NVIDIA e Hugging Face Router validado.

Próximo refinamento:

- mapear aliases estáveis;
- definir modelo padrão para coder/review/architect/fast;
- documentar fallback.

### Fase 3 — Tool Runtime mínimo

Objetivo: criar runtime mínimo com tools locais.

Entregas:

- `shell_exec` controlado;
- `file_read` / `file_write` / `file_patch`;
- `directory_list`;
- `grep` / `file_search`;
- logs por execução;
- política de timeout;
- formato de resposta das tools.

### Fase 4 — Browser OS

Objetivo: adicionar navegação e validação visual.

Entregas:

- Playwright no sandbox;
- `browser_navigate`;
- `browser_click`;
- `browser_type`;
- `browser_scroll`;
- `browser_screenshot`;
- coleta de console errors;
- coleta de network errors.

### Fase 5 — CodeAct Harness

Objetivo: permitir que o agente gere e rode Python controlado.

Entregas:

- execução Python isolada;
- diretório temporário por run;
- captura de stdout/stderr;
- promoção manual de artefatos;
- bloqueio de secrets em outputs.

### Fase 6 — UI / Cockpit com feedback ao vivo

Objetivo: mostrar execução em tempo real.

Entregas:

- terminal streaming;
- timeline de passos;
- screenshots;
- diffs;
- status de testes;
- botão de aprovar/rejeitar;
- handoff final.

### Fase 7 — Integração Hermes

Objetivo: conectar Hermes ao AIW runtime depois que o runtime estiver validado.

Regra:

Hermes não deve ser conectado diretamente a provedores individuais.

Fluxo correto:

    Hermes -> AIW Orchestrator -> LiteLLM aliases -> Tool Runtime -> Sandbox

## 9. Critérios de sucesso

O blueprint será considerado implementado quando:

- um agente conseguir receber uma tarefa e quebrar em passos;
- o agente conseguir ler e alterar arquivos com diff controlado;
- o agente conseguir rodar testes no sandbox;
- o agente conseguir navegar em uma aplicação web;
- screenshots e logs forem salvos como evidência;
- o usuário conseguir acompanhar execução ao vivo;
- handoff final incluir comandos, diffs, testes e riscos;
- secrets não aparecerem em logs/docs;
- Hermes puder usar o runtime sem bypass de segurança.

## 10. Decisão operacional

O AIW deve seguir uma arquitetura Manus-style baseada em:

    Planner + LiteLLM + Sandbox + Tool OS + CodeAct + Browser + Feedback Loop

Essa arquitetura vira a referência para próximas implementações do AI Workbench.

Antes de integrar Hermes, o AIW precisa consolidar:

1. aliases estáveis no LiteLLM;
2. contrato mínimo das tools;
3. sandbox seguro;
4. wrapper de execução;
5. logging e evidências;
6. Browser OS com Playwright;
7. feedback loop no cockpit.
