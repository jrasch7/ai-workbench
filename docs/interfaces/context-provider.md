# Context Provider Interface

**Purpose:** Sources of knowledge that the agent can query for relevant information.

## Interface

```python
class ContextProvider:
    def name(self) -> str: ...

    def retrieve(self, query: str, workspace_id: str, **kwargs) -> list[dict]:
        """Return relevant chunks with source, score, content."""

    def index(self, workspace_id: str, **kwargs) -> dict:
        """Optional: (re)build index for this source."""

    def describe(self) -> dict:
        """What kind of data it provides, freshness, cost."""
```

## Examples
- LocalFilesystemRAGProvider
- GitHistoryProvider
- GitHubIssuesProvider
- ObsidianVaultProvider
- VectorDBProvider
- JiraProvider

## Integration
Context Providers feed into the Context layer and can be selected/combined per Agent Profile.
