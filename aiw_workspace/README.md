# aiw_workspace — Legacy Monolith (Being Migrated)

**Status:** Legacy / In Migration (continuing)

This package grew into a large monolith containing many different concerns:
- Agent orchestration (now primary in aiw/agent)
- Policy, Isolation, and Runtime Gates (primary in aiw/policy)
- Execution (CodeAct migrated to aiw/providers/execution)
- Patch review, evidence, coverage
- Integration, queues (thinned, delegates to aiw/queue), workers (thinned)

More thin delegates added: worker_loop, agent_queue. See docs/MIGRATION.md for status.
New code must target aiw/.
- etc.

See the target architecture in `../docs/ARCHITECTURE.md`.

## Migration Plan
- Core logic will move to `../aiw/core/`, `../aiw/agent/`, `../aiw/policy/`, etc.
- Providers will move to `../aiw/providers/`
- Do not add significant new code here.

Existing functionality is preserved during reorganization.
