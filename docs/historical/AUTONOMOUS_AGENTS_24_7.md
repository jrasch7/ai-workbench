# Autonomous Agents 24/7 Foundation

## 1. Objetivo
Esta é a prioridade máxima do AIW: permitir agentes operando continuamente, com autonomia controlada.

## 2. Princípio central
Autonomia 24/7 não significa ausência de controle. Significa operação contínua dentro de limites pré‑aprovados.

## 3. Níveis de autonomia
| Nível | Nome | Pode fazer | Precisa aprovação | Exemplos |
|------|------|------------|-------------------|----------|
| L0 | Somente leitura | Ler arquivos, logs, documentação | Não | Auditoria somente leitura |
| L1 | Escrita restrita | Criar/editar documentos em `docs/` | Não | Gerar relatórios, atualizar Evidence Map |
| L2 | Código de escopo baixo | Criar branch, alterar código em áreas limitadas | Não | Refatorar utilitários internos |
| L3 | Testes e PR | Executar testes, abrir pull request | Não | Rodar testes unitários, abrir PR para revisão |
| L4 | Jobs recorrentes | Operar cron jobs, pipelines controlados | Não | Executar pipelines de evidence map, gerar snapshots |
| L5 | Produção/sensível | Alterar produção, deploy, manipular secrets | Sim (aprovação humana explícita) | Deploy para produção, alterar `.env` |

## 4. Arquitetura alvo
- **Task Queue** – fila de tarefas pendentes.
- **Scheduler** – agenda execução periódica.
- **Supervisor** – monitoramento e reinício de agentes.
- **Policy Engine** – validação de escopo, custos, permissões.
- **Agent Runner** – ambiente de execução isolado.
- **Sandbox / Devcontainer** – isolamento seguro.
- **Memory / Obsidian / Git** – armazenamento de estado e evidências.
- **Evidence Store** – repositório de logs e artefatos.
- **Logs** – registro estruturado de cada passo.
- **Budget Manager** – controle de custo e tempo.
- **Notification Gateway** – alertas via Telegram.
- **Human Approval Gateway** – ponto de aprovação manual.

## 5. Policy Engine
### Regras práticas da Policy Engine
- **Escopo restrito**: cada comando deve estar listado em whitelist por nível de autonomia. Ex.: `git status` permitido em L2, mas `git push` somente em L5 com aprovação.
- **Custo máximo**: limite de $0.05 por tarefa; a engine aborta se a estimativa supera.
- **Tempo máximo**: 300 segundos para L3/L4, 60 segundos para L1/L2.
- **Rede**: somente chamadas a endpoints internos (`api.aiw.local`) são permitidas; acesso externo requer aprovação L5.
- **Auditoria**: todas as execuções geram um registro JSON em `evidence/` com hash SHA‑256 do script executado.
- **Rollback automático**: se comando altera arquivos, a engine cria um commit temporário de rollback que pode ser revertido se a tarefa falhar.

Cada tarefa deve declarar:
- escopo
- nível de autonomia
- arquivos permitidos
- comandos permitidos / proibidos
- limite de custo
- limite de tempo
- limite de rede
- critério de sucesso
- critério de parada
A engine rejeita tarefas fora das regras.

## 6. Filas de trabalho
- inbox
- planned
- running
- blocked
- review
- done
- failed

## 7. Tarefas que podem rodar sem aprovação
- auditoria somente leitura
- gerar Evidence Map
- criar relatório em `docs/`
- validar Markdown
- rodar `git diff --check`
- rodar testes locais não destrutivos
- criar snapshot
- atualizar Obsidian Inbox (quando autorizado)

## 8. Tarefas que sempre exigem aprovação
- commit
- push
- deploy para produção
- alterações de secrets ou `.env`
- reset de banco de dados
- ação destrutiva
- alteração de identidade Git
- tarefas de Cyber Bench fora de laboratório autorizado

## 9. Loop operacional 24/7
1. coletar tarefa da fila
2. classificar risco via Policy Engine
3. montar contexto
4. executar em sandbox
5. validar saída
6. registrar evidência
7. decidir: done, review, blocked ou retry
8. notificar João somente quando necessário

## 10. Healthcheck e watchdog
- heartbeat periódico
- restart controlado
- limite de retries
- detecção de loops infinitos
- detecção de custo excessivo
- detecção de resposta truncada
- snapshot automático antes de parada

## 11. Logs e evidências
Para cada tarefa registrar:
- task id
- agente
- modelo usado
- prompt resumido
- arquivos alterados
- comandos executados
- validações realizadas
- `git diff --stat`
- decisão final
- custo aproximado
- duração

## 12. Segurança
- **Proibição absoluta** de secrets, `.env`, credenciais de produção.
- Nenhuma operação de produção sem aprovação humana.
- Execução sempre em sandbox.
- Cyber Bench somente dentro de regras de engajamento.

## 13. Papel de Go/Golang
Go/Golang será candidato para:
- `aiwctl`
- supervisor
- workers
- healthchecks
- gateways
- agent runner
- policy engine leve
Status: Ring 0, candidato, fase futura **AIW‑G1**.

## 14. MVP da autonomia 24/7
- agent runner local simples
- fila em arquivos Markdown/JSON
- política por tarefa (L0/L1 apenas)
- logs detalhados em `docs/`
- watchdog básico
- notificação via Telegram
- **sem commit automático**

## 15. Critérios de sucesso
- agente completa tarefa L1 sem intervenção humana
- gera evidência completa
- não altera fora do escopo
- não executa commit/push
- bloqueia tarefas fora de política
- gera snapshot se interrompido
- notifica João somente quando necessário

## 16. Próximas ações
- criar template de task
- criar template de policy
- criar pasta `queue/`
- implementar runner experimental (Python ou Go)
- decidir implementação do `aiwctl` spike
- testar tarefa L1 24/7 com documentação
