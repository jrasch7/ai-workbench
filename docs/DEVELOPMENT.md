# Development Guide

## Current Focus (as of this document)
Documentation and structural alignment with the target architecture.

No major feature development should happen until the documentation and high-level structure are solid.

## Running the Project
See root README.md and existing runbooks for current commands.

## Working with the New Structure
- New interfaces go in `aiw/interfaces/`
- New provider implementations go in `aiw/providers/`
- Documentation updates go in `docs/` following the structure in `docs/STRUCTURE.md`

## Testing Philosophy
Use the Experiment Lab mindset even for internal changes: measure impact on cost, quality, and behavior across providers when possible.

## Legacy Code
Treat `aiw_workspace/`, `aiw_runtime/`, and `aiw_context/` as legacy. Changes there should be minimal and accompanied by a migration note.
