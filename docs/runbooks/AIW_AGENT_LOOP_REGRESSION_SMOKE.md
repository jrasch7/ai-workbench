# AIW Agent Loop Regression Smoke

## Objetivo

O regression smoke do Agent Loop valida, de forma local e offline, que o Agent Iterative Loop v1 continua respeitando os contratos de safety entregues nas sprints AIW-CAP-06.x.

Ele cobre CLI, dry-run, execute confirmado, policy, path hygiene, traversal e, opcionalmente, os endpoints read-only do Cockpit.

## Comando

Smoke padrao, sem Cockpit:

```bash
./scripts/aiw-agent-loop-regression-smoke --workspace aiw
```

Smoke com Cockpit read-only em localhost:

```bash
./scripts/aiw-agent-loop-regression-smoke --workspace aiw --with-cockpit --cockpit-port 18769
```

Por default o Cockpit e pulado. Quando `--with-cockpit` e usado, o harness inicia `./scripts/aiw-cockpit` como processo foreground controlado, usa apenas `GET` em `127.0.0.1`, e encerra o processo ao final.

No artifact, isso e registrado como:

```text
external_network_used=false
localhost_http_used=true
cockpit_smoke_used=true
```

Sem `--with-cockpit`, o smoke registra:

```text
external_network_used=false
localhost_http_used=false
cockpit_smoke_used=false
```

`localhost_http_used=true` nao significa rede externa. Ele indica somente GETs locais para `127.0.0.1`.

## Artifacts

Cada execucao grava:

```text
.aiw/workspaces/<workspace_id>/agent-loop-regression/runs/<run_id>/
```

Arquivos:

```text
run.json
summary.md
checks/*.json
```

`run.json` inclui:

```text
run_id
workspace_id
created_at
status
checks_total
checks_passed
checks_failed
llm_real_used=false
external_write_used=false
daemon_used=false
external_network_used=false
localhost_http_used=false|true
cockpit_smoke_used=false|true
unsafe_broad_search_used=false
validation_search_scope=explicit_paths_only
generated_agent_loop_runs
isolation_boundary
```

Cada check em `checks/*.json` registra `name`, `status`, `command`, `expected`, `observed` e `error`. Saidas de subprocess ficam truncadas em previews; o harness usa a saida completa apenas em memoria para parsear JSON.

## Checks

O smoke padrao valida:

- `./scripts/aiw-agent-loop --help`.
- `--dry-run --max-iterations 3` cria tres iteracoes.
- Dry-run nao gera `codeact_run_id`.
- `--execute` sem confirmacao bloqueia com `confirmation_required`.
- `--execute --confirm-agent-loop` conclui e registra `codeact_run_id`.
- `--max-iterations 99` bloqueia.
- Capability ausente bloqueia com `capability_missing`.
- Operation desconhecida bloqueia com `unknown_operation`.
- Policy direta cobre dry-run simulado, offline sem confirmacao, offline confirmado, modo `llm` bloqueado e operation desconhecida.
- `run.json` novo e leitura endpoint-like nao expõem `/home/joao/` e usam paths relativos.
- Leitura de run rejeita traversal como `../x`, `/tmp/x` e traversal codificado.

Com `--with-cockpit`, tambem valida que o Cockpit responde via GET local nos endpoints de lista/detalhe read-only do Agent Loop. A pagina inicial do Cockpit e amostrada quando responde dentro do timeout; com muitos artifacts locais, os endpoints JSON continuam sendo o contrato obrigatorio do smoke.

## Fronteira de Isolamento

O smoke e local/offline:

- Sem LLM real.
- Sem GitHub/Jira write.
- Sem daemon persistente.
- Sem Docker.
- Sem `curl` ou `wget`.
- Sem browser automation.
- Sem `shell=True`.
- Sem processo em background persistente.
- Sem rede externa. O modo `--with-cockpit` usa apenas HTTP localhost em `127.0.0.1`.

O CodeAct continua sendo host-sandbox best-effort. Ele e exercitado apenas pelo caminho seguro existente do Agent Loop, com codigo fixo e confirmacao explicita.

## Busca Escopada

Para validar texto do projeto, use paths explicitos e nao varra o repositorio inteiro. Validacao textual nunca deve usar busca ampla quando houver risco de varrer secrets.

Permitido:

```bash
grep -R "external_network_used\|localhost_http_used\|unsafe_broad_search_used\|explicit_paths_only" -n \
  aiw_workspace/agent_loop_regression.py \
  docs/runbooks/AIW_AGENT_LOOP_REGRESSION_SMOKE.md \
  README.md \
  2>/dev/null || true
```

Tambem permitido:

```bash
python3 - <<'PY'
from pathlib import Path
paths = [
    Path("scripts/aiw-agent-loop"),
    Path("scripts/aiw-agent-loop-regression-smoke"),
    Path("aiw_workspace/agent_loop_regression.py"),
    Path("aiw_workspace/agent_iterative_loop.py"),
    Path("aiw_workspace/capability_policy.py"),
    Path("docs/runbooks/AIW_AGENT_LOOP_REGRESSION_SMOKE.md"),
    Path("docs/runbooks/AIW_AGENT_ITERATIVE_LOOP.md"),
    Path("docs/runbooks/AIW_AGENT_CAPABILITY_FOUNDATION.md"),
    Path("docs/runbooks/AIW_CODEACT_SANDBOX.md"),
    Path("README.md"),
]
for path in paths:
    text = path.read_text(encoding="utf-8", errors="replace")
    if "agent-loop-regression" in text:
        print(path)
PY
```

Proibido:

```bash
grep -R "..." -n .
grep -R "." -n .
find . -type f
```

Nao use busca ampla sobre `.` nem leia arquivos sensiveis como `.env`, `config/litellm.yaml` ou `AGENTS.md`. Se uma busca acidental ampla ocorrer, o relatorio deve registrar o desvio, o risco e a correcao adotada.

O regression smoke registra este padrao no artifact:

```text
unsafe_broad_search_used=false
validation_search_scope=explicit_paths_only
```

## Interpretação

`status=passed` significa que o harness validou a regressao offline no estado local atual.

`status=failed` aponta o check especifico em `checks/*.json`. O arquivo `summary.md` oferece leitura curta para revisao humana.
