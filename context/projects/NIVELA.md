# Project Context — Nivela

## Visão

Nivela é um SaaS/ERP para empresas de serviço.

O produto deve vender organização, controle, clareza, profissionalização e crescimento.

A comunicação não deve parecer ERP pesado, antigo ou genérico.

## Segmento inicial

Foco inicial:

- barbearias;
- salões de beleza;
- clínicas de estética;
- negócios de beleza e atendimento recorrente.

Expansão planejada:

- pet shops;
- estúdios de tatuagem;
- oficinas;
- assistências técnicas;
- clínicas pequenas;
- manutenção e outros serviços com agenda, clientes, equipe, financeiro e operação.

## Módulos principais

- agenda;
- clientes/cadastros;
- serviços;
- produtos;
- pedidos/lancamentos;
- financeiro;
- caixa;
- planos e recorrência;
- equipe/profissionais;
- estoque;
- configurações;
- checkout/billing;
- painel SaaS;
- fiscal em fase inicial/simulação/homologação quando aplicável.

## Regras de produto

- Não prometer funcionalidade que não está pronta.
- Não vender como ERP pesado.
- Evitar copy genérica como solução completa para sua empresa.
- Começar falando com beleza/atendimento recorrente sem bloquear expansão futura.
- UI deve parecer moderna, séria e SaaS real.
- Segmentação por vertical deve respeitar labels seguros.

## Segmentação por vertical

Política atual esperada:

- barbearia usa termos como barbeiro quando fizer sentido;
- petshop usa tutor e pets somente quando o segmento permitir;
- estética e outros usam termos genéricos como profissional, cliente e serviço;
- animal/pet só deve funcionar para petshop quando módulo/segmento permitir;
- fora de petshop, pets não devem aparecer nem ser aceitos por endpoint.

## Áreas críticas

- billing SaaS;
- planos e créditos;
- financeiro;
- caixa;
- pedidos/lancamentos;
- agenda;
- segmentação por tenant/vertical;
- permissões;
- dados multi-tenant.

## Status operacional conhecido

Fase 5 de Planos/Créditos está avançada, com etapas 5.1 a 5.7 implementadas ou em validação conforme histórico do projeto.

Após fechamento da frente de créditos, próximas frentes planejadas:

- diagnóstico de condições de pagamento, títulos financeiros e baixa de caixa;
- revisão UI/UX de fila de espera e agenda.

## Regras para agentes

Agente não deve:

- pedir credenciais;
- usar ou expor tokens;
- mexer fora do escopo;
- alterar produção sem autorização;
- prometer que algo está validado sem teste;
- fazer commit/push sem validação e autorização.

Agente deve:

- trabalhar por branch;
- manter escopo pequeno;
- rodar testes aplicáveis;
- revisar git diff;
- atualizar documentação quando fizer sentido;
- gerar handoff objetivo.

## Validação esperada

A validação depende da tarefa, mas pode incluir:

```text
python -m compileall app tests
pytest
pytest tests/test_fluxos_regressao.py
pytest tests/test_agendamento_creditos.py
git diff --check
git status --short
```

## Uso no AI Workbench

Antes de qualquer tarefa real no Nivela, anexar este contexto e um task brief específico.

Nunca pedir ao agente para arrumar o Nivela inteiro.

Sempre quebrar em diagnóstico, plano, implementação pequena, validação e handoff.
