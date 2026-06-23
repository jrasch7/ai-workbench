# ADR: Stateless Agent Runs

**Status:** Proposed

## Decisão
- Agentes AIW devem operar em ciclos **stateless** entre runs.
- Cada run salva seu estado completo em disco (artefatos, metadados, diffs, logs).
- Execuções subsequentes **retomam** a partir desses arquivos canônicos, não a partir de um chat longo.

## Motivos
1. **Escalabilidade** – eliminar a dependência de contexto de sessão que cresce indefinidamente.
2. **Confiabilidade** – recuperação garantida após falhas de modelo ou limites de taxa (429).
3. **Auditabilidade** – todas as ações são registradas em arquivos versionados, facilitando revisão.
4. **Portabilidade** – o run state pode ser movido entre ambientes (CI, máquinas locais, cloud) sem precisar reproduzir a conversa inteira.

## Consequências
- **Persistência** – necessidade de espaço em disco para armazenar `reports/aiw-runs/<run_id>/`.
- **Complexidade de Orquestração** – o agente precisa gerar e consumir os artefatos (`compact_summary.md`, `resume_next_prompt.md`).
- **Mudança de Fluxo** – usuários precisarão iniciar novos runs (`/new`) ou usar o `resume` ao invés de continuar a mesma sessão.

## Alternativas Avaliadas
| Alternativa | Prós | Contras |
|-------------|------|---------|
| Depender de chat longo | Simples de implementar; aproveita a memória interna do modelo. | Não escala; risco de perda de contexto e 429. |
| Depender apenas de memória do modelo | Menos I/O, mais rápido. | Modelo não é fonte de verdade; perdas de precisão e falhas de taxa. |
| Usar apenas RAG | Mantém o prompt curto, reutiliza documentos. | Ainda requer gerenciamento de estado externo para executar comandos. |
| Usar apenas checkpoint LangGraph | Gerencia estado interno ao grafo. | Não cobre artefatos externos (git, arquivos). |

## Critério para Accepted
- O design inclui **run state store** em disco.
- Existe um processo automatizado que gera **compact summary** e **resume prompt** ao final de cada fase.
- A política de fallback de modelo está documentada e implementada.
- A documentação foi revisada pelo time de arquitetura e aprovada.

---
*Este ADR será atualizado para *Accepted* quando a implementação de persistência de run state estiver concluída e validada.*