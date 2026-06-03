# Role Aliases — AI Workbench

Este documento define os aliases oficiais de modelo por papel dentro do AI Workbench.

## Principio

A operacao da bancada deve usar aliases por funcao, nao por provedor.

O usuario e os agentes devem pedir `dev-coder`, `dev-review` ou `dev-architect`.

O LiteLLM decide qual provedor esta por baixo.

## Aliases operacionais

### dev-coder

Uso:

- implementacao;
- edicao de codigo;
- correcao focada;
- scripts;
- mudancas pequenas em arquivos reais.

Status atual:

- roteado para Gemini;
- validado via `./scripts/aiw smoke dev-coder`;
- usar no OpenHands como `openai/dev-coder`.

### dev-review

Uso:

- revisao de diff;
- validacao;
- analise de risco;
- checagem de regressao;
- leitura critica de entrega de executor.

Status atual:

- roteado para Gemini;
- validado via matrix;
- deve ser usado por agentes validadores.

### dev-architect

Uso:

- planejamento;
- decomposicao de tarefa;
- analise de arquitetura;
- tradeoffs;
- criacao de plano para executor.

Status atual:

- roteado para Gemini;
- validado via matrix;
- deve ser usado antes de tarefas grandes ou arriscadas.

## Aliases de laboratorio e comparacao

### dev-gemini-coder

Alias explicito para testar Gemini diretamente.

Nao deve ser o alias principal do fluxo operacional.

### dev-openrouter-free

Alias explicito para testar OpenRouter free tier.

Pode falhar por rate limit, provider indisponivel ou instabilidade upstream.

Nao deve ser usado como base critica.

## Regra de uso no OpenHands

Na configuracao do OpenHands, usar preferencialmente:

```text
openai/dev-coder
```

Para fluxos futuros, podemos usar:

```text
openai/dev-review
openai/dev-architect
```

## Validacao obrigatoria

Antes de usar agente em projeto real:

```bash
./scripts/aiw doctor
```

```bash
./scripts/aiw gateway
```

```bash
./scripts/aiw matrix dev-coder dev-review dev-architect
```

## Decisao estrategica

A bancada deve trocar provedores por baixo sem mudar o fluxo de trabalho.

Se amanha `dev-coder` sair de Gemini e for para outro modelo, o usuario e os agentes continuam usando `dev-coder`.
