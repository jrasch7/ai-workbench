# ADR: Phase 7.5 before Worktree/RAG

**Status:** Accepted

## Contexto

- A arquitetura atual define a pilha de agentes e um roadmap que inclui, em sequência, Phase 7.5 (UI de análise), Phase 8 (worktree/sandbox) e Phase 9 (LangChain RAG).
- O Cockpit já suportava execução de runs, mas ainda não exibia diff, handoff e validações de forma integrada.
- A equipe tem código em progresso nas fases 6.5/7 no PC antigo, que ainda não foi resgatado.
- Avançar diretamente para Phase 8 ou 9 implicaria operar em um ambiente de trabalho isolado ou de recuperação de contexto antes de ter visibilidade clara das análises e validações.

## Decisão

**Concluir a Phase 7.5 (UI de análise) antes de iniciar a Phase 8 (Worktree/Sandbox) e a Phase 9 (RAG/Context Engine).**

### Motivo

1. **Visibilidade de qualidade** – A UI de análise fornece diff, handoff e validações que permitem aos desenvolvedores confirmar a correção das mudanças antes de executar isolaç\ão (worktree) ou indexação de documentos (RAG).
2. **Redução de risco** – Sem a análise completa, o worktree poderia gerar diffs que não foram validados, elevando o risco de introduzir bugs ao merge.
3. **Dependência de contrato** – Os contratos definidos em `AIW_ANALYSIS_HANDOFF_VALIDATOR_CONTRACTS.md` são pré-requisitos para que o worktree e o RAG consumam artefatos consistentes.
4. **Alinhamento com estratégia** – O roadmap indica que a UI de análise prepara os usuários para tomar decisões informadas antes de avançar para funcionalidades mais complexas.

## Consequências positivas

- A equipe terá uma camada de revisão visual antes de experimentar worktrees ou indexação, reduzindo retrabalho.
- Os artefatos de análise ficarão padronizados, facilitando a integração futura com LangChain e o provider router.
- Melhor experiência de usuário no Cockpit, mantendo coerência com a visão Devin‑like.

## Consequências negativas

- Pequeno atraso no início da experimentação de worktrees e RAG, pois a UI de análise precisa ser desenvolvida e validada primeiro.
- Necessidade de esforço extra de UI para exibir diff e handoff de forma amigável.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|-------------|------|----------|
| Ir direto para Worktree (Phase 8) | Começar a testar isolamento de código cedo | Falta de validação visual pode levar a merges problemáticos |
| Ir direto para RAG (Phase 9) | Aproveitar imediatamente a camada de contexto | Depende de contratos ainda não definidos; risco de divergência de dados |
| Instalar Paperclip como executor | Poderia simplificar execução de código | Violação das regras críticas (não usar Paperclip) |
| Testar Ralph (orquestrador avançado) | Avaliar solução robusta de gerenciamento de recursos | Fora do escopo atual, alta complexidade, sem necessidade imediata |
| Fine‑tuning agora | Melhor desempenho de modelo | Requer dataset real, alto custo, fora do escopo atual |

## Critério para revisar a decisão

- Se a UI de análise for concluída e aceita (PRD cumprido, validações passarem) **e** a equipe precisar urgentemente isolar alterações críticas, pode‑se reavaliar a ordem.
- Qualquer alteração nas dependências (ex.: mudança de provedor de modelo que impacte a UI) exigirá nova avaliação de risco.
