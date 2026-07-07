# AIW Project Write Mode Phase 3D.2

## Resultado

Implementação do Write Mode Avançado para código-fonte, também conhecido como **Project Write Mode**, concluída com êxito. Três novas ferramentas orientadas à UI de Cockpit foram adicionadas para permitir aprovação de diffs técnicos reais gerados via runtime.

## Funcionalidades adicionadas

- `project_patch_preview`: Cria o proposal local de alteração extraindo o arquivo base, validadando a string substituída (exata) e exportando pro UI com status *preview* (não destrutivo).
- `project_patch_apply`: O trigger real. Aplica na árvore de desenvolvimento usando o patch_id restrito gerado pelo *preview*. Gera um backup do timestamp antes de concretizar o file system write.
- `project_patch_rollback`: Retorna o file para a cópia do backup indexado no *apply*.

## Modelo de segurança

- As tools project-level compartilham das mesmas defesas do File OS padrão, com um endurecimento: **somente `aiw_runtime`, `scripts`, `tests` e `docs` podem receber comandos deste escopo.**
- `patch_id` é o único portador da mutabilidade. Se a UI ou o Runner não gerarem o patch_id primeiro pelo *preview*, não há escrita.
- Path escapes (`..`, `/`), ou edições indiretas (secrets, env, .venv, git) são rigorosamente bloqueadas ainda no preview. 

## Fluxo de preview/apply/rollback

1. A tool `project_patch_preview` escreve um JSON local dentro do cache de patches do AIW (`.aiw/patches/<patch_id>.json`).
2. O Cockpit lê os patches deste run (mapeados nos traces de logs) e renderiza na interface em linguagem de produto.
3. O trigger envia POSTs `/runner/patch/apply` e `/runner/patch/rollback`. O cockpit chama localmente o module tool.

## Cockpit UX

Uma subseção no detalhe do Run nomeada `Alterações propostas` exibe:
- Arquivo atingido
- Motivo relatado do patch
- Status: preview, applied, ou rolled_back.
- Botão condicional de Apply ou Rollback baseado no lifecycle.
- O unified diff exposto via block dropdown interativo (*Ver diff técnico*).

## Validações executadas

- Comandos básicos de parsing nas heredocs `python3 -m py_compile`.
- Embedded Cockpit Python validation (extraindo Python body isolado).
- Execução isolada das novas tools bypassando LiteLLM por `aiw-tool-smoke`.
- Path policies. Testes deliberados provam falhas corretas no `.env` e em pastas fora da source whitelist, tal como a raiz `.`.
- Replacement lock. Se houver variação no número de aparições ou o state changer durante o Preview e o Apply, a transação morre via Exception tratada (`ok: False`).

## Limitações

- Sem patch difuso. (Segurança máxima obriga match literal).
- Sem regex patch.
- Sem escrita livre. (Precisa especificar a substituição ou usar o legacy system file writer na whitelist estática).
- apply somente por patch_id; não acata path dinâmico.
- rollback depende de backup perfeitamente gravado no step *apply*.
- código-fonte permitido apenas em roots explícitos.

## Próximo passo recomendado

Revisão visual e QA real na GUI do Cockpit para atestar a fluidez da esteira *Agent -> Proposal -> User Applies*. A base operacional do file system para a ferramenta AI Workbench agora é completa para produção iterativa!
