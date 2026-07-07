# PRD: Phase 7.5 – UI de Análise do Cockpit

**Objetivo**

Fornecer ao Cockpit uma interface visual que permita aos usuários analisar execuções (runs) de agentes, visualizar diffs, handoffs e validar resultados antes de mesclar alterações.

**Problema**

- Atualmente o Cockpit lista apenas runs e logs; não há suporte a visualização estruturada de diff e handoff.
- Falta de validação automática impede que usuários identifiquem rapidamente riscos ou falhas nas mudanças propostas.

**Contexto da Phase 6.5/7**

- Phase 6.5 realizou hardening da execução e coleta de métricas.
- Phase 7 introduziu o fluxo de handoff/validator, mas a UI ainda não exibe esses artefatos de forma integrada.

**Fluxo esperado no Cockpit**

1. **Listar runs** – página principal apresenta todas as execuções recentes.
2. **Abrir run** – ao selecionar, mostra detalhes da missão.
3. **Visualizar status** – indica sucesso, falha ou necessidade de revisão.
4. **Visualizar log** – acesso ao log bruto da execução.
5. **Acionar “Analisar run”** – gera análise de diff e handoff.
6. **Exibir Diff Summary** – visualização colorida de adições/removers.
7. **Exibir Handoff** – documento Markdown com resumo, recomendações e próximos passos.
8. **Exibir Validator** – resultados de validações automáticas (testes, lint, checks).
9. **Exibir riscos e próximos passos** – listagem de possíveis impactos e ações a serem tomadas.

**Requisitos Funcionais**

- UI deve consumir artefatos gerados pelo `Validator` (`validation.json`) e `Handoff` (`handoff.md`).
- Exibir diff resumido (`diff_summary.txt`) e permitir download do diff completo.
- Botão “Aprovar”/”Rejeitar” que grava decisão no `analysis.json`.
- Histórico de análises armazenado em `metadata.json`.

**Requisitos Não Funcionais**

- Responsividade: funciona em desktop e tablets.
- Tempo de carregamento < 2 s para runs com até 10 k linhas de log.
- Segurança: apenas usuários autenticados podem acionar análise.

**Estados Esperados**

- `pending` – run criada, sem análise.
- `analyzing` – análise em progresso.
- `review` – diff/handoff/validator disponíveis.
- `approved` / `rejected` – decisão final gravada.

**Erros Esperados**

- Falha ao gerar diff → mensagem *"Diff generation failed, contacte o desenvolvedor"*.
- Arquivo de handoff ausente → alerta de *"Handoff missing; abort analysis"*.
- Validação falha → exibir lista de falhas e bloquear aprovação.

**Fora de Escopo**

- Implementação de Phase 8 worktree/sandbox.
- Integração com LangChain RAG (Phase 9).
- Fine‑tuning de modelos.

**Critérios de Aceite**

- UI mostra lista de runs e permite abrir detalhes.
- Botão “Analisar run” gera diff e handoff dentro de 5 s.
- Validações automáticas são exibidas e, se falharem, impedem aprovação.
- Decisão de aprovação gera `analysis.json` com campo `status` = `approved`.

**Plano de Validação Manual**

1. Criar run de teste (script dummy) que gera diff, handoff e validation.
2. Verificar que UI lista o run e exibe todos artefatos.
3. Aprovar e rejeitar manualmente, confirmar gravação de `analysis.json`.

**Plano de Validação Automatizada Futuro**

- Testes end‑to‑end com Cypress que simulam fluxo completo e verificam estado final.
- Integração CI que garante que a UI compile sem regressões.
