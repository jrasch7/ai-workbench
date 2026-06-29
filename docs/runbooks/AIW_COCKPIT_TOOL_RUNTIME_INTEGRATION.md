# AIW Cockpit Tool Runtime Integration

## Resultado
Integração concluída com sucesso. O AIW Cockpit agora suporta nativamente a execução de runs em modo Agent (Tool Runtime), com UX aprimorada para exibir uso de ferramentas e timeline sem expor logs técnicos brutos na interface principal.

## Arquivos alterados
- `scripts/aiw-cockpit`

## Integração implementada
- Foi criada a função backend `run_agent_from_cockpit` para acionar, de maneira controlada e segura, o subprocesso `scripts/aiw-runner-agent`.
- Adicionada a rota `POST /runner/run-agent` para responder às solicitações da UI para rodar a fila no modo Agent.
- Mantido integralmente o endpoint `/runner/run-once` para manter retrocompatibilidade com as pipelines "One-shot" (fluxo legado).

## UX implementada
- **Lista de runs**: Um selo visual ("badge") "Agent" (com destaque em cor primária) foi incluído nos cards para runs que utilizaram ferramentas. Ele verifica a presença do arquivo interno `tool-traces.jsonl` e adapta a interface sem exibir o caminho explícito na lista.
- **Detalhes do run**:
  - A interface detalhada foi totalmente enxuta de ruídos técnicos pesados.
  - Implementada a seção "Ferramentas usadas", listando de forma legível e interativa as ferramentas invocadas (nome limpo, args abstraídos e resultado).
  - Implementada a seção "Linha do tempo", processando a árvore de comunicação via `messages.json` e traduzindo eventos para estados amigáveis como "Tarefa criada / Prompt recebido", "Modelo chamou ferramentas", etc.
  - Todos os arquivos internos persistentes (`status.json`, `commands.log`, `tool-traces.jsonl`, json puro, etc) foram isolados em uma seção colapsável ("Avançado: Ver evidências técnicas e arquivos brutos").
- **Ações na UX**: Agora o painel de criação/próxima execução apresenta abertamente ao usuário os dois botões sem sobreposição ("Executar One-shot (Legado)" e "Executar modo Agent").

## Endpoints / UI
- `POST /runner/run-agent`: Processa o `form` de inicialização de um task modelando com ferramentas (Tool Runtime Phase 3).
- O backend garante a passagem sanitizada do nome do modelo (`AIW_MODEL`).

## Como executar
Iniciar normalmente o Cockpit:
```bash
AIW_COCKPIT_OPEN_BROWSER=0 \
AIW_LLM_ENABLED=1 \
AIW_MODEL=dev-coder \
./scripts/aiw-cockpit
```
Após estar rodando (na porta padrão 8765):
1. Entre na interface ou envie um POST (via composer nativo de Nova Task).
2. Na fila (Inbox), clique em "Executar modo Agent".
3. Visualize os resultados com Timeline e Ferramentas Usadas renderizadas intuitivamente.

## Validações executadas
- Validações estáticas (`bash -n`) rodaram sem erros sobre `scripts/aiw-cockpit`, `aiw-runner-agent` e `aiw-tool-smoke`.
- Compilação Python sem erros no engine do agente: `python3 -m py_compile aiw_runtime/*.py`.
- Run isolado via extractor/validador embedded do `aiw-cockpit` (EMBEDDED_PYTHON_OK).
- Remoção minuciosa de `trailing whitespaces` reportados em checagem pelo `git diff --check`.
- Teste autônomo e de comunicação limpa `scripts/aiw-tool-smoke` registrou `SUCCESS: Model returned tool_calls`.

## Evidências
- As verificações provaram que as chaves da aplicação e variáveis de ambiente mantiveram-se restritas.
- O novo script do cockpit não cria injeção de parâmetros (shell injection prevention garantido pela arquitetura subprocess controlada).

## Segurança
Confirmar:
- não alterou .env;
- não imprimiu secrets;
- não mexeu em Hermes;
- não usou OpenHands;
- não removeu runner legado;
- não fez push.

## Riscos restantes
- A visualização na Timeline assume consistência de JSON puro; eventuais panes no logger interno do Agent durante interrupções forçadas precisariam de handling gracioso de exceção na leitura da interface, ainda que tenha sido adicionado um bloco try-except global e fallback na leitura do cockpit.
- Futuras implementações do filesystem tools (`file_write`, `file_patch`) precisarão ser rastreadas da mesma forma para UX rica.

## Próximo passo recomendado
- Fazer o commit das mudanças desta Integração de Interface:
  `git commit -m "feat(aiw): integrate tool runtime with cockpit"`
- Posteriormente seguir para a próxima fase técnica (Tool Runtime Phase 3D) e liberar os hooks operacionais `file_write` / `file_patch`.
