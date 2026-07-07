# AI Workbench — AIW

O **AI Workbench (AIW)** é a bancada de IA do ecossistema Nivela.

Ele não é um produto comercial para vender neste momento. O AIW é a infraestrutura interna, laboratório, cockpit e backbone operacional usado para construir, testar, organizar e evoluir produtos com apoio de uma equipe de agentes de IA.

A visão é transformar o desenvolvimento do ecossistema Nivela em uma operação orientada por agentes: o fundador atua como direção estratégica, Product Owner e sócio-investidor, enquanto os agentes executam pesquisa, planejamento, implementação, validação, integração, documentação e aprendizado contínuo.

---

## Objetivo

Criar uma bancada de IA quase autônoma para:

* acelerar o desenvolvimento do ecossistema Nivela;
* reduzir dependência de contexto manual em chats longos;
* organizar conhecimento técnico, decisões, PRDs, runbooks e handoffs;
* testar ferramentas modernas de agentes antes de consolidar padrões;
* permitir execução segura em ambientes isolados;
* criar um laboratório local para modelos, automação e cibersegurança autorizada;
* transformar ideias estratégicas em execução validada.

---

## Princípios

O AIW segue alguns princípios operacionais:

1. **Testar antes de consolidar**
   Nenhuma ferramenta vira padrão por hype. Tudo passa por pesquisa, instalação, smoke test e uso real pequeno.

2. **Evidência antes de confiança**
   Agentes precisam entregar comandos executados, saídas reais, diff, validações e riscos.

3. **Git como fonte versionada**
   Decisões críticas, skills, runbooks e documentação operacional devem estar versionados.

4. **Obsidian como conhecimento navegável**
   O vault serve como camada de conhecimento auditável, conectando decisões, produtos, domínios, PRDs e snapshots.

5. **Segurança e isolamento**
   Execução perigosa ou permissiva deve ocorrer em sandbox, devcontainer ou laboratório controlado.

6. **Sem secrets no conhecimento**
   Vault, docs e handoffs não devem conter tokens, `.env`, chaves privadas, credenciais ou dados sensíveis de clientes.

7. **Ferramentas em anéis de maturidade**
   Ferramentas novas entram como experimento e só avançam conforme validação real.

8. **Local-first quando fizer sentido**
   Modelos locais são importantes para privacidade, custo, laboratório e cibersegurança autorizada.

9. **APIs premium para tarefas críticas**
   Anthropic, OpenAI, Gemini e OpenRouter podem ser usados como fallback ou para tarefas de maior complexidade.

10. **Agentes não substituem validação**
    Toda entrega importante precisa de revisão, validação e rastreabilidade.

---

## Anéis de maturidade

Cada ferramenta, integração ou fluxo do AIW deve ser classificado em um ring:

| Ring   | Significado                      |
| ------ | -------------------------------- |
| Ring 0 | Pesquisado e documentado         |
| Ring 1 | Instalado em laboratório         |
| Ring 2 | Smoke test validado              |
| Ring 3 | Usado em fluxo real pequeno      |
| Ring 4 | Padrão operacional do AIW/Nivela |

A promoção entre rings exige evidência: instalação, testes, limitações conhecidas, riscos e critérios de sucesso.

---

## Arquitetura alvo

O AIW é composto por camadas complementares.

### Obsidian Knowledge Layer

Camada de conhecimento auditável.

Uso previsto:

* PRDs;
* ADRs e decisões técnicas;
* runbooks;
* handoffs;
* snapshots;
* roadmap;
* documentação de marca;
* documentação por produto;
* documentação por domínio;
* matriz de ferramentas;
* histórico de experimentos;
* avaliação de modelos e agentes.

O Obsidian é o cérebro navegável. O Git continua sendo a fonte versionada.

### Hermes Runtime

Runtime de agentes com memória persistente, skills, gateways e capacidade de autoaperfeiçoamento.

Uso previsto:

* execução local de tarefas;
* Telegram Gateway;
* skills versionadas;
* handoffs operacionais;
* interação futura com Obsidian;
* worker futuro dentro do Paperclip.

