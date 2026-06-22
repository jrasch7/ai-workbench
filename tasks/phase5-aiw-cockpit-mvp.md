TAREFA: AIW Phase 5 — Cockpit MVP funcional estilo Devin

CONTEXTO
Repo: ~/ai-workbench
Branch atual esperada: spike/langgraph-engineering-loop
PR draft existente: https://github.com/jrasch7/ai-workbench/pull/6
O usuário está frustrado porque a bancada ainda não tem interface/chat funcional.
Prioridade absoluta agora: entregar uma UI local funcional, não mais documentação.

OBJETIVO
Criar um Cockpit web local mínimo, utilizável no navegador, parecido com uma primeira fatia do Devin:

- tela com textarea para escrever uma missão;
- botão "Executar missão";
- lista de execuções/runs;
- status da execução: queued/running/succeeded/failed;
- visualização do log gerado;
- integração real com scripts/aiw-run-task;
- comando simples para iniciar o servidor.

ESCOPO OBRIGATÓRIO
1. Confirmar branch, HEAD e working tree.
2. Inspecionar estrutura atual do repo.
3. Criar um módulo local de cockpit. Preferir solução simples e rápida:
   - Python stdlib ou FastAPI se já estiver disponível/for adicionado em requirements separado.
   - HTML/CSS/JS simples, sem React/Vite se isso atrasar.
4. Criar comando:
   scripts/aiw-cockpit

5. O comando deve subir um servidor local em:
   http://127.0.0.1:8765

6. A UI deve ter:
   - título "AI Workbench Cockpit";
   - campo grande de texto para missão;
   - botão "Executar missão";
   - cards/lista de runs;
   - status por run;
   - link/botão para ver log;
   - área de log na própria página;
   - instrução clara de que é MVP local.

7. Backend deve:
   - salvar missões em diretório ignorado pelo Git, por exemplo reports/aiw-cockpit/tasks/;
   - salvar logs em reports/aiw-cockpit/runs/;
   - iniciar scripts/aiw-run-task em subprocess;
   - manter metadados simples de run em JSON;
   - não bloquear a UI enquanto a missão roda;
   - permitir consultar status e log por HTTP.

8. Segurança:
   - servidor bind somente em 127.0.0.1;
   - não aceitar caminho arbitrário vindo do usuário para execução;
   - criar arquivos temporários controlados pelo próprio app;
   - não expor secrets;
   - não usar shell=True quando não for necessário.

9. Atualizar .gitignore para ignorar:
   reports/aiw-cockpit/

10. Criar runbook:
   docs/runbooks/AIW_COCKPIT.md

   Deve conter:
   - como iniciar;
   - URL local;
   - como executar missão;
   - onde ficam logs;
   - limitações do MVP;
   - próximos passos para virar "Devin-like".

11. Não mexer em Paperclip.
12. Não mexer em Obsidian.
13. Não mexer em produtos Nivela.
14. Não fazer merge.
15. Não apagar trabalho anterior.

VALIDAÇÕES OBRIGATÓRIAS
- bash -n scripts/aiw-cockpit
- python -m compileall aiw_langgraph
- python -m compileall aiw_cockpit
- iniciar servidor em background
- testar GET / com curl ou python urllib
- testar endpoint de criação de run com uma missão read-only pequena
- testar endpoint de status/log
- parar servidor background
- git diff --check
- git status --short

GIT
- Commitar somente arquivos desta fase.
- Mensagem:
  feat: add aiw cockpit mvp
- Push para origin/spike/langgraph-engineering-loop.

ENTREGA FINAL
Responder com:
- STATUS: DONE ou BLOCKED
- URL local
- comando para iniciar
- arquivos alterados
- validações executadas
- commit criado
- push realizado
- como testar manualmente no navegador
- próximos passos para transformar em Devin-like
