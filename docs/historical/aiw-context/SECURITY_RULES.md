# Security Rules

- No secrets, keys, or credentials are stored in code or config files.
- All external calls must be audited and limited to read‑only operations.
- Do not invoke any network access that could modify remote resources.
- The LangGraph spike must not perform privileged actions (no sudo, no deletions).
- Any new dependency must be reviewed for security implications before install.
