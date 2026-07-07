# Concept: Model Router + AUTO Mode

The Model Router is responsible for deciding **which brain to use** for a given task.

## Inputs
- Task description
- Agent Profile
- Constraints (budget, latency target, quality target, context size)
- Mode: specific or AUTO

## In AUTO mode the router considers
- Task type (refactor, test generation, security analysis, research...)
- Historical performance of models on similar tasks
- Current cost and availability
- Context window requirements
- Reasoning strength needed

## Outcome
Returns a concrete (provider, model, parameters) tuple plus explanation for auditability.

This is one of the highest-leverage features for making any individual LLM much more powerful in practice.
