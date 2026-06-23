# PRD: Phase 8 – Worktree / Sandbox

**Objetivo**

Permitir a execução de missões em um *worktree* isolado, mantendo a branch principal limpa e garantindo que quaisquer alterações geradas sejam revisáveis antes de integração.

**Problema**

- Alterações diretas na branch principal podem contaminar o histórico e introduzir bugs inesperados.
- Necessidade de validar resultados de agentes sem impactar a base de código estável.

**Requisitos**

- Criação automática de um *worktree* a partir da branch de destino.
- Execução do agente dentro do *worktree* com o mesmo ambiente (Python venv, dependências).
- Coleta de `git diff` ao final da missão.
- Geração automática de um *handoff* (arquivo Markdown) contendo:
  - Descrição da missão
  - Diff resumido
  - Logs relevantes
  - Recomendações de merge ou abandono
- Opção de promover o diff para a branch principal via `git merge --no-ff` (apenas após revisão humana).

**Fora de Escopo**

- Integração automática (auto‑merge) sem revisão.
- Deploy de artefatos compilados.
- Manipulação de arquivos binários grandes.

**Fluxo Esperado**

1. Usuário cria uma missão via Cockpit.
2. O *Run Manager* dispara a criação de um *worktree* (ex.: `git worktree add /tmp/aiw-worktree <target-branch>`).
3. O agente (LangGraph) executa dentro desse diretório usando o *Hermes Executor*.
4. Ao final, o agente captura o diff (`git diff --cached`) e gera um handoff.
5. O usuário revisa o handoff e decide por:
   - **Promover**: `git merge --no-ff <worktree-branch>` na branch principal.
   - **Abortar**: `git worktree remove <path>` descartando mudanças.

**Comandos Git Seguros**

```bash
# criar worktree temporário
git worktree add /tmp/aiw-worktree <target-branch>

# dentro do worktree, aplicar alterações (agente)
# ...

# gerar diff
git diff > /tmp/aiw-worktree.diff

# opcional: revisar e mesclar
git checkout <target-branch>
git merge --no-ff /tmp/aiw-worktree

# remover worktree
git worktree remove /tmp/aiw-worktree
```

**Riscos**

- **Conflitos de merge** se a branch principal evoluir enquanto o worktree está aberto.
- **Uso de espaço em disco** por múltiplos worktrees não removidos.
- **Persistência de segredos** caso o agente escreva arquivos sensíveis no worktree; deve‑se validar ausência de segredos (`git diff --check`).

**Critérios de Aceite**

- Worktree criado e removido cleanly.
- Diff gerado corresponde exatamente às alterações realizadas pelo agente.
- Handoff contém todas as informações listadas acima.
- Nenhum segredo detectado nos arquivos modificados.

**Plano de Validação**

- Testar fluxo completo em um repositório de exemplo.
- Verificar que `git status --short` está limpo após remoção do worktree.
- Executar `git diff --check` para garantir ausência de segredos.
- Revisar handoff gerado por pares.
