# AIW Tool Registry v1

Este runbook detalha o funcionamento do **Tool Registry v1**, o registro estático e seguro das ferramentas e workflows do AI Workbench.

## O que é o Tool Registry?

O Tool Registry (`aiw_workspace/capability_registry.py`) é uma camada de metadados introspectável que descreve as capacidades disponíveis no AI Workbench. Ele não executa ferramentas por si só; ele as registra, classifica seus riscos e descreve seus schemas de entrada. Isso garante que, no futuro, quando um LLM ou Agent Loop solicitar ferramentas, o AIW as forneça de forma formatada e com os devidos guardrails.

## Diferença entre Capability, Tool e Workflow

- **Capability**: Termo guarda-chuva que inclui qualquer ação, contexto ou ambiente disponível para o agente (tools, workflows, sandboxes, RAG).
- **Tool**: Ferramentas ativas focadas em ações singulares que podem ser chamadas repetidamente (ex: `file_read`, `shell_exec`).
- **Workflow**: Fluxos sistêmicos mais amplos que orquestram várias etapas e geralmente manipulam o ciclo de vida do patch ou workspace (ex: `validation_plan`, `review_gate`, `agent_dispatcher`).

## Como adicionar uma tool nova

1. Abra `aiw_workspace/capability_registry.py`.
2. Adicione a nova definição da ferramenta no array retornado por `_capabilities_db()`.
3. Garanta que o dicionário respeite o schema v1 com todos os campos obrigatórios: `name`, `kind`, `status`, `risk`, `description`, `requires_confirmation`, `allows_external_io`, `writes_files`, `runs_code`, `network_access`, `modifies_git`, `reads_secrets`, `artifacts_path`, `input_schema`, `blocked_by_default`, `allowed_modes`, `source`.

## Como classificar risco

A função `classify_capability_risk(capability)` implementa a política restrita de classificação:

- **High**: Tools que invocam `runs_code`, têm `network_access`, invocam `modifies_git`, permitem `allows_external_io` ou tratam da aplicação/reversão de patches no projeto (`project_patch_apply`, `project_patch_rollback`).
- **Medium**: Tools que têm `writes_files` ou afetam a visualização do projeto (como `project_patch_preview`).
- **Low**: Tools puramente de leitura passiva e controlada, sem escrita ou execução.

*Nota: `reads_secrets` é sempre inválido em qualquer tool.*

## Quais tools estão registradas?

Atualmente, o Registry expõe:
- `file_read` (tool)
- `file_write` (tool)
- `file_patch` (tool)
- `shell_exec` (tool)
- `project_patch_preview` (tool)
- `project_patch_apply` (tool)
- `project_patch_rollback` (tool)
- `validation_plan` (workflow)
- `review_gate` (workflow)
- `evidence_bundle` (workflow)
- `evidence_export` (workflow)
- `integration_outbox` (workflow)
- `worker_loop` (workflow)
- `agent_queue` (workflow)
- `agent_dispatcher` (workflow)

## Quais são passivas e quais exigem confirmação?

As ferramentas passivas (`file_read`, `project_patch_preview`, `review_gate`, `evidence_bundle`, `evidence_export`, `agent_queue`) operam com `requires_confirmation: False`.
As demais ferramentas e workflows ativos (escrita, mutação, execução, integração externa) exigem confirmação explícita no sistema (`requires_confirmation: True`).

## Por que o registry não executa tools ainda?

Neste momento (v1), o objetivo é criar a estrutura de dados (manifests) para que o AI Workbench consiga avaliar e listar o que tem de forma programática. O Tool Runtime (`aiw_runtime.tools`) ainda faz o parse e a execução. A etapa futura será acoplar a execução no registry.

## Como isso será usado no futuro Agent Loop?

Quando implementarmos o Agent Loop interativo, o agente LLM consumirá o `export_capabilities_manifest()` extraindo o `input_schema` e gerando dinamicamente a definição das ferramentas via *Function Calling* da OpenAI / LiteLLM / Ollama. O agente não precisará adivinhar quais ferramentas existem. O Sandbox do CodeAct utilizará essas policies de confirmação para determinar se pode rodar autonomamente (dry_run) ou pausar para permissão do usuário.
