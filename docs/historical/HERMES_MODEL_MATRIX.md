# Hermes Model Matrix

## 1. Purpose

Este documento registra quais modelos são adequados para o Hermes no AI Workbench e em quais contextos devem ser usados.

## 2. Operational rule

- Sem evidência, não aconteceu.
- Modelo só é aprovado para execução se passar em teste real de tool-use, não apenas smoke textual.
- Responder "OK" não prova capacidade de editar arquivos.
- Toda mudança de modelo precisa ser validada com tarefa pequena e verificação externa.

## 3. Current recommendation

- **Executor local controlado:** `google/gemini-3.1-pro-preview`
- **Não aprovado para edição/tool-use:** `google/gemini-3.5-flash`
- **Fallback/rascunho:** `openai/gpt-oss-120b:free`

## 4. Model table

| Model | Provider | Role | Status | Evidence | Known risks | Recommended use |
|-------|----------|------|--------|----------|-------------|-----------------|
| google/gemini-3.1-pro-preview | OpenRouter | critical/local executor | approved for controlled local tool-use | * respondeu smoke simples;\n* criou docs/HERMES_MODEL_TOOL_SMOKE.md corretamente;\n* entregou PROGRESS 1/7 até 7/7;\n* entregou handoff;\n* arquivo foi verificado manualmente;\n* passou H5B.3 Gateway Operations;\n* passou H5B.4 git-safe-workflow;\n* passou H5B.5 retry engineering-handoff;\n* passou H5B.6 task-brief-to-plan. | * ainda exige validação externa humana;\n* já houve tentativa anterior com git checkout inesperado em H5B.5;\n* não deve fazer commit/push sozinho. | * edição local controlada;\n* tarefas críticas pequenas/médias;\n* documentação operacional;\n* skills;\n* tarefas que exigem tool-use real. |
| google/gemini-3.5-flash | OpenRouter | draft/text candidate | not approved for file editing/tool-use in this setup | * respondeu smoke simples;\n* falhou no H5B.3;\n* imprimiu JSON/tool-call como texto;\n* não alterou arquivo;\n* não entregou validação nem handoff. | * pode parecer responder corretamente mas não executar ferramenta;\n* risco de tool-call textual sem ação real. | * rascunho textual;\n* brainstorming;\n* não usar como executor de arquivos. |
| openai/gpt-oss-120b:free | OpenRouter | fallback/free draft model | usable but unstable for larger executor tasks | * criou H5A;\n* executou parte do H5B;\n* teve falhas de path/tool-use no Telegram;\n* gerou tarefa parcial na primeira tentativa Cyber Bench. | * instável para tarefas longas;\n* pode declarar DONE com validação incompleta;\n* pode falhar em paths relativos;\n* exige validação externa. | * rascunhos;\n* respostas simples;\n* fallback;\n* não usar sozinho para tarefa crítica. |

## 5. Validation protocol for new models

- [ ] smoke textual;
- [ ] smoke de criação de arquivo;
- [ ] verificação externa com `git status`;
- [ ] verificação externa do conteúdo do arquivo;
- [ ] teste de progress updates;
- [ ] teste de handoff;
- [ ] teste de falha proposital para validar BLOCKED;
- [ ] remover arquivo de teste;
- [ ] `git status` limpo.

## 6. Cost discipline

- usar modelo pago apenas quando necessário;
- preferir tarefa pequena e objetiva;
- não usar modelo caro para rascunho simples;
- registrar falhas e sucessos antes de trocar default;
- manter uso controlado enquanto orçamento for baixo.

## 7. Current routing policy

- Para executor local crítico: usar `google/gemini-3.1-pro-preview` explicitamente via `-m` e `--provider openrouter`.
- Para Telegram ainda não aprovado: não assumir que modelo aprovado localmente está aprovado no gateway.
- Para Cyber Bench: só usar executor aprovado depois de H6 Telegram confiável.
- Para docs simples: modelo free pode ser usado, mas com validação externa.

## 8. Commands used in tests

```
hermes -m google/gemini-3.5-flash --provider openrouter -z "Responda apenas: GEMINI_35_FLASH_OK" chat
hermes -m google/gemini-3.1-pro-preview --provider openrouter -z "Responda apenas: GEMINI_31_PRO_OK" chat
```
