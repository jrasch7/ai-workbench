# Model Router - AUTO Mode

## How AUTO Works

When a user selects "AUTO" (or no specific model), the Model Router analyzes the task and chooses the best combination.

### Decision Factors
- Task category (refactoring, testing, security, research, documentation, etc.)
- Agent Profile constraints
- Cost vs quality vs speed trade-off
- Context window requirements
- Provider availability and latency
- Historical performance (from Experiment Lab)

### Output
The router returns:
- Chosen Model Provider
- Specific model
- Recommended parameters (temperature, max_tokens, reasoning effort)
- Rationale (for logging and UI)

## Example Rules (initial heuristics)

- Large structural changes or complex reasoning → High-capability model (e.g. Claude 3.5/Opus class)
- Test generation or boilerplate → Fast/cheap model (DeepSeek, Qwen, local)
- Security/pentest → Models strong in code analysis
- Simple edits → Local or fast model

Future versions will use data from the Experiment Lab to improve decisions.
