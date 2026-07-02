# AIW CodeAct Sandbox Executor v1

## O que é CodeAct no AIW

CodeAct é a camada de execução controlada de código Python dentro do AI Workbench. Ela permite que ações estruturadas sejam executadas em um processo isolado, com timeout, captura de saída, bloqueio de padrões perigosos e registro completo de evidências.

Na v1, CodeAct **não** executa código vindo de LLM. Ele cria a infraestrutura segura para que, no futuro, o Agent Loop possa consumir ações CodeAct de forma controlada.

## O que o v1 permite

- Execução de snippets Python puros (`kind: python_eval`).
- Timeout configurável por ação.
- Captura e truncamento de stdout/stderr.
- Registro de artifacts por run (action.json, run.json, stdout.txt, stderr.txt, summary.md).
- Bloqueio de padrões perigosos antes da execução.
- Confirmação obrigatória (`confirm=True`).
- Listagem e leitura de runs anteriores.

## O que o v1 bloqueia

Padrões perigosos detectados estaticamente no código antes da execução:

```text
import socket, import requests, urllib, http.client,
subprocess, os.system, popen, pty, shutil.rmtree,
Path.home, expanduser, open(".env"), open('.env'),
litellm.yaml, AGENTS.md, git push, git clone, gh pr,
curl, wget, nc, ncat, ssh, scp
```

Modos bloqueados:

```text
shell, bash, powershell, node, python_script_path externo,
browser, network, git
```

Qualquer `kind` diferente de `python_eval` é rejeitado.

## Por que isso ainda não é sandbox forte

O executor v1 roda no host local, sem devcontainer, chroot ou VM. O isolamento é feito por:

- Processo separado (`subprocess.run` com `shell=False`).
- Flag `-I` do Python (ignora variáveis de ambiente e site-packages do usuário).
- Ambiente mínimo (apenas `PATH` e `PYTHONPATH`).
- `cwd` apontando para o diretório do run dentro de `.aiw/`.

**Isso NÃO é fronteira de segurança final.** É um host-sandbox best-effort. Devcontainer/chroot ficam para sprint futura.

## Onde ficam artifacts

```text
.aiw/workspaces/<workspace_id>/codeact/runs/<run_id>/
```

Arquivos gerados por run:

| Arquivo | Descrição |
|---------|-----------|
| `action.json` | A ação original submetida |
| `run.json` | Metadados da execução (status, timestamps, returncode) |
| `script.py` | O código efetivamente executado |
| `stdout.txt` | Saída padrão capturada (truncada) |
| `stderr.txt` | Saída de erro capturada (truncada) |
| `summary.md` | Resumo human-readable da execução |

## Como executar smoke seguro

```bash
cd /home/joao/ai-workbench
PYTHONPATH=. python3 -c "
from aiw_workspace.codeact_sandbox import run_codeact_action
result = run_codeact_action('aiw', {
    'kind': 'python_eval',
    'title': 'hello',
    'code': \"print('CODEACT_HELLO')\",
    'timeout_seconds': 5,
}, confirm=True)
print(result['status'], result.get('stdout', '').strip())
"
```

## Como inspecionar uma run

```bash
PYTHONPATH=. python3 -c "
from aiw_workspace.codeact_sandbox import list_codeact_runs
runs = list_codeact_runs('aiw')
for r in runs['runs']:
    print(r['run_id'], r['status'])
"
```

## Como isso se conecta ao Tool Registry

O CodeAct Sandbox está registrado no Capability Registry como:

```json
{
  "name": "codeact_sandbox",
  "kind": "action",
  "status": "experimental",
  "risk": "high",
  "requires_confirmation": true,
  "runs_code": true,
  "blocked_by_default": true,
  "allowed_modes": ["manual"]
}
```

Ele aparece no manifest exportado e pode ser consultado via `get_capability("codeact_sandbox")`.

## Como será usado pelo futuro Agent Loop

Quando o Agent Loop (AIW-CAP-06) for implementado, ele poderá:

1. Receber uma ação estruturada do LLM.
2. Validar a ação contra a política do CodeAct.
3. Executar com `confirm=True` (após aprovação humana ou policy gate).
4. Capturar o resultado e alimentar o próximo turno do loop.

## Por que ainda não usa LLM/Ollama

O objetivo desta sprint é provar que a infraestrutura de execução controlada funciona de ponta a ponta sem depender de modelo. Quando o LLM for conectado, ele gerará ações que passarão por esta mesma pipeline de validação e execução.

## Por que devcontainer/chroot ficam para sprint futura

A prioridade é ter o fluxo funcional primeiro. Containerização adiciona complexidade operacional (Docker, volumes, networking) que será tratada quando a base estiver madura.
