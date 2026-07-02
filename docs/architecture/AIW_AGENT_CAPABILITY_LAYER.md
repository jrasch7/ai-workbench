# AIW Agent Capability Layer

## 1. Objetivo da camada de capacidades

A camada de capacidades (Capability Layer) tem como objetivo abstrair, isolar e controlar o acesso do modelo de linguagem (LLM) ao ambiente local, repositório e infraestrutura. Ela atua como um barramento unificado de execução e segurança, garantindo que o agente possua as ferramentas corretas para operar de forma autônoma sem violar regras de segurança.

## 2. O que já existe no AIW (Verificado no Código)

* **Filesystem Tools:** `file_read`, `file_write`, `file_patch`.
* **Shell Tools:** `shell_exec`.
* **Repo/Git Tools:** Integração mínima via comandos shell orquestrados no pipeline e extração de diffs via `patch_gate` e `changed_lines_coverage`.
* **Test Tools:** Adaptações para testes unitários e extração de logs/resultados (`test_runner`, `coverage_report`).
* **Context Engine:** Empacotador de contexto primitivo via `indexer.py` (`get_context_pack`, `_build_search_index`).
* **Agent Dispatcher / Queue:** Controle de filas de dispatching e roteamento, permitindo que a execução opere em modo offline sem consumo acidental de recursos e rede (`agent_dispatcher.py`, `agent_queue.py`).

## 3. O que ainda falta (Não encontrado no Código)

* **Context / RAG Local:** (Implementado na v1 via `indexer.py` e `search.py`) Motor de indexação, chunking e busca léxica local. Consulte o [Runbook Context RAG Local](../runbooks/AIW_CONTEXT_RAG_LOCAL_INDEX.md).
* **Context Pack Builder:** (Implementado na v1 via `context_pack.py`) Geração dinâmica de contexto baseada no RAG, empacotando o problema ativamente dentro de orçamentos de chunks/caracteres. Consulte o [Runbook Context Pack Builder](../runbooks/AIW_CONTEXT_PACK_BUILDER.md).
* **Tool Registry:** (Implementado na v1 via `capability_registry.py`) Gerenciador formal de ferramentas plugáveis que registra dinamicamente capacidades do LLM, agora com schemas estáticos e políticas de risco estabelecidas. Consulte o [Runbook Tool Registry](../runbooks/AIW_TOOL_REGISTRY.md).
* **CodeAct:** (Implementado na v1 via `codeact_sandbox.py`) Executor controlado de ações Python com timeout, bloqueios e confirmação obrigatória. Consulte o [Runbook CodeAct Sandbox](../runbooks/AIW_CODEACT_SANDBOX.md).
* **Sandbox:** Containerização (ex. devcontainers) para garantir que ferramentas operem em ambiente efêmero seguro, protegendo a máquina host.
* **Browser/Web Tools:** Integração de ferramentas web para consulta externa (ex: documentação, issues).
* **MCP / Tools Futuros:** Suporte aos protocolos abertos de integração do mercado.
* **Agent Loop:** Ciclo iterativo real (ReAct ou similar) onde o agente decide as ferramentas a utilizar, interpreta os resultados e ajusta o plano iterativamente.
* **Memory / Replay:** Memória de longo prazo ou replay de execuções para aprendizado contínuo.

## 4. Mapa de capacidades

* Context / RAG
* Context Pack Builder
* Tool Registry
* Tool Policy
* CodeAct
* Sandbox
* Filesystem tools
* Shell tools
* Repo/Git tools
* Test tools
* Browser/Web tools
* MCP/tools futuros
* Agent Loop
* Memory / Replay
* Evidence / Audit

## 5. Contrato mínimo de uma capability

```json
{
  "name": "string",
  "kind": "context|tool|action|sandbox|memory|validation",
  "status": "planned|experimental|available|blocked",
  "risk": "low|medium|high",
  "requires_confirmation": true,
  "allows_external_io": false,
  "writes_files": false,
  "runs_code": false,
  "network_access": false,
  "artifacts_path": ".aiw/..."
}
```

## 6. Como essa camada se conecta ao fluxo existente

Patch Intent
→ Agent Queue
→ Agent Dispatcher
→ **Capability Layer**
→ Patch Preview
→ Validation Plan
→ Review Gate
→ Evidence Bundle

## 7. Regras de segurança

* Todas as capacidades de alteração de estado (state-mutating) devem ser rastreadas e audíveis via artefatos gravados no diretório `.aiw/`.
* Ferramentas não devem acessar arquivos fora da restrição do diretório configurado, protegendo `.env`, segredos ou escopos externos.
* A camada atuará como gatekeeper entre o modelo (LLM) e a ação final invocada no sandbox ou máquina host.

## 8. O que fica proibido por padrão

* Escritas fora do escopo do repositório clonado da workspace.
* Alteração de chaves criptográficas locais (`.env`, config files de sistema).
* Execução de downloads diretos de bibliotecas arbitrárias sem passar pelo Tool Policy configurado e proxy seguro (se aplicável).
* Envio de Pushs para repositório sem aprovação explícita no loop de Integração (`integration_outbox`).

## 9. Como modelos entram depois

* Quando a Capability Layer, Tool Registry e Agent Loop (Sandbox) estiverem amadurecidos, o Cockpit ou Runner orquestrará a entrada do *Model Provider Lab*.
* A entrada dos modelos injetará LLMs conectados via Ollama ou provedores API que interagirão com este conjunto de ferramentas via JSON-schema padronizado.

## 10. Limites da v1

* Operações simuladas.
* Registry manual gerenciado localmente na workspace.
* Sem integrações avançadas de RAG / Embeddings, adotando fallback linear (`grep`, indexação estática) primeiro.
