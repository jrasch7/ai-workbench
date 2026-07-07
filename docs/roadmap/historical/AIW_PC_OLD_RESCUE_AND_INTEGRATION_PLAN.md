# PRD: PC Old Rescue and Integration Plan

**Objetivo**

Preservar e integrar com segurança as alterações locais não commitadas que ainda residem no PC antigo (relacionadas ao Cockpit Phase 6.5/7) antes de trazê‑las para o repositório compartilhado.

**Contexto dos dois PCs**

- **PC novo**: branch `docs/aiw-agent-stack-and-roadmap` contendo apenas documentação.
- **PC antigo**: contém trabalho de código em andamento na branch `spike/langgraph-engineering-loop` com alterações locais não versionadas.

**Regra principal**

> **Preservar** todo trabalho local antes de qualquer outra ação. Nenhuma modificação deve ser feita nos arquivos existentes até que o estado atual seja capturado.

**Sequência de Resgate**

1. **Diagnosticar branch**
   - `git rev-parse --abbrev-ref HEAD` → confirmar que está em `spike/langgraph-engineering-loop`.
   - `git status --short` → listar arquivos modificados/untracked.
2. **Salvar patch**
   - Criar diretório temporário: `mkdir -p /tmp/aiw-rescue`
   - `git diff > /tmp/aiw-rescue/changes.patch`
   - `git diff --stat > /tmp/aiw-rescue/changes.stat`
   - `git diff --name-only > /tmp/aiw-rescue/changed_files.txt`
3. **Registrar estado completo**
   - `git log -n 10 > /tmp/aiw-rescue/log.txt`
   - `git status > /tmp/aiw-rescue/status.txt`
4. **Auditar arquivos alterados**
   - Classificar cada caminho listado em `changed_files.txt` nas categorias:
     - *Phase 6.5* (hardening, métricas)
     - *Phase 7* (analysis, handoff, validator)
     - *Docs* (README, ADRs, PRDs)
     - *Bug* (correções menores)
     - *Fora de escopo* (qualquer coisa que não se enquadre nas fases acima)
   - Usar um editor de texto (ex.: `vim`) ou `sed` para anotar a classificação no arquivo `/tmp/aiw-rescue/audit.md`.
5. **Validar sintaxe**
   - Para arquivos Python/JSON/YAML: `python -m py_compile <file>` ou `yq eval . <file>`.
   - Para arquivos Markdown: garantir que não há blocos de código incompletos que causem parsing de ferramenta.
6. **Comitar se estiver seguro**
   - **Atenção**: só proceder se a auditoria confirmar que todas as alterações são desejadas e não violam as regras de segurança (sem secrets).
   - `git add <list-of-files>` (usar a lista auditada).
   - `git commit -m "feat: rescue local work from old PC – phase 6.5/7"`
7. **Push para branch de código**
   - `git push -u origin spike/langgraph-engineering-loop`
   - Caso o push seja rejeitado por divergência, **não** usar `--force`; comunicar ao time.

**Comandos Permitidos** (executados no PC antigo)

- `git status`, `git diff`, `git log`, `git add`, `git commit`, `git push`
- `mkdir`, `cp`, `mv`, `cat`, `sed`, `awk` (para manipular arquivos de auditoria)
- Ferramentas de validação de sintaxe (ex.: `python -m py_compile`, `yq`, `jsonlint`).

**Comandos Proibidos**

- `git reset` (qualquer forma)
- `git restore`
- `git checkout .`
- `git clean`
- `git stash`
- Qualquer operação que descarte alterações locais sem backup.

**Plano de Rollback Seguro**

- Se o commit de resgate já foi criado, usar `git revert <commit_sha>` para criar um commit reverso rastreável.
- Se ainda não houve commit, preservar patch, status, diff e auditoria em `/tmp/aiw-rescue` e parar para decisão humana.
- Se o push for rejeitado ou houver divergência, não usar `--force`; relatar o bloqueio.
- Não usar `git reset`, `git restore`, `git checkout .`, `git clean` ou `git stash` durante o resgate.

**Critérios de DONE / BLOCKED**

- **DONE**: Todas as alterações locais foram auditadas, validadas e commitadas; patch foi pushado com sucesso; arquivos de auditoria armazenados em `/tmp/aiw-rescue` para referência futura.
- **BLOCKED**: Encontrados secrets, falhas de sintaxe críticas, ou impossibilidade de push (por exemplo, falta de permissão). O processo deve parar, relatar o bloqueio e aguardar instruções.

**Relatório Final Esperado**

- `git status --short` limpo.
- `git log -n 3` mostra o novo commit de resgate.
- Arquivo `audit.md` incluído no commit ou mantido localmente como evidência.
- Mensagem de sucesso ou descrição do bloqueio.