Governança atual:

* self-improvement é permitido;
* promoção silenciosa de skills é proibida;
* skills locais são drafts;
* regras críticas ficam em Git;
* Hermes pode futuramente escrever no Inbox do Obsidian, mas não pode promover decisões automaticamente.

### Paperclip Control Plane

Camada experimental para organização de agentes.

Uso previsto:

* org chart;
* agentes como “funcionários”;
* metas;
* budgets;
* workers;
* dashboard;
* auditoria;
* possível integração com Hermes via `hermes-paperclip-adapter`.

Paperclip deve ser testado em laboratório antes de virar padrão.

### Ralph Execution Harness

Harness de execução autônoma orientado por PRD.

Uso previsto:

* ler PRDs;
* quebrar tarefas;
* executar iterações;
* manter contexto limpo por ciclo;
* registrar progresso em disco/Git;
* usar PRDs vindos do Obsidian.

### Devcontainer Sandbox

Ambiente isolado para execução de agentes por projeto.

Uso previsto:

* rodar Claude Code dentro de container;
* isolar permissões;
* restringir egress;
* evitar execução permissiva no host;
* permitir automação controlada por projeto.

Regra crítica:

`--dangerously-skip-permissions` nunca deve ser usado no host bare metal. Somente dentro de container/VM isolado e controlado.

### Ollama Local Model Lab

Laboratório de modelos locais.

Uso previsto:

* testar modelos pequenos e médios;
* triagem;
* raciocínio auxiliar;
* coding local;
* Cyber Bench;
* redução de bloqueios falsos de provedores comerciais em cenários autorizados.

Hardware atual:

* CPU: Intel i5-10400;
* RAM: 16 GB;
* GPU: GTX 1650 Super 4 GB VRAM.

Alvo inicial realista:

* modelos 3B, 7B e 8B quantizados;
* Qwen Coder;
* Qwen3;
* modelos pequenos de código e raciocínio.

### Cyber Bench

Bancada de cibersegurança autorizada.

Uso previsto:

* laboratório isolado;
* análise de vulnerabilidades;
* validação defensiva;
* estudo técnico;
* testes autorizados;
* modelos locais;
* ferramentas de segurança.

Ferramentas previstas:

* Ollama;
* Semgrep;
* Nuclei;
* OWASP ZAP;
* Burp Suite;
* CAI;
* PentAGI;
* PentestGPT;
* scripts próprios;
* devcontainer isolado.

Restrições:

* sem atividade ilegal;
* sem alvos externos sem autorização;
* sem credenciais de produção;
* sem flood/bruteforce fora de escopo;
* sempre com regras de engajamento.

### Provider Router / Fallbacks

O AIW deve suportar múltiplos provedores.

Provedores previstos:

* Anthropic / Claude;
* OpenAI / Codex / ChatGPT;
* Google Gemini / Google AI Pro;
* OpenRouter;
* modelos locais via Ollama.

Estratégia:

* local para laboratório, privacidade e cyber;
* APIs premium para arquitetura, revisão e execução crítica;
* fallback entre provedores para reduzir dependência.

### Nivela Product Ecosystem

O AIW existe para acelerar o ecossistema Nivela.

Produtos atuais/futuros:

* Nivela Core / ERP;
* Nivela Store;
* Nivela Conta / Billing;
* futuros produtos integrados.

Visão:

* ecossistema grande;
* preço acessível;
* produtos integrados;
* lock-in positivo;
* forte retenção;
* alta automação por IA.

---

## Estado atual

### Repositório

Caminho local:

```text
/home/joao/ai-workbench
```

Branch principal:

```text
main
```

Remote:

```text
git@github.com:jrasch7/ai-workbench.git
```

Commits recentes relevantes:

```text
49a3406 scripts: add obsidian vault sync helpers
7089d22 chore: ignore obsidian local app state
e5eca2a docs: validate obsidian local vault smoke
de7d9ae docs: add obsidian operational vault structure
207dec3 docs: clean skill promotion workflow formatting
82263b1 docs: define hermes skill promotion workflow
7108c67 docs: add obsidian knowledge layer foundation
e79fe6b docs: curate hermes telegram smoke tests skill
b738496 docs: add hermes self-improvement governance
```

