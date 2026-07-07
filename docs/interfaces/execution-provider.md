# Execution Provider Interface

**Purpose:** Abstraction for mechanisms that can actually *do* things in the environment (run code, edit files, execute commands, etc.).

## Interface

```python
class ExecutionProvider:
    def name(self) -> str: ...

    def describe(self) -> dict:
        """Capabilities, supported operations, risk level, required runtime."""

    def validate(self, action: dict | None = None) -> dict: ...

    def supports_runtime(self, runtime: str) -> bool: ...

    def dry_run(self, workspace_id: str, action: dict, **kwargs) -> dict: ...

    def execute(
        self, workspace_id: str, action: dict, confirm: bool = False, **kwargs
    ) -> dict: ...
```

## Key Concepts
- Execution Providers are **separate** from Model Providers.
- They declare what runtimes they support (via Runtime Gate).
- Safety validation happens before execution.

## Current Implementation
- CodeActExecutionProvider (Python sandbox with strict guardrails).

## Future
- DevcontainerExecutionProvider
- DockerExecutionProvider
- NativeShellProvider
- BrowserProvider
- etc.
