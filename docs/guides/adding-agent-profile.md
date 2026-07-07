# Adding or Customizing an Agent Profile

## Location
Profiles are declarative (JSON/YAML) + can have associated system prompts.

Recommended location: `aiw/profiles/` or workspace-level overrides.

## Structure
See `docs/interfaces/agent-profile.md` for the schema.

## How to add a new one
1. Define the profile configuration in aiw/profiles/loader.py BUILTIN_PROFILES.
2. Decide: allowed_model_providers, execution_provider + allowed_execution_providers (codeact/docker/devcontainer), llm_planning_allowed (polish 7), tools.
3. Create or reference a system prompt.
4. Register so it appears in Cockpit / CLI / Experiment Lab.
5. Test via aiw-agent-loop --profile NAME and experiment bench/arena.

## Round 2 notes
- llm_planning_allowed controls whether real LLM planner is used.
- execution_provider drives router + future exec selection.
- Profiles now drive more of the Provider-First flow.
5. Test with different tasks in the Experiment Lab.

Profiles are the main way users customize behavior without changing core code.
