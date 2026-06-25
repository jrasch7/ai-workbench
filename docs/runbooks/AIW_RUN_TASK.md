# AIW_RUN_TASK Runbook

## Purpose

See AGENTS.md for the operational contract governing agents.
A standard, auditable runner for executing AIW task markdown files with Hermes. It provides logging, reproducibility, and avoids manual clipboard or editor steps.

## Usage
```bash
./scripts/aiw-run-task path/to/task.md
```
- The script must be run from the repository root (it will `cd` there automatically).
- It activates the Python virtual environment (`.venv`) if present.
- Logs are written under `reports/aiw-runs/` with a UTC timestamp.

## Log Location
All logs are stored at:
```
reports/aiw-runs/run-<timestamp>.log
```
The script prints the absolute path of the log after execution.

## Preparing a Task Markdown File
1. Create a markdown file in any directory of the repo, e.g. `tasks/my-task.md`.
2. Include the required sections (see the template at `tasks/templates/engineering-task.md`).
3. The file should contain the full instruction set for Hermes; the script will feed it to `hermes --yolo chat -q "$(cat <file>)"`.

## Safety & `--yolo`
- `--yolo` skips the usual confirmation prompts in Hermes, making the run non‑interactive.
- Use it only for fully vetted, repeatable tasks where you trust the prompt content.
- **Never** use `--yolo` for tasks that involve secret handling, destructive actions, or unreviewed code changes.

## When **NOT** to Use `--yolo`
- Tasks that modify production data or infrastructure without prior review.
- Any operation that requires human approval before proceeding.
- When the task includes secrets, credentials, or requires interactive validation.

## Validation Checklist (run automatically by CI)
- `bash -n scripts/aiw-run-task`
- `chmod +x scripts/aiw-run-task`
- `./scripts/aiw-run-task` → exits with usage message.
- `./scripts/aiw-run-task missing.md` → exits with clear error.
- `git diff --check` – no whitespace errors.
- `git status --short` – only intended changes present.

## Integration
- Add new task markdown files to version control.
- Run the script locally; logs are kept for audit trails.
- CI can invoke the script in a head‑less environment for automated runs.
