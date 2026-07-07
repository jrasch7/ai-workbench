# AIW Local Monolith MVP — Release Notes

Generated UTC: 2026-06-18 15:11:27 UTC
Branch: feature/aiw-local-monolith-mvp
HEAD: b8e406f feat: add run rejection command

## Summary

This branch delivers the first local monolith MVP of AI Workbench.

The MVP provides a complete local task lifecycle:

- create task;
- create document task;
- run once;
- run in watch mode;
- call LLM optionally through LiteLLM;
- store run evidence locally;
- list runs;
- inspect runs;
- approve runs;
- reject runs;
- run local doctor diagnostics;
- operate through the main `scripts/aiw` command.

## Local lifecycle

Current supported flow:

- inbox -> review -> done
- inbox -> review -> failed

## Main commands

- `./scripts/aiw local-status`
- `./scripts/aiw task "Task title"`
- `./scripts/aiw doc-task "Task title" docs/file.md`
- `./scripts/aiw run-once`
- `./scripts/aiw watch`
- `./scripts/aiw runs 5`
- `./scripts/aiw show latest`
- `./scripts/aiw approve latest`
- `./scripts/aiw reject latest "reason"`
- `./scripts/aiw doctor-local`

## Guardrails

The MVP keeps these boundaries:

- no automatic commit;
- no automatic push;
- no deploy;
- no `.env` reading by generated tasks;
- no secret exposure;
- runtime files stay under `.aiw` and are ignored;
- document executor only writes under `docs/*.md`;
- human review is required for `done` or `failed`.

## Commits in this branch

b8e406f feat: add run rejection command
5caad39 fix: make local doctor resilient to model provider outages
2a4da0e feat: add local doctor command
3e3c11b feat: wire local MVP commands into aiw CLI
a7ec3d2 feat: add run inspection commands
1824ad6 feat: add run approval command
75e3f54 fix: add fallback for L1 document generation
8459072 feat: add L1 document executor
ac08219 fix: default local runner to working Gemini model
39ffbea feat: add optional local LLM adapter
e719eb8 feat: add local AIW runner watch
6f19aaa feat: add local AIW runner MVP
