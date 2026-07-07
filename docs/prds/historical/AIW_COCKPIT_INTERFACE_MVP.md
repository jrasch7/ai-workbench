# PRD: AIW Cockpit Interface MVP

**Objetivo**

Entregar uma interface mínima (MVP) no AIW Cockpit que permita aos usuários operacionais monitorar e interagir com runs de agentes, analisar resultados e aprovar/rejeitar mudanças antes de mesclar ao código.

**Usuários-alvo**

- Engenheiros de software que criam missões/agents.
- Gerentes de projeto que revisam handoffs e validam entregas.
- QA/Validador que executa checks automáticos.

**Problemas a resolver**

- Falta de visualização consolidada de runs (status, logs, diffs).
- Necessidade de aprovar/rejeitar mudanças com base em handoff e validações.
- Ausência de página de detalhe que mostre artefatos gerados (metadata, diff, handoff, validation).

**Telões mínimas (MVP)**

1. **Home / Dashboard** – resumo de métricas rápidas: número de runs hoje, runs pendentes, últimos erros.
2. **Runs List** – tabela paginada com colunas: Run ID, Agente, Timestamp, Status (pending/review/approved/rejected), Botão "Detalhes".
3. **Run Detail** – ao abrir, mostra:
   - `metadata.json` (ID, agente, parâmetros)
   - Log (texto com realce de erros)
   - Diff Summary (conteúdo de `diff_summary.txt`)
   - Handoff (`handoff.md` renderizado)
   - Validação (`validation.json` checklist visual)
   - Botões **Aprovar** / **Rejeitar** que gravam `analysis.json`.
4. **Analysis / Handoff / Validator** – telas embutidas em Run Detail para facilitar navegação.

**Contratos de dados (artefatos esperados)**

| Artefato | Formato | Campo(s) chave |
|----------|---------|----------------|
| `metadata.json` | JSON | `run_id`, `agent`, `timestamp`, `parameters` |
| `log` | Texto | – |
| `diff_summary.txt` | Texto | – |
| `handoff.md` | Markdown | – |
| `validation.json` | JSON | `run_id`, `checks[]`, `overall` |
| `analysis.json` | JSON (gerado pelo Cockpit) | `run_id`, `status`, `approver`, `comments`, `timestamp` |

**Requisitos Não Funcionais**

- **Segurança** – apenas usuários autenticados podem acionar aprovação; nunca exibir credenciais ou secrets.
- **Performance** – carregamento de detalhes < 2 s para runs com até 10 k linhas de log.
- **Responsividade** – UI adaptada para desktop e tablets.
- **Auditoria** – todas as decisões (aprovar/rejeitar) são registradas em `analysis.json` e versionadas via Git.

**Estados esperados**

- `pending` – run criada, sem análise.
- `review` – artefatos disponíveis, aguardando ação do usuário.
- `approved` – usuário aprovou; pronto para merge.
- `rejected` – usuário rejeitou; requer correções.

**Erros esperados**

- Falha ao carregar log → mensagem *"Não foi possível ler o log da execução"*.
- Validação falhou → interface desabilita o botão **Aprovar** e exibe lista de falhas.
- Operação de aprovação falha (ex.: permissões Git) → aviso ao usuário e registro no log.

**Fora de escopo**

- Integração com LangSmith, Provider Router, Worktree visual, RAG visual – serão desenvolvidas em fases posteriores.
- Criação de novos agentes ou lógica de negócio – foco apenas na UI de visualização/gerenciamento.

**Critérios de Aceite**

1. Dashboard exibe contadores corretos de runs por status.
2. Lista de runs mostra todos os runs recentes e permite filtro por agente/status.
3. Ao abrir um run, todos os artefatos listados acima são carregados e exibidos.
4. Botões **Aprovar** e **Rejeitar** gravam `analysis.json` com estado correto e são persistidos no repositório.
5. Aprovação impede merge se `validation.json` = `failed` (botão desabilitado).
6. UI passa testes de acessibilidade básicos e funciona em Chrome/Firefox.

**Plano de Validação Manual**

- Criar três runs de teste (uma bem‑sucedida, uma com lint falho, uma com falha de testes).
- Verificar que o Cockpit exibe os runs, diffs, handoffs e validações corretas.
- Aprovar a run bem‑sucedida, rejeitar as outras; confirmar que `analysis.json` foi criado com status correto.
- Revisar o histórico Git para garantir que os commits de `analysis.json` aparecem.

**Plano de Validação Automatizada (futuro)**

- Testes end‑to‑end (Cypress) que simulam fluxo completo de criação de run, visualização, aprovação e verificação de artifacts versionados.
- Integração CI que falha se `analysis.json` não for criado para runs marcados como `approved`.
