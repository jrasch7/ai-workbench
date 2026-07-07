# Model Router Interface

**Purpose:** Intelligent selection of provider + model for a given task.

This is one of the key differentiators of AIW.

## Interface

```python
class ModelRouter:
    def route(
        self,
        task: str,
        profile: AgentProfile | None = None,
        constraints: dict | None = None,  # cost, speed, quality, max_tokens, etc.
        mode: str = "auto"  # "auto" | "specific"
    ) -> dict:
        """Returns {provider, model, params, reasoning}"""

    def list_options(self, task: str, constraints: dict) -> list[dict]:
        """For UI / manual selection."""
```

## AUTO Mode Behavior
When `mode="auto"`:
- Analyze task type (refactoring, testing, security review, research...)
- Consider profile preferences
- Optimize for cost / latency / quality / context window
- Apply fallbacks
- Log decision for observability

## Examples
- Task: "Large refactoring" → Strong reasoning model (Claude Sonnet/Opus via OpenRouter)
- Task: "Write tests" → Fast/cheap model (DeepSeek or local)
- Task: "AUTO" → Router decides based on heuristics + learned data (future)
