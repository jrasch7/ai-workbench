# AIW Phase 7.6 — Context Resilience / Auto-Compaction

## Objetivo
Garantir que o AIW continue operando de forma confiável mesmo quando o contexto da sessão cresce, ocorre rate‑limit 429 ou falhas de modelo, e que o estado de execução seja persistido e re‑inicializável automaticamente.

## Problema
Operações de longo prazo produzem sessões com centenas de mensagens. O Hermes compacta o histórico repetidamente, o que:
* Aumenta o tamanho dos prompts enviados ao modelo;
* Degrada a precisão porque o modelo perde informações relevantes;
* Aciona o limite de taxa (429) em `gpt‑oss‑120b:free`;
* Interrompe a execução no meio de um run, deixando o agente em estado inconsistente.

## Sintomas observados
- Sessão com muitas mensagens (≥250 linhas) ainda funciona às vezes, mas falha intermitentemente.
- Compactação repetida gera perda de contexto e respostas menos precisas.
- Recebimento de erro HTTP 429 do provedor de modelo.
- Prompts longos demais são truncados ou recusados.
- Execução para abruptamente; o agente perde a continuidade.

## Requisitos
| Requisito | Descrição |
|-----------|-----------|
| **Run state persistido em disco** | Cada “run” grava um diretório de artefatos em `reports/aiw‑runs/<run_id>/`.
| **Compact summary por run** | Ao final de cada fase, o agente gera `compact_summary.md` que resume tudo que aconteceu.
| **Resume prompt curto** | `resume_next_prompt.md` contém apenas as informações necessárias para retomar a execução.
| **Limite de contexto por missão** | Definir um teto (ex.: 8 k tokens) que, ao ser ultrapassado, dispara compactação automática.
| **Checkpoint por etapa** | Salvar `metadata.json` e `diff.patch` após cada sub‑tarefa crítica.
| **Política de `/new`** | Quando o limite for atingido, o agente pode sugerir `/new` para iniciar um novo run, vinculando ao anterior.
| **Fallback de modelo** | Em caso de 429, mudar para modelo secundário (`gpt‑4o‑mini` ou similar) e marcar a mudança em `metadata.json`.
| **Execução shell determinística** | Todos os comandos de auditoria Git são executados via shell com `set -euo pipefail` e registrados em `commands.log`.

## Estrutura esperada dos artefatos
```
reports/aiw‑runs/<run_id>/
├─ metadata.json          # informação de run, timestamps, SHA do modelo, status
├─ prompt.md              # prompt original usado para iniciar a fase atual
├─ commands.log           # stdout+stderr de todos os comandos shell
├─ outputs.log            # saídas relevantes (ex.: resultados de `git`)
├─ diff.patch             # diff gerado pelo agente para alterações propostas
├─ validation.json        # resultados de validações (tests, lint, etc.)
├─ handoff.md             # resumo final para o próximo operador/handoff
├─ compact_summary.md    # resumo compacto da fase completa
└─ resume_next_prompt.md # prompt enxuto para continuar a missão
```

## Critérios de Aceite
- Cada run cria o diretório acima com todos os arquivos listados.
- `compact_summary.md` não ultrapassa 1 k tokens.
- `resume_next_prompt.md` contém menos de 500 tokens.
- Em caso de 429, o agente registra a troca de modelo e continua sem perda de estado.
- O agente pode retomar a partir de `resume_next_prompt.md` reproduzindo exatamente o mesmo estado.

## Riscos
- Aumento de I/O em disco pode impactar performance em ambientes de CI.
- Falhas ao escrever arquivos podem deixar o run em estado inconsistente.
- Dependência de modelo fallback pode introduzir variação nos resultados.

## Plano de Validação
1. Simular um run que gera >12 k tokens de contexto.
2. Verificar que o agente cria `compact_summary.md` e `resume_next_prompt.md` automaticamente.
3. Forçar erro 429 (mock) e confirmar que o fallback de modelo é acionado e registrado.
4. Reiniciar o run usando apenas `resume_next_prompt.md` e validar que o estado final (diff, validation) coincide com a execução original.
5. Executar auditoria de Git (`git status`, `git diff`) e garantir que `commands.log` e `outputs.log` contêm saídas completas e determinísticas.

---
*Este documento foi gerado para orientar a implementação da fase 7.6 de resiliência de contexto no AIW.*