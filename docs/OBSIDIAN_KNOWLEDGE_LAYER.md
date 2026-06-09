# Obsidian Knowledge Layer

## 1. Purpose
Explain that Obsidian will serve as the auditable second brain of the AI Workbench, capturing decisions, handoffs, skills, runbooks, model test reports, and contextual knowledge for future reference and compliance.

## 2. Role in the system
- **Hermes skills** = procedural memory.
- **Git docs/skills** = versioned operational truth.
- **Obsidian** = curated knowledge graph, decisions, architecture, handoffs, lessons and context.
- **Session history** = raw execution evidence.

## 3. What belongs in Obsidian
- architectural decisions
- project handoffs
- model test reports
- skill reviews
- runbooks
- incident notes
- Cyber Bench research notes
- Nivela/SisOp context summaries
- lessons learned from Hermes self‑improvement

## 4. What does not belong in Obsidian
- secrets
- tokens
- .env files
- raw private keys
- temporary task noise
- unreviewed hallucinations
- raw logs without summary
- sensitive client data

## 5. Proposed vault structure
- `00_Inbox`
- `01_Decisions`
- `02_Projects`
- `03_Hermes`
- `04_Skills`
- `05_Runbooks`
- `06_Model_Tests`
- `07_Cyber_Bench`
- `08_Nivela`
- `09_SisOpERP`
- `90_Archive`
- `_Templates`

## 6. Tags
- `#aiworkbench`
- `#hermes`
- `#skill`
- `#runbook`
- `#decision`
- `#handoff`
- `#modeltest`
- `#cyberbench`
- `#nivela`
- `#sisop`
- `#security`
- `#validated`
- `#draft`
- `#archived`

## 7. Promotion workflow
1. Hermes learns something.
2. Local skill or session evidence is reviewed.
3. Decision is recorded in Obsidian.
4. Operational rule is committed to Git.
5. Executable procedure becomes a versioned skill.
6. Temporary noise is archived or discarded.

## 8. Review cadence
Recommend a weekly review or review at each major milestone to ensure the vault stays current and aligned with the repository.

## 9. Future integration
Future Hermes capabilities may automatically write notes to Obsidian, limited to the Inbox or predefined templates, ensuring that only reviewed and approved content becomes part of the knowledge graph.

## 10. Skill promotion workflow

Skill promotion is governed by:

- `docs/HERMES_SKILL_PROMOTION_WORKFLOW.md`
- `docs/obsidian/templates/skill-promotion.md`

Use the skill promotion template when reviewing self-generated Hermes skills, deciding whether to keep them as local drafts, promote them to versioned repository skills, convert them to runbooks, convert them to Obsidian notes, quarantine them, or discard them.

A skill created by Hermes self-improvement is not authoritative until reviewed, validated, and promoted through the workflow.

