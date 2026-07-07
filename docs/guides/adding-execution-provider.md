# Adding a New Execution Provider

## Steps

1. Implement `ExecutionProvider` (see `docs/interfaces/execution-provider.md`).

2. Put it in `aiw/providers/execution/`.

3. Declare supported runtimes (must be compatible with Runtime Gate). See current support for "docker" and "devcontainer".

4. Implement strong validation and dry-run where possible.

5. Register in `aiw/providers/execution/registry.py`.

6. Register capabilities in the Capability Registry (or extend it) if new ops.

7. Test thoroughly with the regression suite and Experiment Lab.

8. Update Agent Profiles (`aiw/profiles/loader.py`) `allowed_execution_providers`.

9. Update runtime_gate if new isolation/runtime profile needed.

## Current providers (Round 2)
- codeact (primary, full legacy bridge)
- docker (stub + foundation; real adapter planned)
- devcontainer (stub + foundation; real adapter planned)

## Important
Execution providers must respect Policy and Isolation decisions. They should never bypass gates. Stubs provide metadata and dry_run for now.
