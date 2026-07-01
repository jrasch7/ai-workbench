# AIW Patch Evidence Bundle

## Resultado

O Evidence Bundle fornece um registro estruturado, auditável e histórico de todas as evidências analisadas (coverage, validações, score) no momento em que uma decisão (aprovação/rejeição/apply) foi tomada.

## Evidence Bundle

Um *Evidence Bundle* é um snapshot de dados capturado em um determinado instante para um patch. Ele armazena o status do review gate, métricas de coverage e a execução do plano de validação.

## Decision Record

Permite o registro manual (via interface) das seguintes decisões sobre um bundle:
- `approved`
- `rejected`
- `needs_work`
- `applied`
- `rolled_back`

## Risk Summary

Calculado com base em regras heurísticas em cima dos checks do Review Gate:
- **Low**: Gate passed, sem regressions de coverage ou tests.
- **Medium**: Parcial coverage, sem testes, no baseline.
- **High**: Regressions de coverage, test reports com falha ou gate bloqueando apply.

## Apply-reviewed

O apply manual via `apply-reviewed` gera automaticamente um evidence bundle (se necessário) e registra a decisão de `applied` se o apply for bem-sucedido. Continua operando localmente sem fazer commits automáticos ou push no remoto.

## Cockpit

Os evidence bundles e o risk level são renderizados na interface local, com botões rápidos para registrar a decisão do revisor humano.

## Segurança

- não executa testes;
- não aplica automaticamente;
- não commita;
- não faz push;
- não lê .env;
- artifacts locais ignorados.

## Limitações

- operador local fixo;
- risk score heurístico;
- sem assinatura criptográfica;
- sem export externo.

## Próximo passo recomendado

Considerar adicionar Mutation Testing (v1) para aumentar a confiabilidade da intenção de cobertura, ou implementar Sync de estado com provedores externos via CLI local.
- [AIW Patch Evidence Export](AIW_PATCH_EVIDENCE_EXPORT.md)
