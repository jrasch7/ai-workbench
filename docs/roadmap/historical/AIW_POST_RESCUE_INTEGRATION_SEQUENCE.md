# PRD: Post Rescue Integration Sequence

**Objetivo**

Definir a sequência operacional a ser seguida depois que o código local do PC antigo for resgatado e integrado ao repositório, garantindo que a documentação estratégica existente (branch `docs/aiw-agent-stack-and-roadmap`) permaneça consistente e que as mudanças de código sejam revisadas de forma segura.

**Contexto**

- O PC antigo contém alterações não commitadas relacionadas ao Cockpit (Phase 6.5/7).
- A branch `docs/aiw-agent-stack-and-roadmap` já contém apenas documentação e não interfere no código.
- Precisa‑se de um fluxo claro para comparar, revisar e integrar essas mudanças sem perdas de histórico nem conflitos inesperados.

**Sequência Pós‑Resgate (sem merges automáticos)**

1. **Preservar e validar o código resgatado**
   - Verificar que o código está na branch `spike/langgraph-engineering-loop` localmente.
   - Executar `git status --short` e `git diff --stat` para garantir que o working tree está limpo após o commit de resgate.
2. **Comparar com a branch de documentação**
   - `git checkout docs/aiw-agent-stack-and-roadmap`
   - `git diff --name-status spike/langgraph-engineering-loop` → analisar alterações que afetam documentação vs código.
   - Certificar‑se de que não há sobreposição de arquivos (ex.: `docs/` vs `src/`).
3. **Abrir PRs separados**
   - **PR Docs**: criar PR da branch `docs/aiw-agent-stack-and-roadmap` para `main` (ou branch alvo) contendo só os documentos.
   - **PR Código**: criar PR da branch `spike/langgraph-engineering-loop` para `main` contendo as mudanças de código.
4. **Revisão cruzada**
   - Revisores verificam se a documentação ainda reflete o estado real do código (ex.: ADRs, PRDs, diagramas).
   - Atualizar documentos se necessário antes de mesclar.
5. **Aprovar e mesclar documentação**
   - Quando a PR Docs for aprovada, fazer merge (fast‑forward ou squash) sem afetar a branch de código.
6. **Aprovar e mesclar código**
   - Só mesclar a PR Código depois que:
     - Todos os testes CI passam.
     - Validator/Hand off aprova o diff.
     - Nenhum secret foi introduzido (`git diff --check`).
7. **Atualizar roadmap**
   - Pós‑mescla, criar commit que atualiza o roadmap para refletir a nova linha de tempo (ex.: remover etapas já concluídas).
8. **Comunicação**
   - Notificar a equipe (ex.: canal Slack) que a integração foi concluída e que a próxima fase (Phase 7.5 UI) pode iniciar.

**Riscos**

- **Conflitos de merge** entre a branch de docs e a de código se arquivos de mesma pasta forem alterados simultaneamente.
- **Desalinhamento** de documentação caso o código evolua após o PR Docs ser mesclado.
- **Perda de trabalho** se o patch do PC antigo não for salvo corretamente antes de reset.
- **Segredos inadvertidos** – garantir que `git diff --check` seja executado antes de qualquer push.

**Critérios de Aceite**

- Working tree limpa em ambas as branches após as operações.
- Dois PRs abertos e revisados separadamente.
- Documentação revisada reflete o estado atual do código.
- Nenhum secret detectado nos diffs.
- Comunicação enviada ao time informando conclusão.

**Plano de Validação**

- **Manual**: o integrador revisa os PRs, executa `git diff --stat` e verifica checklist de segurança.
- **Automatizado (futuro)**: pipeline CI que verifica que `docs/` não contém alterações de código e que `src/` não contém arquivos markdown de documentação.
