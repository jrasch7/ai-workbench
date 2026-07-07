# How the Cockpit Should Consume Interfaces

## Rule
The Cockpit (and all UIs/CLIs) **must** consume only public interfaces. They should not import directly from internal implementation modules.

## Expected Consumption Points
- List available Model Providers → via Model Provider Registry
- Trigger AUTO routing → via ModelRouter
- Select Agent Profile → via Agent Profile registry
- Execute tasks → via Agent Runtime (which internally uses Router + Planner + Execution)
- View experiments → via Experiment Lab

## Current State
The Cockpit currently reaches into many internal modules. This is technical debt that will be cleaned during migration.

## Recommendation
All new Cockpit features should be developed against the interfaces defined in `aiw/interfaces/` and documented in `docs/interfaces/`.
