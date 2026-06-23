# AIW Analysis/Handoff/Validator Contracts

## Visão geral

Esta especificação define os **contratos** que o **Cockpit** (UI), o **Validator** e o **Handoff** devem trocar para garantir análise consistente, rastreável e segura das execuções (runs) de agentes.

## Artefatos de um run

| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `metadata.json` | JSON | Metadados da missão (id, timestamp, agente, parâmetros). |
| `log` | Texto | Log bruto da execução (stdout + stderr). |
| `diff_summary.txt` | Texto | Resumo legível por humanos das mudanças (`git diff --stat`). |
| `diff_full.patch` | Texto | Patch completo em formato `git apply`‑compatible. |
| `handoff.md` | Markdown | Resumo da run, recomendações, risco, próximo passo. |
| `validation.json` | JSON | Resultado das validações automáticas (tests, lint, secret‑scan). |
| `analysis.json` | JSON | Decisão do analista (status, comentários, aprovador). |

## Campos mínimos de `analysis.json`
```json
{
  "run_id": "string",
  "status": "pending|review|approved|rejected",
  "approver": "optional string",
  "comments": "optional string",
  "timestamp": "ISO8601"
}
```

## Campos mínimos de `validation.json`
```json
{
  "run_id": "string",
  "checks": [
    {"name": "lint", "result": "passed|failed", "details": "..."},
    {"name": "tests", "result": "passed|failed", "details": "..."},
    {"name": "secret_scan", "result": "passed|failed", "details": "..."}
  ],
  "overall": "passed|failed",
  "timestamp": "ISO8601"
}
```

## Formato recomendado de `handoff.md`
```
# Handoff – Run <run_id>

## Resumo
- **Objetivo**: …
- **Resultado**: …

## Diff Summary
```
<conteúdo de diff_summary.txt>
```

## Validações
- Lint: passed
- Tests: passed
- Secret scan: passed

## Riscos identificados
- …

## Próximos passos
- …
```

## Status permitidos (em `analysis.json`)
- `pending` – run criada, ainda sem análise.
- `review` – diff/handoff/validator disponíveis.
- `approved` – aprovado para merge.
- `rejected` – rejeitado; necessidade de correções.

## Status proibidos
- `merged` – a decisão de merge deve ser feita fora do Cockpit (por integrador).
- `deleted` – run removida sem registro de análise.

## Regras de compatibilidade
- **LangGraph** deve gerar todos os artefatos acima antes de sinalizar `status: review`.
- **Hermes Executor** garante que `validation.json` contenha somente resultados *pass* ou *fail*; *fail* impede transição para `approved`.
- **Cockpit** consome os arquivos como *read‑only*; não deve alterar `diff_full.patch` ou `validation.json`.
- **Validator** pode bloquear a passagem para `approved` quando `validation.overall` = `failed`.

## Como o Cockpit consome os dados
1. Ao abrir um run, lê `metadata.json` → exibe detalhes da missão.
2. Carrega `log` → apresenta visualização com realce de erros.
3. Lê `diff_summary.txt`/`diff_full.patch` → exibe diff colorido.
4. Exibe `handoff.md` renderizado.
5. Consulta `validation.json` → mostra checklist de validações.
6. Permite ao usuário gravar `analysis.json` com decisão final.

## Como o Validator bloqueia entrega ruim
- Se `validation.overall` = `failed`, a UI desabilita o botão **Aprovar** e exibe mensagens de erro.
- O Validator pode opcionalmente adicionar campos `blocking_issues` em `validation.json` listando arquivos críticos que precisam correção antes de aprovação.

## Riscos de contrato instável
- Alterações de schema sem versionamento podem quebrar a UI.
- Dependência implícita em caminhos fixos (`/tmp/aiw/run/<run_id>/`) → usar caminhos configuráveis.
- Falha ao gerar artefatos (ex.: `diff_full.patch` ausente) → validar antes de mudar de `pending` para `review`.

## Estratégia de mitigação
- Versionar o contrato via *semantic version* no cabeçalho de `metadata.json` (ex.: `"contract_version": "1.0"`).
- Testar backward compatibility em CI antes de atualizar o contrato.
- Documentar alterações de contrato em ADRs para rastreabilidade.
