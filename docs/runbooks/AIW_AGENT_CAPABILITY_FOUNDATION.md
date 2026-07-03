# AIW Agent Capability Foundation Runbook

Este runbook documenta os procedimentos operacionais para auditoria, adição e governança das capacidades ("capabilities") dentro da arquitetura do AI Workbench.

## Como auditar capacidades atuais

Para verificar as ferramentas, hooks e contextos injetáveis no ambiente atual, utilize a combinação padrão de busca pela raiz do repositório:

```bash
find . -maxdepth 3 -type f \
  \( -path './aiw_runtime/*' -o -path './aiw_context/*' -o -path './aiw_workspace/*' -o -path './scripts/*' -o -path './docs/*' \) \
  | sort

grep -R "class .*Tool\|def .*tool" aiw_runtime aiw_context aiw_workspace
```

A busca retornará as definições exatas. Se a ferramenta não aparecer no código final injetável para o runtime (`aiw_runtime`), considere-a como não existente.

## Como adicionar uma capability nova

1. Defina a interface em `aiw_workspace/capability_registry.py` provendo o nome, `kind` (context, tool, sandbox) e dependências.
2. Codifique o comportamento em uma estrutura Python pura, preferencialmente dentro de `aiw_runtime/tools.py` caso seja utilitária, ou `aiw_context` caso seja informativa.
3. Configure as policy flags obrigatórias:
    * `requires_confirmation: bool`
    * `writes_files: bool`
    * `runs_code: bool`
    * `network_access: bool`

## Como classificar risco

* **Low (Baixo):** Ferramentas read-only puras e locais sem consumo grande de processamento (ex: `file_read`, `directory_list`).
* **Medium (Médio):** Ferramentas mutáveis controladas e reversíveis, restritas ao repositório local (ex: `file_write` no `.aiw/`, operações de commit não enviadas ao remoto).
* **High (Alto):** Ferramentas que invocam processos destrutivos, execuções de shell sem filtro nativo (`shell_exec`), comunicação de rede, e modificações fora da pasta `.aiw/` restrita ou alterações sem versionamento prévio.

## Como impedir execução perigosa

* Utilize a camada `ExternalWorkerPolicy` / `ToolPolicy` para barrar a injeção em instâncias de Agent Loop baseados em risco.
* Evite conceder privilégios irrestritos ou permitir path traversal (bloquear `../` nativamente).
* Exija a flag `--confirm` ou dependa do Cockpit / Inbox UI para dar sinal verde para capacidades mutáveis (*requires_confirmation = true*).
* A execução perigosa não deve virar execução externa sem aprovação de uma policy.
* Actions como `codeact_sandbox` devem declarar `artifacts_path` e `input_schema`, exigir confirmação, bloquear IO externo por padrão e documentar que o host-sandbox é best-effort, não isolamento forte.

## Capability Policy v1

O Agent Iterative Loop usa `aiw_workspace/capability_policy.py` como primeira camada local de decisão antes de acionar uma capability. A policy v1 é pequena, hardcoded, usa `policy_profile=local_offline_v1` e não depende de configuração sensível.

A avaliação sempre consulta `capability_registry.py` e registra no artifact:

```text
workspace_id
capability
mode
operation
policy_profile
risk
requires_confirmation
confirmed
runs_code
writes_files
external_io
blocked_by_default
simulation_only
capability_not_executed
allowed
reason
```

Regras atuais:

* `dry-run` é permitido como simulação, registra `simulation_only=true` e não executa capability real.
* Capability ausente ou inválida bloqueia a run.
* Operation desconhecida bloqueia a run.
* Modo `llm` bloqueia a run.
* IO externo bloqueia execução offline.
* Capability que exige confirmação bloqueia quando `confirmed=false`.
* `codeact_sandbox` é `high-risk`, `runs_code=true`, `writes_files=true` e `blocked_by_default=true`; no Agent Iterative Loop ele só passa em `offline` com confirmação explícita, `operation=python_eval_fixed`, código fixo, execução local e artifacts rastreáveis.

As decisões aparecem em `run.json` como `capability_decisions` e no `summary.md`. Em caso de bloqueio, `status=blocked` e `blocked_reason` recebe o motivo da policy, por exemplo `confirmation_required` ou `capability_missing`.

Paths expostos em UI/API devem usar forma relativa ao repo, como `.aiw/workspaces/<id>/...`, para reduzir vazamento de paths absolutos locais. Artifacts antigos continuam legíveis e devem ser higienizados na apresentação.

## Como uma capability gera artifacts

As ferramentas não enviam resultados para fora do workspace local sem intervenção do Worker Loop. Os resultados, prints e status de execução devem ser salvos nas estruturas delimitadas de artifact:
```
.aiw/workspaces/<id>/runs/<run_id>/
```
Cada tool invocation loga os parâmetros e payloads nesses arquivos `json` para garantir o "Evidence / Audit".

## Como ela entra no Cockpit futuramente

O Cockpit usará o `capability_registry.py` para listar as ferramentas dinamicamente. Elas serão expostas na interface operacional com badges informando seu nível de risco. Para acioná-las na UI, os modelos consumirão o schema de interface publicado e interagirão ativamente.

## Como validar sem modelo real

* Utilize mocks que injetam JSONs estáticos (`item.json`, `patch-intent.json`) previstos no RAG ou Inbox, injetando comportamentos forjados na fila.
* Rode `agent_dispatcher` em `--dry-run` para validar a orquestração e uso aparente do sandbox e registry pela pipeline, atestando estabilidade arquitetural sem faturar chamadas caras de LLM.
* Rode `scripts/aiw-agent-loop` em `--dry-run` e `--execute --confirm-agent-loop` para validar a Capability Policy v1 sem modelo real, sem GitHub/Jira e sem background.
