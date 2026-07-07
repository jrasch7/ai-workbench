# Adding a New Context Provider

## Steps

1. Implement `ContextProvider`.

2. Location: `aiw/providers/context/`.

3. Support `retrieve()` well — this is what agents rely on.

4. Optionally implement `index()` for background refreshing.

5. Make it discoverable by the Context layer.

6. Document supported data sources.

Example sources: Git, Jira, internal wikis, SQL, vector stores.
