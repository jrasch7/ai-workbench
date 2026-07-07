# Hermes Context & Quality Harness

## 1. Objetivo
Este documento define o protocolo operacional para transformar o Hermes de um agente que apenas responde/escreve em um agente que recupera contexto, valida evidência, compacta memória, reseta sessão com continuidade e entrega trabalho verificável.

## 2. Problema observado
A falha na criação do ROADMAP.md ocorreu devido a:
- Prompt amplo demais.
- Mistura de fontes sem etapa de verificação.
- Ausência de *Evidence Map* antes da escrita.
- Ausência de validação automática das afirmações.
- Markdown quebrado.
- Divergência entre relatório e conteúdo real.
- Risco de uso de memória antiga ou documentos conflitantes.

## 3. Princípio central
**Nenhum documento estratégico, roadmap, PRD, arquitetura ou decisão permanente pode ser escrito diretamente pelo agente sem uma etapa anterior de *Evidence Map*.
**

## 4. Hierarquia de fonte de verdade
| Prioridade | Fonte |
|-----------|-------|
| 1 | Decisão explícita recente do João no chat atual |
| 2 | Documento aprovado e commitado no Git |
| 3 | ADRs, governança e docs técnicos específicos |
| 4 | `README.md` |
| 5 | Documentos antigos ou experimentais |
| 6 | Memória interna do Hermes |
| 7 | Inferência do modelo |

**Regra:** Se duas fontes conflitam, o agente deve declarar o conflito e pedir decisão ou marcar como pendente, nunca escolher silenciosamente.

## 5. Evidence Map
Formato obrigatório (tabela ou lista):
```
| Claim | Fonte | Evidência | Status | Ação |
|-------|-------|-----------|--------|------|
| ...   | ...   | ...       | ...    | ... |
```
**Status permitidos:**
- `confirmado`
- `contraditório`
- `sem evidência`
- `inferido`
- `pendente de decisão`

**Regras:**
- Claim `confirmado` pode entrar no documento final.
- Claim `contraditório` exige destaque no relatório.
- Claim `sem evidência` não pode virar fato.
- Claim `inferido` deve ser marcado como inferência.
- Claim `pendente de decisão` não deve ser promovido.

## 6. Protocolo de criação documental
1. **Context Scan** – identificar objetivo, fontes relevantes e estado do Git.
2. **Evidence Map** – mapear cada claim com fonte e status.
3. **Conflict Report** – listar e sinalizar conflitos de fonte.
4. **Outline** – esqueleto do documento.
5. **Draft** – rascunho baseado no Evidence Map.
6. **Self‑check** – revisar claims vs. evidência.
7. **Markdown validation** – garantir sintaxe válida.
8. **Git diff review** – analisar alterações.
9. **Human approval** – obter consentimento explícito.
10. **Commit only after authorization**.

## 7. Context Manager
O Hermes deve decidir o que entra na janela de contexto:
- objetivo da tarefa;
- fonte de verdade prioritária;
- documentos relevantes;
- estado do Git (arquivos modificados, branches);
- decisões recentes;
- restrições de segurança;
- comandos permitidos;
- critérios de sucesso.

**Deve excluir do contexto:**
- logs longos não necessários;
- outputs duplicados;
- documentos antigos sem relação;
- memória interna sem confirmação;
- segredos e arquivos `.env`.

## 8. Reset e compactação de sessão
Quando a sessão ficar longa, confusa ou o Gateway reiniciar, criar um *snapshot* contendo:
- objetivo atual;
- estado do Git;
- arquivos alterados;
- decisões tomadas;
- bloqueios;
- comandos executados;
- evidências coletadas;
- próximos passos;
- o que **não** fazer.

**Modelo de snapshot:**

```markdown
# SESSION SNAPSHOT — AIW

## Objetivo atual
...

## Estado do Git
...

## Arquivos alterados
...

## Decisões tomadas
...

## Evidências
...

## Bloqueios
...

## Próxima ação segura
...

## Não fazer
...
```

## 9. Scorecard de qualidade do agente
| Critério | Nota (0‑5) |
|----------|-----------|
| Factualidade |
| Uso de evidência |
| Obediência ao escopo |
| Qualidade do Markdown |
| Completude |
| Segurança |
| Clareza do relatório |
| Capacidade de corrigir erro |
| Não invenção de estado |
| Separação entre fato, plano e hipótese |

**Regra:** Qualquer entrega com factualidade < 4 ou segurança < 5 não pode ser commitada.

## 10. Guardrails automáticos mínimos
- `git status --short`
- `git diff --check`
- `git diff --stat`
- `grep` de termos suspeitos definidos pela tarefa
- validação se todos os arquivos alterados estão no escopo
- revisão de Markdown
- confirmação explícita de que commit/push não foram realizados

## 11. Aplicação ao ROADMAP.md
A próxima tentativa de criar ROADMAP.md deve seguir este ciclo:
1. Criar *Evidence Map*.
2. Resolver conflitos de fonte.
3. Aprovar matriz de ferramentas.
4. Aprovar rings.
5. Só então escrever o roadmap.
6. Validar Markdown e diff.
7. Submeter para revisão humana.

## 12. Estado de maturidade deste harness
- **Ring 0** – documentado, ainda não automatizado.
- Necessita teste em nova tentativa real de ROADMAP.md.
- Evoluirá para Ring 1/2 quando transformado em script, checklist ou skill versionada.

## 13. Próximas ações
- Testar este protocolo na recriação do ROADMAP.md.
- Criar template de *Evidence Map*.
- Criar template de *Session Snapshot*.
- Criar script/check de Markdown e termos suspeitos.
- Criar skill Hermes apenas após revisão humana.
- Registrar resultados no Obsidian depois de validado.
