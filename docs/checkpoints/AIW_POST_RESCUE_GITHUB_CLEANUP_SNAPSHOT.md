# AIW Post-Rescue GitHub Cleanup Snapshot

**Data/Hora local:** 2026-06-25 13:13:15 -03

## Estado Git final

- **main SHA:** `7df10f4`
- Working tree limpa
- Smoke LangGraph na main: **OK**
- Branches remotas restantes:
  - `origin/main`
  - `origin/rescue/old-pc-cockpit-20260623`

## PRs consolidados

- PR #7 — docs foundation
- PR #8 — AIW Cockpit UI prototype
- PR #9 — rescued Cockpit/runner core
- PR #10 — LangGraph runtime smoke fix
- PR #11 — AIW run task runbook

## O que foi resgatado do outro PC

- Branch rescue preservada (`origin/rescue/old-pc-cockpit-20260623`)
- Core importado para `main` via PR #9
- Runtime corrigido via PR #10
- Docs/runbook salvo via PR #11

## O que foi limpo

- Branches integradas deletadas
- Worktrees temporários removidos
- GitHub reduzido para `main` + rescue

## O que foi preservado

- `origin/rescue/old-pc-cockpit-20260623`
- Checkpoints em `/home/joao/aiw-checkpoints/`

## Decisão sobre Fugu

- Fugu é promissor, mas pago
- Não integrar agora
- Pode entrar futuramente como candidato de benchmark pago
- Foco imediato em modelos grátis/free‑tier

## Próxima fase recomendada

- **AIW Model Bench & Routing Matrix**

## Escopo da próxima fase

- Mapear provedores gratuitos/free‑tier
- Criar matriz de modelos por função
- Definir harness de benchmark
- Comparar modelos por tarefa:
  - planner
  - executor/coder
  - reviewer
  - validator
  - summarizer/context builder
- Medir:
  - qualidade
  - custo
  - latência
  - aderência às regras Git
  - alucinação de arquivos/comandos
  - estabilidade operacional

## Regras permanentes

- Não executar comandos destrutivos sem autorização
- Não mexer direto na `main`
- Sempre usar branch/worktree para novas mudanças
- Sempre validar smoke antes de merge
- Sempre documentar decisões importantes
