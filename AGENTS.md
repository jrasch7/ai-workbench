# AGENTS.md – AI Workbench Operational Contract

## Purpose
The AI Workbench provides a deterministic, auditable engineering platform where **agents** execute tasks under strict operational rules.

## Core Rules
1. **Execution Engine** – Long‑running or multi‑step missions must be run via `scripts/aiw-run-task` to ensure logging, reproducibility, and safe isolation.
2. **Paperclip** – The Paperclip code‑generation component is *frozen* for code engineering; agents must not invoke it.
3. **LangGraph** – All deterministic workflow orchestration is powered by LangGraph. Agents must express their plan as a LangGraph chain.
4. **Source of Truth** – Markdown files in the repository together with Git history constitute the single source of truth.
5. **Pre‑Commit Validation** – Before any commit agents must run all project‑defined checks (e.g., `git diff --check`, lint, tests) and ensure no failures.
6. **Forbidden Artifacts** – Do **not** commit the following:
   - `.venv/` virtual‑environment directories
   - `reports/` generated logs and audit files
   - any secrets, credential files, or token files
   - raw execution logs
7. **.gitignore** – Never overwrite the entire `.gitignore`. Add only the minimal required entries.
8. **Commit Granularity** – Commits must be small, scoped to a single logical change, and include a clear commit message.
9. **Human Decision Point** – Agents must stop and request explicit human approval when:
   - a conflict or ambiguous requirement is detected
   - a change touches security‑sensitive areas
   - the scope of a change exceeds the originally defined boundaries
10. **Final Report Format** – Upon task completion agents emit a concise, structured report (max 20 lines) containing:
    - Branch & HEAD hashes (initial/final)
    - List of altered files
    - Commands executed
    - Validation results
    - Identified risks
    - Next recommended action
11. **Progress Updates** – Agents emit short progress messages prefixed `PROGRESS X/N` where `X` is the step number (e.g., `PROGRESS 1/5 – confirming branch`).

## Agent Roles
- **Architect** – Plans, scopes, and assesses risks.
- **Executor** – Implements the scoped change.
- **Validator** – Runs validation checks, reviews diffs.
- **Integrator** – Performs the final commit/push after human approval.

---
*All agents must adhere to this contract when operating within the AI Workbench repository.*