### Obsidian

Status atual:

* Obsidian instalado no Windows;
* vault local aberto com sucesso;
* nota smoke criada e validada;
* `.obsidian/` ignorado no Git;
* scripts de sincronização criados.

Vault local Windows:

```text
%USERPROFILE%\Documents\AIW-Obsidian-Vault
```

Vault versionado no repo:

```text
docs/obsidian/vault/
```

Scripts de sincronização:

```text
scripts/obsidian-vault-pull-from-repo
scripts/obsidian-vault-push-to-repo
```

Uso:

```bash
scripts/obsidian-vault-pull-from-repo --dry-run
scripts/obsidian-vault-pull-from-repo

scripts/obsidian-vault-push-to-repo --dry-run
scripts/obsidian-vault-push-to-repo
```

### Hermes

Status atual:

* Hermes em uso como agente local;
* Telegram Gateway já foi testado;
* skill de smoke Telegram curada;
* governança de self-improvement criada;
* regra de identidade Git criada;
* skills locais são drafts;
* promoção de skills exige revisão.

Arquivos relevantes:

```text
docs/HERMES_SELF_IMPROVEMENT_GOVERNANCE.md
docs/HERMES_SKILL_PROMOTION_WORKFLOW.md
docs/HERMES_OPERATIONAL_RELIABILITY.md
skills/hermes/telegram-smoke-tests/SKILL.md
skills/hermes/git-safe-workflow/SKILL.md
```

Regra crítica:

Agentes não podem executar:

```bash
git config user.name ...
git config user.email ...
```

---

## Roadmap

### AIW-O1 — Obsidian Operational Foundation

Objetivo: tornar o Obsidian utilizável como camada inicial de conhecimento do AIW.

Status: em andamento, com base operacional validada.

Concluído:

* instalar Obsidian no Windows;
* abrir vault local;
* criar nota smoke;
* validar nota pelo WSL;
* promover nota para o repo;
* ignorar `.obsidian/`;
* criar scripts de sync manual entre Windows e WSL.

Próximos passos:

* documentar os scripts no README;
* decidir Obsidian Git vs Obsidian Sync;
* testar mobile apenas para captura de ideias;
* criar templates centrais no vault.

### AIW-O2 — Knowledge Architecture

Objetivo: estruturar o vault como cérebro do ecossistema Nivela.

Entregas previstas:

* estrutura para marca;
* estrutura para produtos;
* estrutura para domínios;
* PRDs;
* ADRs;
* snapshots;
* handoffs;
* runbooks;
* matriz de ferramentas;
* experiment reports;
* model evaluations;
* agent roles.

Templates previstos:

* PRD;
* ADR;
* snapshot;
* handoff;
* runbook;
* agent role;
* experiment report;
* tool evaluation;
* model evaluation.

### AIW-H1 — Hermes Operational Layer

Objetivo: consolidar Hermes como runtime operacional governado.

Entregas previstas:

* skill segura para escrever no Inbox do Obsidian;
* skill de snapshot;
* skill de handoff;
* skill de validação Git;
* regras de promoção de skills;
* integração controlada com vault;
* relatório de uso dos modelos.

### AIW-R1 — Ralph Harness

Objetivo: validar Ralph como executor iterativo por PRD.

Entregas previstas:

* instalar/testar Ralph TUI;
* criar PRD piloto no Obsidian;
* converter/espelhar PRD para formato consumível pelo Ralph;
* rodar tarefa dummy;
* medir qualidade, custo, tempo e confiabilidade.

### AIW-D1 — Devcontainer Sandbox

Objetivo: criar ambiente seguro para execução de agentes.

Entregas previstas:

* devcontainer base;
* firewall/egress controlado;
* Claude Code dentro do container;
* validação de permissões;
* documentação do padrão;
* regra contra bypass no host.

### AIW-L1 — Ollama Local Model Lab

Objetivo: validar modelos locais no hardware atual.

Entregas previstas:

