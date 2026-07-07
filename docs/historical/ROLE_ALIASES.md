# AIW Role Aliases

## Objetivo

Este documento define os aliases operacionais de modelos usados pelo AI Workbench.

A regra principal é:

> Usuários, agentes, cockpit e integrações devem pedir aliases por papel, não nomes crus de provedores.

Exemplos corretos:

- `dev-coder`
- `dev-review`
- `dev-architect`
- `dev-fast`
- `dev-fallback`

O LiteLLM decide qual provedor e modelo real está por baixo.

## Estado atual

Os aliases estáveis foram roteados para o pool validado em 2026-06-26.

Commit de referência:

- `8c67fa7 config: route stable LiteLLM aliases to validated pool`
- `ae52192 test: smoke stable LiteLLM aliases`

Validação principal:

    ./scripts/model-pool-smoke

Resultado esperado:

    OK: LiteLLM operational alias pool smoke passed

## Mapa operacional atual

| Alias | Papel | Modelo/provedor atual | Uso recomendado |
| --- | --- | --- | --- |
| `dev-fast` | rápido / barato / fallback leve | Hugging Face Router → `MiniMaxAI/MiniMax-M3` | tarefas simples, respostas rápidas, fallback comum |
| `dev-balanced` | balanceado | Hugging Face Router → `deepseek-ai/DeepSeek-V4-Pro` | raciocínio geral, validação intermediária |
| `dev-large` | forte / grande | NVIDIA NIM → `nvidia/llama-3.3-nemotron-super-49b-v1` | tarefas maiores, arquitetura, análise mais pesada |
| `dev-coder` | código | Hugging Face Router → `moonshotai/Kimi-K2.7-Code:deepinfra` | implementação, refatoração, leitura de código |
| `dev-review` | revisão | Hugging Face Router → `deepseek-ai/DeepSeek-V4-Pro` | review, validação, auditoria técnica |
| `dev-architect` | arquitetura | NVIDIA NIM → `nvidia/llama-3.3-nemotron-super-49b-v1` | desenho de sistema, decisões estruturais |
| `dev-fallback` | fallback operacional | Hugging Face Router → `MiniMaxAI/MiniMax-M3` | contingência quando outro alias falhar |

## Aliases por provedor

Além dos aliases operacionais, existem aliases crus por provedor para diagnóstico e benchmark.

| Alias cru | Modelo/provedor |
| --- | --- |
| `dev-nvidia-nemotron` | NVIDIA NIM → `nvidia/llama-3.3-nemotron-super-49b-v1` |
| `dev-hf-kimi-code` | Hugging Face Router → `moonshotai/Kimi-K2.7-Code:deepinfra` |
| `dev-hf-deepseek-v4-pro` | Hugging Face Router → `deepseek-ai/DeepSeek-V4-Pro` |
| `dev-hf-minimax-m3` | Hugging Face Router → `MiniMaxAI/MiniMax-M3` |

Esses aliases crus são úteis para smoke, benchmark e troubleshooting, mas não devem ser usados como padrão por agentes.

## Regra de uso

### Para tarefas normais

Use:

    dev-coder
    dev-review
    dev-architect
    dev-fast
    dev-fallback

### Para OpenAI-compatible clients

Quando uma ferramenta exigir prefixo OpenAI-compatible, use:

    openai/dev-coder
    openai/dev-review
    openai/dev-architect
    openai/dev-fast
    openai/dev-fallback

### Para benchmark ou diagnóstico

Use aliases crus:

    dev-nvidia-nemotron
    dev-hf-kimi-code
    dev-hf-deepseek-v4-pro
    dev-hf-minimax-m3

## Regras para agentes

Agentes não devem:

- chamar provedores diretamente;
- depender de Gemini, Groq, OpenRouter, NVIDIA ou Hugging Face no prompt;
- alterar `.env`;
- usar nome cru de provider como default;
- assumir que `dev-coder` sempre será o mesmo modelo.

Agentes devem:

- pedir o papel desejado;
- usar alias estável;
- rodar smoke antes de integrações sensíveis;
- registrar falhas com evidência;
- preservar fallback.

## Comandos de validação

Validar pool operacional completo:

    ./scripts/model-pool-smoke

Validar alias individual:

    ./scripts/model-smoke dev-coder
    ./scripts/model-smoke dev-review
    ./scripts/model-smoke dev-architect

Testar conversa curta:

    ./scripts/model-ask dev-coder "Responda em uma frase curta: AIW OK"

Listar modelos expostos pelo LiteLLM:

    ./scripts/aiw models

## Decisão operacional

O AIW deve tratar `dev-coder`, `dev-review`, `dev-architect`, `dev-fast`, `dev-balanced`, `dev-large` e `dev-fallback` como a interface pública do pool de modelos.

A camada abaixo desses aliases pode mudar sem quebrar Cockpit, scripts, agentes ou futuras integrações controladas.

## Próxima regra antes do Hermes

Antes de conectar Hermes ao AIW runtime:

1. `./scripts/model-pool-smoke` deve passar;
2. Hermes deve usar aliases estáveis;
3. Hermes não deve apontar diretamente para provider cru;
4. o fallback precisa estar documentado;
5. falhas de provider devem gerar evidência.
