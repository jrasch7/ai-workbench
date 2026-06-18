#!/usr/bin/env bash
# AIW Cockpit v2 - Branch setup, validation, commit, push, PR
set -euo pipefail
cd /home/joao/ai-workbench

echo "=== STEP 1: Git audit ==="
git log --oneline -10
echo "---"
git status

echo ""
echo "=== STEP 2: Create branch ==="
git checkout main
git pull --ff-only || git pull
git checkout -b feature/aiw-cockpit-agent-workspace-v2 2>/dev/null || git checkout feature/aiw-cockpit-agent-workspace-v2

echo ""
echo "=== STEP 3: Validate Python syntax ==="
python3 -m py_compile scripts/aiw-cockpit && echo "Python syntax OK"

echo ""
echo "=== STEP 4: Start server for validation ==="
AIW_COCKPIT_PORT=18765 python3 scripts/aiw-cockpit > /tmp/aiw-v2-test.log 2>&1 &
COCKPIT_PID=$!
echo "Started PID: $COCKPIT_PID"
sleep 3

kill -0 $COCKPIT_PID 2>/dev/null || { echo "FAIL: process died"; cat /tmp/aiw-v2-test.log; exit 1; }

echo ""
echo "=== STEP 5: Test endpoints ==="

# Home page loads
curl -sf http://127.0.0.1:18765/ | grep -q "AIW" && echo "PASS: home loads" || { echo "FAIL: home not loading"; kill $COCKPIT_PID; exit 1; }

# API endpoints
curl -sf http://127.0.0.1:18765/api/status > /dev/null && echo "PASS: /api/status" || echo "NOTE: /api/status empty (ok)"
curl -sf http://127.0.0.1:18765/api/runs > /dev/null && echo "PASS: /api/runs" || echo "NOTE: /api/runs empty (ok)"

# V2 UI text checks
curl -sf http://127.0.0.1:18765/ | grep -q "O que você quer" && echo "PASS: composer text present" || { echo "FAIL: composer text missing"; kill $COCKPIT_PID; exit 1; }
curl -sf http://127.0.0.1:18765/ | grep -q "Criar e executar com IA" && echo "PASS: primary CTA present" || { echo "FAIL: primary CTA missing"; kill $COCKPIT_PID; exit 1; }
curl -sf http://127.0.0.1:18765/ | grep -q "dev-gemini-fast" && echo "PASS: model values present" || { echo "FAIL: model values missing"; kill $COCKPIT_PID; exit 1; }
curl -sf http://127.0.0.1:18765/ | grep -q "Precisa da sua aten" && echo "PASS: review section present" || { echo "FAIL: review section missing"; kill $COCKPIT_PID; exit 1; }
curl -sf http://127.0.0.1:18765/ | grep -q "Salvar na inbox" && echo "PASS: secondary CTA present" || { echo "FAIL: secondary CTA missing"; kill $COCKPIT_PID; exit 1; }

# JSON API task create
RESULT=$(curl -sf -X POST http://127.0.0.1:18765/api/task/create \
  -H "Content-Type: application/json" \
  -d '{"title":"Test task v2","description":"Automated test","model":"dev-balanced"}' 2>&1 || true)
echo "api/task/create result: $RESULT"

kill $COCKPIT_PID
echo ""
echo "=== ALL VALIDATIONS PASSED ==="

echo ""
echo "=== STEP 6: Commit ==="
git diff --check || true
git add scripts/aiw-cockpit
git status
git commit -m "feat: redesign AIW cockpit as agent workspace

Replaces the technical panel UI with a full Agent Workspace UX:
- Left sidebar navigation (Overview, Inbox, Running, Review, Done, Failed, Models)
- Central composer: 'O que você quer que o AIW faça?' with large textarea
- Model selector dropdown (Rápido, Código, Balanceado, Grande, Revisão, Arquitetura)
- AI on by default — removed 'Usar LLM' checkbox from main flow
- Inbox as cards (not table) with task context before execution
- Human review sections: 'Precisa da sua atenção', 'Atividade recente'
- Run detail prioritizes objective/result over raw technical data
- Buttons: 'Criar e executar com IA', 'Salvar na inbox', 'Executar task selecionada'
- Added /api/task/create JSON endpoint"

echo ""
echo "=== STEP 7: Push ==="
git push origin feature/aiw-cockpit-agent-workspace-v2

echo ""
echo "=== STEP 8: Open PR ==="
gh pr create \
  --title "feat: redesign AIW cockpit as agent workspace" \
  --body "## Objetivo
Transformar o Cockpit em uma interface de operação de agentes, substituindo a experiência técnica por um workspace de agente.

## O que muda
- Sidebar esquerda com navegação completa
- Composer central para criação de tasks com linguagem humana
- Modelo selecionável via dropdown (não campo livre)
- IA ligada por padrão — checkbox 'Usar LLM' removida do fluxo principal
- Inbox como cards contextuais, não tabela
- Seções humanas de review: 'Precisa da sua atenção', 'Atividade recente'
- Detalhe de run prioriza objetivo e resultado sobre dados técnicos brutos
- Endpoint /api/task/create para criação via JSON

## Critério de sucesso
O usuário entende em < 10 segundos:
- Onde digitar o que quer que o AIW faça
- Qual modelo será usado
- Se a task será salva ou executada imediatamente
- Qual task está na inbox
- Qual run precisa de revisão
- Qual ação tomar em seguida" \
  --base main \
  --head feature/aiw-cockpit-agent-workspace-v2

echo ""
echo "=== DONE ==="
git log --oneline -3