* instalar Ollama;
* testar modelos pequenos;
* criar matriz de modelos locais;
* avaliar coding, reasoning, resumo, triagem e cyber;
* medir tempo, RAM, VRAM e qualidade;
* decidir quais modelos entram no AIW.

### AIW-P1 — Paperclip Lab

Objetivo: testar Paperclip como control plane de agentes.

Entregas previstas:

* instalar Paperclip;
* criar organização dummy;
* criar agentes dummy;
* testar org chart;
* testar metas/budgets/workers;
* testar dashboard;
* testar `hermes-paperclip-adapter`;
* decidir ring de maturidade.

### AIW-C1 — Cyber Bench Foundation

Objetivo: criar bancada de cibersegurança autorizada.

Entregas previstas:

* política de escopo e autorização;
* regras de engajamento;
* devcontainer isolado;
* ferramentas defensivas;
* Semgrep;
* Nuclei;
* OWASP ZAP;
* Burp Suite;
* modelos locais;
* CAI/PentAGI/PentestGPT em laboratório;
* proibição de credenciais de produção;
* documentação de segurança.

### AIW-N1 — Nivela Ecosystem Integration

Objetivo: conectar AIW à execução real dos produtos Nivela.

Entregas previstas:

* mapear produtos;
* mapear domínios compartilhados;
* criar PRDs por produto;
* criar agentes por produto/domínio;
* conectar decisões de produto com execução;
* criar ciclo contínuo ideia → PRD → execução → validação → documentação.

---

## Matriz de ferramentas

| Ferramenta               | Papel no AIW                 | Ring atual | Status                     | Próximo teste            | Riscos                        |
| ------------------------ | ---------------------------- | ---------: | -------------------------- | ------------------------ | ----------------------------- |
| Obsidian                 | Conhecimento navegável       |     Ring 2 | Instalado e smoke validado | Estruturar vault         | Conflito de sync              |
| Obsidian Git             | Sync Git via plugin          |     Ring 0 | Ainda não configurado      | Testar em desktop        | Conflitos automáticos         |
| Obsidian Sync            | Sync mobile/desktop          |     Ring 0 | Ainda não usado            | Avaliar para mobile      | Custo e duplicidade           |
| Hermes                   | Runtime de agentes           |     Ring 3 | Já usado no AIW            | Integrar com Inbox       | Self-improvement sem controle |
| Telegram Gateway         | Interface remota Hermes      |     Ring 2 | Smoke validado             | Criar runbook final      | Sessões antigas/stale         |
| Paperclip                | Control plane de agentes     |     Ring 0 | Pesquisado                 | Instalar lab             | Maturidade experimental       |
| hermes-paperclip-adapter | Ponte Hermes/Paperclip       |     Ring 0 | Pesquisado                 | Smoke local              | Documentação/maturidade       |
| Ralph Loop               | Execução iterativa por PRD   |     Ring 0 | Pesquisado                 | Testar PRD dummy         | Loop executar tarefa errada   |
| Ralph TUI                | Harness com UI/CLI           |     Ring 0 | Pesquisado                 | Instalar lab             | Integração com PRDs           |
| Dev Containers           | Sandbox de execução          |     Ring 0 | Planejado                  | Criar base               | Configuração insegura         |
| Claude Code              | Executor premium             |     Ring 1 | Usado fora do AIW          | Rodar em container       | Bypass no host                |
| Ollama                   | Modelos locais               |     Ring 0 | Planejado                  | Instalar e medir         | Hardware limitado             |
| OpenRouter               | Roteador/fallback de modelos |     Ring 2 | Usado com Hermes           | Matriz de modelos        | Custo/limite                  |
| Anthropic/Claude         | Modelo premium               |     Ring 1 | Assinatura existente       | Executor em container    | Restrições/custo              |
| OpenAI/Codex             | Modelo premium/dev           |     Ring 1 | Assinatura existente       | Avaliar papel            | Restrições/custo              |
| Google Gemini            | Modelo premium/fallback      |     Ring 2 | Usado via OpenRouter       | Continuar avaliação      | Tool-use variável             |
| Semgrep                  | Análise estática             |     Ring 0 | Planejado                  | Instalar no Cyber Bench  | Falsos positivos              |
| Nuclei                   | Templates de segurança       |     Ring 0 | Planejado                  | Lab autorizado           | Uso fora de escopo            |
| OWASP ZAP                | DAST/open-source             |     Ring 0 | Planejado                  | Baseline em alvo próprio | Configuração ruidosa          |
| Burp Suite               | Validação manual web         |     Ring 0 | Planejado                  | Lab controlado           | Uso manual incorreto          |
| CAI                      | Agente cyber                 |     Ring 0 | Planejado                  | Teste em lab             | Escopo e segurança            |
| PentAGI                  | Agente pentest               |     Ring 0 | Planejado                  | Pesquisa/teste           | Maturidade/risco              |
| PentestGPT               | Assistente pentest           |     Ring 0 | Planejado                  | Pesquisa/teste           | Restrições/qualidade          |
| Cyber Bench              | Bancada de segurança         |     Ring 0 | Planejado                  | Definir política         | Uso sem autorização           |
| Nivela Core              | Produto principal ERP        |     Ring 0 | Mapeamento futuro          | Criar PRDs               | Escopo grande                 |
| Nivela Store             | Produto e-commerce           |     Ring 0 | Mapeamento futuro          | Criar PRDs               | Integração com core           |
| Nivela Conta/Billing     | Produto financeiro/billing   |     Ring 0 | Mapeamento futuro          | Definir domínio          | Risco financeiro/legal        |

