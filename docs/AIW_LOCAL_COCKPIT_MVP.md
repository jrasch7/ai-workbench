# AIW Local Cockpit MVP

O AIW Local Cockpit é uma interface web local e simples para visualizar o estado do AI Workbench.

## Objetivo

Evitar depender apenas do terminal para acompanhar:

- filas;
- runs;
- status;
- runs em review;
- runs aprovados;
- runs rejeitados;
- evidências básicas.

## Comando

Iniciar:

    ./scripts/aiw cockpit

Abrir no navegador:

    http://127.0.0.1:8765

## Variáveis

- AIW_COCKPIT_HOST: host local. Padrão: 127.0.0.1.
- AIW_COCKPIT_PORT: porta local. Padrão: 8765.
- AIW_ROOT: raiz do AI Workbench. Padrão: ~/ai-workbench.

## Endpoints

- GET /
- GET /api/status
- GET /api/runs

## Guardrails

- servidor local;
- sem autenticação neste MVP;
- não expõe .env;
- não executa tasks;
- não aprova runs;
- não rejeita runs;
- não faz commit;
- não faz push;
- apenas lê `.aiw` e renderiza estado.

## Próximos passos

- tela de detalhe do run;
- botões locais para approve/reject;
- filtro por status;
- auto-refresh;
- integração posterior com Hermes/Ralph/Paperclip.
