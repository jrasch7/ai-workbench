# ADR: AIW LangGraph + LangChain Stack

**Status:** Accepted

## Contexto

O AI Workbench evolui para suportar pipelines de engenharia de software baseados em agentes. Precisamos de um motor de orquestração confiável, ao mesmo tempo em que queremos aproveitar recursos de recuperação de contexto e integração com ferramentas externas.

## Decisão

- **LangGraph** será o motor de execução de fluxos (orquestração de nós, ciclos e controle de estado).
- **LangChain** será a camada de RAG / tools / retrievers / loaders, fornecendo acesso a documentos, bases de conhecimento e APIs externas.
- **Hermes** continuará como executor local responsável por rodar ferramentas, scripts e comandos de shell dentro do ambiente controlado.
- **Cockpit** permanecerá como UI operacional para criação e monitoramento de missões.
- **Obsidian/Git** será a fonte de verdade documental, armazenando ADRs, PRDs, runbooks e outros artefatos.

## Consequências

- A arquitetura separa claramente orquestração (LangGraph) de acesso a contexto (LangChain), facilitando testes e substituição futura de componentes.
- Reduzimos dependências de frameworks de multi‑agente (CrewAI, AutoGen) que ainda não são necessários.
- Mantemos a flexibilidade para introduzir novos provedores de modelo via **Provider Router** sem mudar a lógica de orquestração.

## Alternativas Consideradas

| Alternativa | Prós | Contras |
|-------------|------|----------|
| **Só Hermes** (sem camada de orquestração) | Simplicidade, menos dependências | Falta de suporte a grafos complexos, controle de estado limitado |
| **Só LangChain** (usar como executor) | Unifica orquestração e RAG | LangChain não foi projetado como motor de execução de loops complexos |
| **CrewAI** | Suporte nativo a multi‑agente | Ainda experimental, alto overhead, integração limitada com Hermes |
| **AutoGen** | Similar ao CrewAI, foco em colaboração entre agentes | Não alinhado com nossa arquitetura de missão/run manager |
| **LlamaIndex** | Forte foco em indexação/documentos | Não cobre orquestração de passos de engenharia |
| **Fine‑tuning agora** | Pode melhorar desempenho de modelo | Requer dataset real, risco de sobre‑ajuste, fora do escopo imediato |

## Motivo da Escolha

A combinação **LangGraph + LangChain + Hermes** oferece a melhor separação de responsabilidades, reutilização de código existente e menor risco de introduzir dependências complexas. Essa stack atende aos requisitos de orquestração determinística e acesso a contexto rico, permitindo evolução incremental nas próximas fases.