---

## Organização de agentes

### Founder / PO / Investor Brain

Papel do João.

Responsável por:

* visão;
* prioridades;
* decisões de negócio;
* aprovação de riscos;
* direção do ecossistema;
* escolha de próximos produtos;
* validação final.

### Orchestrator

Responsável por:

* quebrar objetivos em fases;
* gerar prompts para agentes;
* coordenar execução;
* manter roadmap;
* manter snapshots;
* reduzir perda de contexto.

### Architect

Responsável por:

* arquitetura técnica;
* decisões estruturais;
* trade-offs;
* padrões;
* segurança por design.

### Researcher

Responsável por:

* pesquisar ferramentas;
* validar estado atual;
* comparar alternativas;
* resumir riscos e maturidade.

### Executor

Responsável por:

* implementar tarefas;
* editar arquivos;
* rodar testes;
* entregar handoff com evidência.

### Validator

Responsável por:

* revisar diff;
* validar testes;
* detectar escopo indevido;
* verificar riscos;
* bloquear entrega ruim.

### Integrator

Responsável por:

* consolidar branches;
* preparar commits;
* manter histórico limpo;
* garantir documentação pós-merge.

### Cyber Analyst

Responsável por:

* segurança autorizada;
* análise de vulnerabilidades;
* regras de engajamento;
* validação defensiva;
* laboratório isolado.

### Documentation Curator

Responsável por:

* Obsidian;
* README;
* ROADMAP;
* snapshots;
* decisões;
* handoffs;
* runbooks.

### Model Evaluator

Responsável por:

* testar modelos;
* medir custo;
* medir qualidade;
* avaliar tool-use;
* recomendar uso aprovado por modelo.

---

## Segurança e governança

### Git

Regras:

* sempre verificar `git status --short`;
* usar `git add -N` para arquivos novos antes de revisar diff;
* validar `git diff --check`;
* validar `git diff --stat`;
* revisar diff antes de commit;
* não fazer commit/push sem autorização.

Agentes nunca podem rodar:

```bash
git config user.name ...
git config user.email ...
```

### Obsidian

Regras:

* não salvar secrets;
* não salvar `.env`;
* não salvar tokens;
* não salvar chaves privadas;
* não salvar dados sensíveis de clientes;
* notas novas de agentes devem entrar primeiro no Inbox;
* decisões precisam de revisão antes de serem promovidas.

### Hermes

Regras:

* self-improvement permitido;
* promoção automática proibida;
* skills locais são drafts;
* regras críticas ficam em Git;
* skills que enfraquecem segurança devem ser rejeitadas.

