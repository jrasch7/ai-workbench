TAREFA: AIW LangGraph Phase 4 — criar contrato operacional AGENTS.md

Contexto:
Repo: ~/ai-workbench
Branch esperada: spike/langgraph-engineering-loop
PR draft aberto: https://github.com/jrasch7/ai-workbench/pull/6
O runner scripts/aiw-run-task foi criado e validado com self-test read-only.
O self-test indicou AGENTS=missing.
Paperclip está congelado para engenharia de código.

Objetivo:
Criar um AGENTS.md na raiz do repo com regras operacionais claras para agentes que executam tarefas no AI Workbench.

Escopo obrigatório:
1. Confirmar branch, HEAD e working tree.
2. Criar AGENTS.md na raiz.
3. O AGENTS.md deve documentar:
   - propósito do AI Workbench;
   - regra de usar scripts/aiw-run-task para missões longas;
   - Paperclip congelado para engenharia de código;
   - LangGraph como motor determinístico;
   - Markdown/Git como fonte auditável;
   - obrigação de validar antes de commit;
   - obrigação de não commitar .venv, reports, secrets ou logs;
   - proibição de reescrever .gitignore inteiro;
   - regra de commits pequenos e escopo fechado;
   - quando parar e pedir decisão humana;
   - formato do relatório final;
   - padrão de progress updates curtos.

4. Atualizar docs/runbooks/AIW_RUN_TASK.md se necessário para referenciar AGENTS.md.
5. Não alterar projetos externos.
6. Não usar Paperclip.
7. Não mexer em secrets.

Validações obrigatórias:
- test -f AGENTS.md
- grep -n "Paperclip" AGENTS.md
- grep -n "LangGraph" AGENTS.md
- grep -n "aiw-run-task" AGENTS.md
- git diff --check
- git status --short

Git:
- Commitar somente arquivos desta fase.
- Mensagem de commit:
  docs: add aiw agent operating contract

Push:
- Fazer push para origin/spike/langgraph-engineering-loop.

Entrega final:
Responder com:
- branch
- HEAD inicial/final
- arquivos alterados
- validações executadas
- commit criado
- push realizado
- próximo passo recomendado
