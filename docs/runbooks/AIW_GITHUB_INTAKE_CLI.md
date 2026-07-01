# AIW GitHub Intake CLI

## Resultado

O **GitHub Intake CLI** é responsável por consumir dados externos do GitHub (Issues ou Pull Requests) e prepará-los localmente sob o formato de `Integration Inbox` Items. A ferramenta em si não executa Agentes, não edita nada externamente, e seu propósito é preparar um **Patch Intent** local para revisão e futuro acionamento.

## Dry-run

O CLI opera em modo dry-run por padrão. Se invocado sem as flags de `fetch`, ele apenas simula os parâmetros, mas não aciona o `gh` cli e registra apenas um log em `attempts/` dizendo que a intenção de fetch foi válida. Nenhuma pasta local de Inbox real é populada.

## Fetch mode

Quando rodado com `--fetch` e `--confirm-external-read`, o CLI faz a ponte com o comando bash `gh` via `subprocess.run(shell=False)` capturando a saída JSON pura da issue ou do PR, sem afetar o git working tree.

## GitHub Issue

Os comandos restritos executados via wrapper para issues são:
`gh issue view <num> --repo owner/repo --json ...`

## GitHub PR

Para Pull Requests o fetch também captura branch info (head, base) com:
`gh pr view <num> --repo owner/repo --json ...`

## Patch Intent

Para todo item capturado, o CLI constrói arquivos limpos (`patch-intent.md` e `patch-intent.json`) que explicam resumidamente qual é o objetivo de implementação sugerido. Nesta v1, o AIW não permite o campo `automation_allowed=true`, exigindo que um desenvolvedor examine no Cockpit e gere manualmente a requisição para um Agente, garantindo isolamento total. 

## Integration Inbox

A UI lê todos os items armazenados na pasta ignorada `.aiw/workspaces/*/integration-inbox/` e os renderiza no Harness de Execução. 

## Segurança

- read-only absolulamente estrito;
- exige as duplas flags `--fetch` e `--confirm-external-read` para executar o binário do Github.
- não edita GitHub;
- não comenta nem fecha Issues;
- não cria patches;
- não aciona as instâncias do runner-agent;
- `.env` e as chaves master não são lidas;
- `shell=False` estrito impedindo shell arguments injection do ID das issues.

## Limitações

- Não existe suporte a Webhooks nesta versão.
- Github CLI (`gh`) precisa existir no OS hospedeiro do Workbench e estar autenticado.
- Sem Jira.
- Nenhum LLM é usado para criar o *summary*. É apenas uma cópia simples e limitada.

## Próximo passo recomendado

Plugar LLM de leitura de intenção (Intent Parser): Ler `source.json` usando a `aiw_runtime` com um modelo de baixo custo pra extrair acceptance criteria claros e reescrever o `patch-intent.md` magicamente.
