# AIW Context Resilience Roadmap

## Objetivo
Estabelecer um plano de entrega incremental para a **Phase 7.6 — Context Resilience / Auto‑Compaction**. O objetivo é tornar o AIW resiliente a sessões de longo prazo, limites de taxa (429) e falhas de modelo, garantindo que o estado de execução seja persistido e retomável.

## Modelo de Fonte de Verdade
- **Modelo**: não é fonte de verdade; serve apenas para gerar respostas a partir de prompt curto.
- **Git / Disco**: fontes definitivas de verdade para código, artefatos e estado de run.
- **Prompt**: deve permanecer curto, contendo apenas o necessário para a próxima operação.
- **Run State**: deve ser salvo em `reports/aiw‑runs/<run_id>/` (ver Phase 7.6 PRD).
- **`/new`**: deve ser usado quando o contexto da sessão ultrapassar limites operacionais.

---

## Fases (CR‑X)
| Fase | Objetivo | Entregáveis | Dependências | Critério de Pronto | Riscos |
|------|----------|-------------|--------------|--------------------|-------|
| **CR‑0** | Política operacional manual | Documento de procedimento interno | Nenhuma | Aprovação de equipe de ops | Falta de adesão inicial |
| **CR‑1** | Formato padrão de run state | Diretório `reports/aiw‑runs/<run_id>/` com `metadata.json`, `prompt.md`, `commands.log`, `outputs.log`, `diff.patch`, `validation.json`, `handoff.md`, `compact_summary.md`, `resume_next_prompt.md` | Definir especificação de arquivos | Todos os arquivos acima presentes e validados por schema JSON | Sobrecarga de I/O |
| **CR‑2** | Compact summary automático | Script `compact_summary_generator` que gera `compact_summary.md` a partir de `metadata.json` e logs | CR‑1 | Resumo < 1 k tokens, aprovado por teste unitário | Perda de detalhes críticos |
| **CR‑3** | Resume prompt automático | Gerador `resume_prompt_builder` produz `resume_next_prompt.md` contendo apenas informações essenciais | CR‑1, CR‑2 | Prompt < 500 tokens, contém SHA de estado e ação próxima | Falha ao incluir contexto necessário |
| **CR‑4** | Fallback de modelo | Política que detecta erro 429, troca para modelo secundário (`gpt‑4o‑mini`), registra mudança em `metadata.json` | Nenhuma | Troca bem‑sucedida demonstrada em teste de carga | Custos adicionais, variação de respostas |
| **CR‑5** | Integração com LangGraph checkpoint | Adaptação do `Run State Store` para ser usado como backend de checkpoint do LangGraph | CR‑1 | Checkpoints serializados como `checkpoint_<step>.json` no diretório da run | Complexidade de integração |
| **CR‑6** | Integração com RAG (LangChain) | Implementação de RAG que consulta arquivos de run (`reports/aiw‑runs/*`) e `docs/` | CR‑1 | Busca correta e registro em `outputs.log` | Latência adicional |
| **CR‑7** | UI no Cockpit para retomar run | Nova view no Cockpit listando runs disponíveis, botão *Resume* que carrega `resume_next_prompt.md` e estado | CR‑1‑CR‑4 | Usuário pode retomar com 1‑click, sem erro | UI/UX inconsistências |

---

## Notas Gerais
- Cada fase será desenvolvida em branch feature própria e mesclada após validação.
- O plano inclui testes automatizados que verificam a criação correta dos artefatos e a capacidade de retomar a partir de `resume_next_prompt.md`.
- A documentação será mantida atualizada no repositório `docs/roadmap/`.

---

*Este roadmap serve como guia de implementação para a estratégia de resiliência de contexto do AIW.*