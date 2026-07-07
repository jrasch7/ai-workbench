# Contributing to AI Workbench

## Core Rule
All contributions must align with the architecture defined in `docs/ARCHITECTURE.md`.

**Do not**:
- Add new features on top of the old `aiw_workspace` monolith
- Couple logic to a specific Model Provider or Execution Provider
- Bypass Policy / Isolation layers
- Ignore the three provider types (Model, Execution, Context)

## Before You Start
1. Read `docs/ARCHITECTURE.md`
2. Read the relevant interface in `docs/interfaces/`
3. Read the relevant guide in `docs/guides/`

## Development Process
- Prefer extending via interfaces and registries.
- New providers must implement the contracts in `aiw/interfaces/`.
- Document changes in the appropriate guide or concept document.
- Update `docs/MIGRATION.md` if your change affects the reorganization plan.

## Documentation
Documentation is part of the product. If you add or change behavior, update the corresponding document in `docs/`.

## Code Style for New Work
- Place new code under the `aiw/` target structure when possible.
- Legacy code in `aiw_workspace/` should only receive minimal fixes.
