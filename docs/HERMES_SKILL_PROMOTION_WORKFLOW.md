# Hermes Skill Promotion Workflow

## 1. Purpose

Este documento define como uma skill criada ou alterada automaticamente pelo Hermes pode ser revisada, classificada, promovida, arquivada ou descartada.

## 2. Core rule

- Local Hermes skills are drafts.
- Versioned repository skills are operational assets.
- A self-generated skill is not authoritative until reviewed and committed.
- No skill may weaken HERMES.md, Git safety, evidence rules, or handoff rules.

## 3. Sources

- local profile skills in `~/.hermes/profiles/aiworkbench/skills/`
- session history
- Telegram gateway runs
- user‑approved prompts
- manual operator notes
- Obsidian Inbox notes

## 4. Promotion states

- captured
- draft
- quarantined
- under_review
- approved_local
- promoted_to_repo
- converted_to_runbook
- converted_to_obsidian_note
- rejected
- archived

## 5. Review checklist

- frontmatter is valid
- name and description are clear
- trigger condition is clear
- scope is explicit
- commands are safe
- no secrets
- no `.env`
- no destructive commands
- no unauthorized commit/push
- no `git config user.name`
- no `git config user.email`
- no conflict with `HERMES.md`
- no conflict with `skills/hermes/git-safe-workflow/SKILL.md`
- no outdated temporary task state
- validation steps are present
- final handoff is present

## 6. Promotion paths

- keep as local draft
- promote to `skills/hermes/<skill-name>/SKILL.md`
- convert to `docs/<runbook>.md`
- convert to Obsidian note
- quarantine
- discard

## 7. Quarantine rule

Skills que enfraquecem segurança, removem guardrails, autorizam commit/push indevidamente, alteram identidade Git ou misturam estado temporário devem ser copiadas para backup e removidas do caminho ativo.

## 8. Repo promotion requirements

- create or update a versioned skill under `skills/hermes/`
- review diff
- run `git diff --check`
- run grep validation for required safety terms
- ensure no unrelated files changed
- commit only after human approval
- push only after human approval

## 9. Obsidian integration

Toda promoção relevante pode gerar uma nota de revisão usando `docs/obsidian/templates/skill-promotion.md`.

## 10. Current example

- `telegram‑smoke‑tests` was captured as a local self‑generated draft.
- It was reviewed and corrected.
- Unsafe or incomplete instructions were removed.
- A curated version was promoted to `skills/hermes/telegram-smoke-tests/SKILL.md`.
- local `git‑safe‑workflow` was quarantined because it diverged from the versioned safety rules.

## 11. Operator commands

- `find ~/.hermes/profiles/aiworkbench/skills -type f -mmin -60`
- `diff -u skills/hermes/<name>/SKILL.md ~/.hermes/profiles/aiworkbench/skills/software-development/<name>/SKILL.md`
- `git status --short`
- `git diff --check`
- `git diff --stat`