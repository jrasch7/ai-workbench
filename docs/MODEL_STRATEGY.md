# Model Strategy — AI Workbench

## Objetivo

Definir a estratégia de modelos LLM da bancada sem acoplar o AI Workbench a um único provedor.

A bancada deve funcionar com modelos gratuitos, pagos, agregadores e provedores diretos, mas a operação séria não pode depender de free tier instável.

## Princípio central

O modelo é substituível.

O processo de engenharia não é substituível.

O AI Workbench deve manter o mesmo fluxo mesmo quando trocarmos OpenRouter, Groq, Gemini, Anthropic, OpenAI ou outro provedor.

## Estado atual

O LiteLLM é o gateway central.

Aliases atuais conhecidos:

```text
dev-fast
dev-balanced
dev-large
dev-openrouter-free
dev-coder
```

Validações atuais:

```text
./scripts/aiw doctor
./scripts/aiw gateway
./scripts/aiw models
./scripts/aiw smoke dev-coder
./scripts/model-pool-smoke
```

## Separação entre tiers

### Laboratório

Uso permitido:

- testar gateway;
- validar scripts;
- testar OpenHands;
- validar fluxo de smoke;
- tarefas pequenas e descartáveis.

Modelos gratuitos entram aqui.

Problemas esperados:

- rate limit;
- provider upstream indisponível;
- latência alta;
- tool call fraco;
- contexto instável;
- resposta inconsistente.

### Operacional

Uso permitido:

- tarefas pequenas em projetos reais;
- implementação com escopo claro;
- revisão simples;
- geração de handoff;
- validação assistida.

Requisitos:

- provider mais estável;
- limite previsível;
- custo monitorável;
- fallback configurável;
- smoke passando.

### Crítico

Uso permitido:

- arquitetura;
- migração;
- financeiro;
- billing;
- segurança;
- revisão de PR importante;
- tarefas que podem causar regressão relevante.

Requisitos:

- modelo forte;
- fallback definido;
- validação humana obrigatória;
- branch isolada;
- testes obrigatórios;
- custo aceito antes da execução.

## Aliases alvo

### dev-fast

Uso:

- respostas rápidas;
- tarefas simples;
- sumarização curta;
- classificação;
- pequenas revisões.

Prioridade:

- baixo custo;
- baixa latência;
- disponibilidade.

### dev-coder

Uso:

- edição de código;
- implementação pequena;
- ajustes em scripts;
- correções focadas.

Decisão atual:

- `dev-coder` é o alias oficial de trabalho para código;
- atualmente está roteado para Hugging Face Router com `moonshotai/Kimi-K2.7-Code:deepinfra`;
- o uso externo no OpenHands deve continuar sendo `openai/dev-coder`;
- o provedor por baixo pode mudar sem alterar o fluxo operacional.

Prioridade:

- seguir instrução;
- tool use estável;
- bom desempenho em código;
- não inventar validações.

### dev-review

Uso:

- revisão de diff;
- validação;
- análise de risco;
- procura de regressão;
- análise de testes.

Prioridade:

- cautela;
- leitura fiel do diff;
- baixa tendência a concordar sem evidência.

### dev-architect

Uso:

- planejamento;
- decomposição;
- decisões técnicas;
- tradeoffs;
- design de tarefas.

Prioridade:

- raciocínio forte;
- contexto longo;
- organização;
- capacidade de declarar incerteza.

### dev-premium

Uso:

- tarefas críticas;
- decisões caras;
- arquitetura difícil;
- revisão final de alto impacto.

Prioridade:

- melhor qualidade disponível;
- custo controlado;
- uso sob demanda.

## Google AI Pro e Gemini

Google AI Pro pode ser útil para trabalho manual, pesquisa, análise e uso no ecossistema Google.

Para o AI Workbench, o que importa é acesso via API.

Gemini deve entrar na bancada somente como provider testável via LiteLLM, usando chave própria em variável de ambiente e passando por smoke/matrix.

Alias futuro sugerido:

```text
dev-gemini-fast
dev-gemini-coder
dev-gemini-architect
```

Regra:

- não commitar chave;
- não colar chave em prompt;
- não expor .env;
- validar com smoke antes de usar em agente.

## Estratégia de fallback

Fallback deve ser por papel, não por marca.

Exemplo conceitual:

```text
dev-coder -> provider principal de código -> fallback operacional -> provider de laboratório
dev-review -> provider principal de revisão -> provider secundário
dev-architect -> provider forte de raciocínio -> provider premium sob demanda
```

Free tier pode ser fallback de laboratório, não fallback operacional crítico.

## Decisão atual de roteamento

```text
dev-coder           -> alias oficial de código, atualmente roteado para Hugging Face Router / Kimi Code
dev-gemini-coder    -> alias explícito para testar Gemini
dev-openrouter-free -> laboratório/fallback não crítico
```

No uso normal da bancada, preferir aliases por papel, como `dev-coder`, em vez de chamar diretamente aliases por provedor.


## Critérios para promover um modelo

Um modelo só pode sair de laboratório para operacional quando:

- passa em ./scripts/aiw smoke;
- passa em ./scripts/aiw matrix;
- executa uma tarefa pequena sem quebrar ferramenta;
- não inventa validação;
- lida bem com arquivos reais;
- custo é aceitável;
- falhas são claras e recuperáveis.

## Critérios para reprovar um modelo

Reprovar ou rebaixar quando:

- retorna erro frequente;
- quebra tool call;
- inventa diff;
- inventa teste;
- ignora escopo;
- tem rate limit constante;
- custa caro sem ganho proporcional.

## Regra de uso em projetos reais

Antes de usar agente em Nivela ou SisOpERP Web:

```text
1. Selecionar Project Context.
2. Criar Task Brief.
3. Rodar aiw doctor.
4. Rodar aiw gateway.
5. Rodar aiw models.
6. Rodar aiw smoke no alias escolhido.
7. Rodar aiw matrix nos aliases candidatos.
8. Só então abrir OpenHands.
```

## Decisão estratégica

A bancada não deve ser construída ao redor de um modelo gratuito.

A bancada deve ser construída ao redor de processo, validação, contexto e troca controlada de modelos.

Modelos bons entram para aumentar potência.

Eles não substituem Git, testes, escopo e validação humana.
