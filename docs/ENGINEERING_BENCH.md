# Engineering Bench — AI Workbench

## Visão

O AI Workbench não é um experimento de agente. É uma bancada de engenharia de software para operar projetos reais com apoio de IA, Git, contexto, validação e modelos LLM intercambiáveis.

A meta é reduzir dependência de várias plataformas isoladas e criar uma base própria, controlável e evolutiva para desenvolvimento assistido por agentes.

## Princípio central

A plataforma deve continuar útil mesmo quando o modelo LLM for trocado.

O modelo é uma peça da arquitetura, não a arquitetura inteira.

## Objetivo prático

A bancada deve conseguir executar fluxos reais como:

- entender contexto de um projeto;
- planejar uma tarefa;
- editar arquivos com escopo claro;
- rodar validações;
- revisar diff;
- gerar handoff;
- preparar commit, push e PR quando autorizado.

## Projetos alvo

A plataforma deve ser aplicável a projetos reais como:

- Nivela;
- SisOpERP Web;
- futuras plataformas SaaS;
- projetos internos de automação e engenharia.

## Componentes da bancada

### 1. Ambiente local

Base operacional previsível:

- WSL2;
- Ubuntu;
- Docker;
- Git;
- OpenHands;
- LiteLLM;
- repositórios montados como workspace real.

### 2. Gateway de modelos

O LiteLLM será o ponto central para acesso a modelos.

Motivo:

- trocar modelos sem alterar agente;
- criar aliases por finalidade;
- permitir fallback;
- controlar custo;
- separar provider de fluxo operacional.

Aliases planejados:

```text
dev-fast
dev-coder
dev-review
dev-architect
dev-premium
```

### 3. Agentes operacionais

A bancada deve separar papéis.

```text
architect -> executor -> validator -> integrator
```

Cada agente tem escopo e limite.

Nenhum agente deve atuar como dono absoluto da tarefa.

### 4. Contexto por projeto

Cada projeto precisa ter contexto próprio:

- stack;
- regras de negócio;
- módulos críticos;
- comandos de validação;
- padrões de Git;
- áreas proibidas;
- riscos conhecidos;
- decisões técnicas.

Sem contexto bom, mesmo uma LLM boa vira chute.

### 5. Validação obrigatória

A saída do agente nunca é fonte de verdade.

Fontes de verdade:

- git status;
- git diff;
- testes;
- logs;
- build;
- lint;
- comportamento observado.

## Diferença entre plataforma e modelo

OpenHands é a camada operacional.

LiteLLM é o gateway.

A LLM é o cérebro.

Docker é o ambiente de execução.

Git é o controle de realidade.

Documentação e templates são o contrato operacional.

## Estado atual

O ambiente já validou:

- LiteLLM local respondendo;
- OpenRouter via LiteLLM;
- OpenHands conectado ao LiteLLM;
- sandbox criando arquivo em workspace;
- uso de workspace isolado;
- uso de repositório real como workspace;
- problemas de permissão corrigidos com conversations e bash_events.

## Limitações atuais

Modelos gratuitos são apenas laboratório.

Problemas observados:

- rate limit upstream;
- lentidão;
- raciocínio inconsistente;
- erro em tool call;
- JSON inválido;
- falsa validação;
- dificuldade com tarefas grandes.

Conclusão: modelo free não deve ser usado como base de produção da bancada.

## Direção correta

A evolução deve acontecer em fases.

### Fase 1 — Infra sólida

Objetivo: tudo sobe, para, valida e reinicia de forma previsível.

Entregas:

- scripts confiáveis;
- comando doctor;
- setup reproduzível;
- troubleshooting real;
- limpeza de containers;
- permissões resolvidas;
- documentação operacional enxuta e correta.

### Fase 2 — Workspaces por projeto

Objetivo: rodar a bancada em projetos reais sem confusão de pastas.

Entregas:

- modo repo;
- modo current;
- isolamento de workspaces;
- padrões por projeto;
- exclusões locais para arquivos temporários.

### Fase 3 — Agentes formais

Objetivo: transformar uso solto em processo de engenharia.

Entregas:

- architect;
- executor;
- validator;
- integrator;
- templates de tarefa;
- templates de validação;
- templates de handoff.

### Fase 4 — Modelos confiáveis

Objetivo: substituir laboratório free por modelos úteis.

Entregas:

- alias por papel;
- fallback;
- roteamento por custo;
- modelo forte para arquitetura;
- modelo forte para código;
- modelo forte para revisão.

### Fase 5 — Operação real

Objetivo: aplicar no Nivela e SisOpERP Web.

Entregas:

- primeira tarefa real pequena;
- medição de qualidade;
- tempo gasto;
- custo;
- falhas;
- melhorias no processo.

## Critério de qualidade

Não basta o agente responder bonito.

A bancada só é boa quando:

- reproduz setup em outro PC;
- não perde arquivos;
- não vaza segredo;
- respeita Git;
- valida antes de concluir;
- permite revisar tudo;
- permite trocar modelo;
- reduz trabalho real em projetos reais.

## Decisão estratégica

Não vamos construir algo mediano apenas para dizer que existe.

Se uma peça não serve, ela será trocada.

Se um modelo não presta, ele será tratado como laboratório.

Se um fluxo gera erro, ele será simplificado e estabilizado.

A meta é uma plataforma de engenharia robusta, não uma demonstração frágil.
