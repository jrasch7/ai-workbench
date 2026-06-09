# Hermes Self-Improvement Governance

## 1. Purpose

Explain that Hermes can create and improve skills from real experience, but in the AI Workbench this behavior requires curation.

## 2. Principle

- Self-improvement is allowed.
- Silent promotion is not allowed.
- Local skills are drafts until reviewed.
- Critical operational rules must be versioned in Git.
- Human review is required before promoting self‑generated skills.

## 3. Knowledge layers

- **Hermes local skills**: procedural drafts and reusable workflows.
- **Git repository docs/skills**: versioned operational truth.
- **Obsidian**: second brain for decisions, context, audits, architecture and curated learnings.
- **Session history**: evidence and past conversation recall.

## 4. Skill lifecycle

- captured
- quarantined if risky
- reviewed
- classified
- promoted
- rejected
- archived

## 5. Classification

- keep as local draft
- promote to versioned skill
- convert to runbook
- convert to Obsidian note
- discard as duplicate/noisy/wrong
- quarantine as risky

## 6. Rules for self‑generated skills

- must not override critical safety rules;
- must not weaken Git safety;
- must not remove progress/evidence/handoff rules;
- must not authorize commit/push;
- must not configure Git identity;
- must not store secrets;
- must not promote temporary task state into permanent doctrine.

## 7. Review checklist

- frontmatter valid;
- trigger is clear;
- scope is clear;
- commands are safe;
- no secrets;
- no destructive commands;
- no conflict with HERMES.md;
- no conflict with git‑safe‑workflow;
- no outdated task state;
- validation steps included;
- final handoff included.

## 8. Current H6 finding

- **telegram‑smoke‑tests**: useful draft, needs curation;
- **local git‑safe‑workflow**: quarantined because it diverged from versioned rules and weakened Git identity policy;
- H6E proved authorized commit/push works;
- H6G proved unauthorized commit/push is blocked.

## 9. Promotion rule

A self‑generated skill may only become authoritative after review, diff inspection, validation and commit to the AI Workbench repository.

## 10. Next phase

- H7B: curate telegram‑smoke‑tests;
- H7C: create Obsidian vault structure;
- H7D: define skill promotion workflow.

## 11. Obsidian Knowledge Layer

- Documentation: `docs/OBSIDIAN_KNOWLEDGE_LAYER.md`
- Templates:
  - `docs/obsidian/templates/decision.md`
  - `docs/obsidian/templates/handoff.md`
  - `docs/obsidian/templates/model-test.md`
  - `docs/obsidian/templates/skill-review.md`
  - `docs/obsidian/templates/runbook.md`
