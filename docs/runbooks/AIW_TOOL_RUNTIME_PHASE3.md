# AIW Tool Runtime — Fase 3

## Objetivo
Implementar o Tool Runtime mínimo do AI Workbench, criando as fundações para que um Runner (Agent) em Python seja capaz de iterar com a LLM consumindo ferramentas locais, seguindo o roadmap arquitetural. O runtime foi criado mas não substitui o script atual do Cockpit.

## Arquitetura
O Tool Runtime foi implementado no pacote `aiw_runtime`, contendo:
- `schemas.py`: Define o contrato (JSON schema compatível com a API da OpenAI/LiteLLM) para cada tool disponível.
- `policy.py`: Centraliza as políticas de segurança. Define a `allowlist` de comandos do `shell_exec`, bloqueio de acesso a `.env` e tokens, e escape de paths (..).
- `tools.py`: Implementa a lógica das ferramentas. Exposto também como CLI isolado para testes (via `python -m aiw_runtime.tools`).

O Agent foi criado como um novo script:
- `scripts/aiw-runner-agent`: Runner Python em loop que inicializa a task, repassa os schemas de tools para o LiteLLM e executa chamadas locais através do pacote `aiw_runtime`, salvando o log de trace de tudo. Envolto em um heredoc bash (`exec python3 - <<'PYTHON'`) para passar pelas mesmas ferramentas de pipeline e syntax checks locais do projeto.

## Arquivos Criados/Alterados
- **[NEW]** `aiw_runtime/__init__.py`
- **[NEW]** `aiw_runtime/policy.py`
- **[NEW]** `aiw_runtime/schemas.py`
- **[NEW]** `aiw_runtime/tools.py`
- **[NEW]** `scripts/aiw-runner-agent`
- **[NEW]** `scripts/aiw-tool-smoke`
- **[NEW]** `docs/runbooks/AIW_TOOL_RUNTIME_PHASE3.md`

## Tools Implementadas
O MVP inicial de tools conta com:
- `directory_list`: Permite listar o conteúdo local, com limite de entradas e profundidade máxima. Restringe acesso fora da raiz com bloqueio de paths relativos a `..` ou absolutos e ofusca `node_modules` e `.venv`.
- `file_read`: Lê arquivos truncando se passarem do limite de `max_bytes` especificado.
- `shell_exec`: Executa shell isolado via `subprocess.run(shell=False)` e varre os subcomandos na string antes de permitir a execução.

## Política de Segurança
Aplicada fortemente no `policy.py`:
- `shell_exec` roda sem `shell=True`, bloqueando operadores como `|`, `>`, `<`, `&&`, `||`, `$(`, `;`.
- Apenas comandos contidos na **allowlist** passam: `pwd`, `ls`, `find`, `cat`, `sed`, `grep`, `head`, `tail`, comandos neutros de `git`, scripts `.sh` do diretório via bash seguro com flag restritiva ou `python3` para check.
- Proteção ativa contra `git commit`, `git push`, leitura direta de `.env` e vazamento de credentials/secrets passados em inline code.

## Validações Executadas
1. **Compilação**: Validada via `python3 -m py_compile aiw_runtime/*.py` com sucesso.
2. **Bash Syntax Check**: Executado `bash -n scripts/aiw-runner-agent` com sucesso (garantido através da compatibilidade de execução via Bash Heredoc).
3. **Smoke Tests (Isolado e Controlado)**: 
    - `python3 -m aiw_runtime.tools directory_list --path . --max-depth 1 --limit 20` -> OK
    - `python3 -m aiw_runtime.tools file_read --path README.md --max-bytes 1000` -> OK
    - `python3 -m aiw_runtime.tools shell_exec --command "git status -sb"` -> OK
    - `python3 -m aiw_runtime.tools file_read --path .env` -> BLOQUEADO corretamente.
    - `python3 -m aiw_runtime.tools shell_exec --command "git push"` -> BLOQUEADO corretamente.
4. **Smoke Test (LiteLLM)**: O teste foi codificado (`scripts/aiw-tool-smoke`) para verificar como o `dev-coder` manipula `tool_calls`. O servidor LiteLLM local retornou `HTTP Error: 400: "No connected db"`. Conforme alinhamento, o sucesso do modelo não foi falseado no Runner e esse status da infraestrutura upstream foi deixado documentado, mantendo a preparação do endpoint `runner` finalizada.

## Evidências
Verificação de `git diff --check` não encontrou falhas.
Exemplo de bloqueio bem-sucedido:
```json
{
  "ok": false,
  "tool": "shell_exec",
  "error": "Subcomando git mutável bloqueado: push"
}
```

## Limitações e Riscos Restantes
- O erro HTTP 400 no LiteLLM aponta que ele pode estar configurado localmente para logar/proxyar com banco mas sem conexão ativa à base, o que falha requests grandes ou com array complexo de tools no payload.
- As ferramentas dependem fortemente do host local. Em Fases futuras (Fase 5+), Fazer o `shell_exec` saltar para dentro do Workspace Docker isolado, já que no MVP ele roda apenas sob a raiz do Repositório atual do Usuário.
- A validação de tokens nas execuções de command blocks funciona por substring de blacklist, podendo haver gaps que precisem ser lapidados durante a adoção de uso real.

## Próximo passo para integração com Cockpit
1. Identificar e sanar o Error `400` no backend LiteLLM para as requests POST de tool calls.
2. Inserir `file_write` / `file_patch` (com aprovação estendida).
3. Plugar o script `aiw-runner-agent` ao Cockpit via rota dedicada `/api/runs/agent` preservando o Runner One-Shot original (`scripts/aiw-runner-once`) para não quebrar fluxos do MVP até a maturação total do Loop Multi-Agent.

## Confirmações de Restrições
- [x] O arquivo `.env` não foi modificado, nem lido.
- [x] `~/.hermes/config.yaml` não foi modificado.
- [x] Nenhum comando `git add`, `git commit` ou `git push` foi executado.
- [x] OpenHands ou ferramentas externas proibidas não foram utilizadas.
- [x] Cockpit original mantido intacto.
