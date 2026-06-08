# Hermes Operational Reliability Protocol

## 1. Purpose
O Hermes deve operar como agente de engenharia confiável, não chatbot. Em tarefas longas, precisa reportar progresso, executar ações verificáveis e terminar com estado claro.

## 2. Mandatory progress updates
Para tarefas via Telegram ou tarefas maiores que 60 segundos:
- PROGRESS 1/N — Iniciando tarefa e confirmando escopo.
- PROGRESS 2/N — Diretório e Git verificados.
- PROGRESS 3/N — Arquivos inspecionados.
- PROGRESS 4/N — Alterações aplicadas.
- PROGRESS 5/N — Revisando diff/status.
- PROGRESS 6/N — Rodando validações.
- PROGRESS 7/N — Preparando handoff final.
Typing não conta como progress update.

## 3. Evidence rule
Sem evidência, não aconteceu. O agente não pode dizer que executou, validou ou concluiu sem saída real, status real ou evidência objetiva.

## 4. Command execution rule
Não imprimir comandos em bloco markdown fingindo execução. Quando executar comando, reportar comando, saída relevante, erro relevante e conclusão.

## 5. Path rules
Terminal deve usar `cd /home/joao/ai-workbench` antes de comandos do repo.
File tools devem usar caminhos relativos ao repo.

## 6. Tool failure rule
Se `read_file`, `write_file` ou qualquer tool falhar:
- não repetir a mesma chamada em loop;
- não ignorar erro;
- enviar `BLOCKED`;
- reportar o erro;
- sugerir próximo passo.

## 7. Untracked files rule
`git diff --stat` não mostra arquivos untracked. Para arquivos novos, conferir `git status --short`, confirmar existência com `test -f` ou `ls`, e usar `git add -N` quando precisar visualizar diff de arquivo novo sem staged real.

## 8. Final states
Toda tarefa precisa terminar com `DONE`, `NEEDS_REVIEW`, `BLOCKED` ou `NO_CHANGES`.

## 9. Final handoff
Sempre incluir status final, arquivos criados/alterados, comandos executados, evidências, validações, riscos, pendências, git status final e próximo passo recomendado.

## 10. Telegram continuity
Mensagens adicionais durante tarefa ativa não devem apagar contexto anterior. Se forem complemento, responder `ACK` e incorporar. Se mudarem escopo, responder `NEEDS_CONFIRMATION`. Não interromper automaticamente sem necessidade.

### Validação obrigatória:
- `git status --short`
- `git diff --check`
- `test -f docs/HERMES_OPERATIONAL_RELIABILITY.md && echo "reliability doc exists"`
