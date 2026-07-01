# AIW LLM Queue Execution Guard

## Resultado

O **LLM Queue Execution Guard** atua como uma trava rígida para garantir que a transição de um sistema offline/puramente estático (Integration Inbox e manual agent queue) para um sistema ativo conectando-se a LLMs só ocorra de forma altamente intencional, com rastreabilidade total e explicitamente bloqueado por padrão (default-deny).

## llm_execution profile

O guardrail começa na estrutura base do perfil do workspace, através do bloco estrito `llm_execution` (`config/aiw-workspaces.example.json`).
Se `enabled` não for explicitamente `true`, ou se o array de `allowed_models` estiver vazio, ou mesmo ausente, *nenhuma* requisição pode alcançar a ponte do LLM.

## Dry-run

Para testar as travas do Guard, foi estabelecido que execuções de intenção sobre itens LLM na Agent Run Queue ocorrem por padrão em modo `dry_run`. Se `--confirm-llm` não for passado (mesmo com `--run-llm` acionado), a CLI apenas registra na sub-pasta `attempts/` a inteção de acesso barrada (`"mode": "llm_dry_run"`) mantendo o ambiente e os status puros e intactos.

## Manual LLM execution

A execução LLM só é desbloqueada via terminal hospedeiro do Workbench executando:
`./scripts/aiw-agent-queue --workspace <ws> --item <item> --run-llm --confirm-llm --model <model>`

Este comando dispara o `subprocess.run(shell=False)` chamando `./scripts/aiw-runner-agent` (onde as travas de offline mode finalmente caem e AIW_LLM_ENABLED=1), engatilhando o LiteLLM. A execução é travada com um `timeout_seconds` herdado estritamente do profile.

## Attempts

Toda vez que uma invocação falha ou tem sucesso, é persistido o registro na tentativa do item (e.g., `att-xyz123.json`), contendo o exit code do subprocesso e um dump truncado defensivamente (via `max_stdout_chars`) do log do AI. Nenhum dado sensível (`.env`, auth) entra aqui.

## Cockpit

Na tela de "Bancada de Execução" > "Agent Run Queue", o Cockpit atua com **LLM Execution Guard Visualizer**, lendo a API `/api/workspaces/.../profile` e informando claramente à equipe se a LLM está ativada.
A interface não tem botões HTML de execução (nem rotas da API). A execução é delegada à linha de bash, copiável pela UI.

## Segurança

- sem daemon;
- sem cron;
- sem execução pela UI;
- exige `--run-llm`;
- exige `--confirm-llm`;
- exige modelo permitido;
- shell=False;
- não altera `config/litellm.yaml`;
- não lê `.env`;
- não aplica patch automaticamente;
- não commita;
- não faz push.

## Limitações

- depende do runner existente;
- depende da configuração externa de modelos já existente;
- sem retry automático;
- sem fallback automático entre modelos;
- sem scheduler.

## Próximo passo recomendado

O último elo para fechar a esteira do AIW de vez: introduzir a função **Handoff & Patch Apply Reviewer**, permitindo que o Cockpit acione a rotina de aplicar na árvore de trabalho (`project_patch_apply`) um patch gerado de maneira supervisionada, após a aprovação de todos os Gates!
- [AIW Agent Patch Review & Apply Flow](AIW_AGENT_PATCH_REVIEW_FLOW.md)
