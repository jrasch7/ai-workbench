# Agent Profile

**Purpose:** A reusable configuration that defines "what kind of agent" is running.

Inspired by systems like Manus.

## Structure

```json
{
  "name": "software-engineer",
  "display_name": "Software Engineer",
  "description": "...",
  "preferred_planner": "iterative-v1",
  "allowed_model_providers": ["openrouter", "ollama"],
  "default_model": "claude-3-5-sonnet",
  "temperature": 0.2,
  "tools": ["file_read", "file_write", "codeact_sandbox", "git"],
  "system_prompt": "...",
  "context_strategy": "context-pack + git-diff",
  "required_runtime": "host_best_effort",
  "isolation_level": "standard"
}
```

## Usage
- Selected by user in Cockpit / CLI
- Influences Model Router decisions
- Controls which Execution and Context Providers are available
- Can be customized per workspace or project

## Standard Profiles (initial)
- software-engineer
- security-analyst
- code-reviewer
- architect
- performance-engineer
- devops
- researcher
- technical-writer