### Cyber Bench

Regras:

* somente ambientes próprios ou autorizados;
* sem produção sem autorização explícita;
* sem credenciais reais;
* sem destruição;
* sem flood/bruteforce fora de escopo;
* sempre registrar escopo, alvo, autorização e evidências.

### Devcontainers

Regras:

* execução permissiva apenas em sandbox;
* nunca usar bypass no host;
* restringir egress;
* não montar credenciais sensíveis;
* separar projetos/produtos.

---

## Critérios de sucesso

O AIW será considerado bem-sucedido quando:

* um novo agente conseguir retomar contexto em poucos minutos;
* decisões importantes estiverem rastreadas;
* PRDs virarem execução real;
* execução gerar handoff verificável;
* validação independente detectar erros;
* ferramentas forem promovidas por evidência, não por hype;
* modelos forem escolhidos por matriz de qualidade/custo;
* Obsidian e Git trabalharem juntos sem conflito;
* o usuário reduzir trabalho operacional repetitivo;
* Nivela ganhar velocidade real de desenvolvimento.

---

## Próximas ações imediatas

1. Documentar oficialmente os scripts de sync do Obsidian.
2. Criar `ROADMAP.md` versionado no repo.
3. Criar snapshot atual dentro do vault.
4. Estruturar AIW-O2 — Knowledge Architecture.
5. Criar templates PRD, ADR, snapshot, handoff e experiment report.
6. Decidir Obsidian Git vs Obsidian Sync.
7. Testar Obsidian mobile apenas para captura.
8. Planejar primeiro teste Ralph.
9. Planejar primeiro teste Paperclip.
10. Planejar instalação Ollama e matriz de modelos locais.
11. Definir política inicial do Cyber Bench.
12. Mapear produtos Nivela no vault.

---

## Snapshot atual

```markdown
# SNAPSHOT_AIW — current

## Estado atual

O AI Workbench está sendo estruturado como bancada/fábrica de IA do ecossistema Nivela.

Já foram concluídos:

- base de governança Hermes;
- skill de smoke Telegram curada;
- fluxo de promoção de skills;
- vault Obsidian versionado;
- Obsidian instalado no Windows;
- vault local Windows validado;
- nota smoke criada e promovida para Git;
- `.obsidian/` ignorado;
- scripts de sync manual entre Windows e WSL criados.

Último commit relevante:

- `49a3406 scripts: add obsidian vault sync helpers`

## Próxima ação

Criar e versionar o `ROADMAP.md` do AIW.

Depois seguir para AIW-O2: Knowledge Architecture do vault.

## Bloqueios

Nenhum bloqueio técnico crítico no momento.

Pendências:

- decidir Obsidian Git vs Obsidian Sync;
- documentar scripts de sync;
- testar Ralph;
- testar Paperclip;
- testar Ollama;
- definir política Cyber Bench.

## Perguntas abertas

- O knowledge base ficará para sempre dentro do AIW ou terá repo separado?
- Obsidian mobile será via Obsidian Sync?
- Qual orçamento mensal real para APIs?
- Qual será o primeiro projeto real após AIW piloto?
- Quais limites iniciais do Cyber Bench?
```

---

## Comandos úteis

Validar repo:

```bash
cd ~/ai-workbench
git status --short
git log --oneline -5
```

Sincronizar repo para Obsidian Windows:

```bash
cd ~/ai-workbench
scripts/obsidian-vault-pull-from-repo --dry-run
scripts/obsidian-vault-pull-from-repo
```

Sincronizar Obsidian Windows para repo:

```bash
cd ~/ai-workbench
scripts/obsidian-vault-push-to-repo --dry-run
scripts/obsidian-vault-push-to-repo
```

Validações antes de commit:

```bash
git status --short
git diff --check
git diff --stat
```

---

## Regra de ouro

O AIW deve crescer como uma bancada confiável, auditável e evolutiva.

A meta não é ter várias ferramentas bonitas instaladas. A meta é formar uma operação real de agentes capaz de transformar visão estratégica em produto funcionando, com segurança, documentação e validação.
