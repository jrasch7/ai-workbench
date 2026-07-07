# Adding a New Model Provider

## Steps

1. Implement the `ModelProvider` interface (see `docs/interfaces/model-provider.md`).

2. Place the implementation under `aiw/providers/model/your_provider.py`.

3. Register it in the central Model Provider Registry (will be defined in `aiw/providers/model/registry.py`).

4. Add configuration support (API keys via environment or workspace config — never hardcode).

5. Update the Model Router to be aware of the new provider (usually automatic via registry).

6. Add tests in the Experiment Lab (cost, latency, quality for sample tasks).

7. Document in `docs/guides/` and runbooks if needed.

## Example Skeleton

```python
from aiw.interfaces.model_provider import ModelProvider

class MyProvider(ModelProvider):
    def name(self):
        return "my-provider"

    def list_models(self):
        return [...]

    # ... implement generate, supports, etc.
```

See `aiw/providers/model/openrouter.py` for a real implementation example (OpenRouter direct API).

## Using OpenRouter

```python
from aiw import get_openrouter_provider, get_model_provider_registry

# Direct
provider = get_openrouter_provider()  # uses OPENROUTER_API_KEY env

# Or via registry
reg = get_model_provider_registry()
provider = reg.get("openrouter")

result = provider.generate("Hello", model="openai/gpt-oss-120b:free")
print(result["text"])
```
Set `OPENROUTER_API_KEY` (already configured in the project's litellm env).
The router and profiles will choose it automatically when allowed.
```

## Rules
- Do not put provider-specific logic in the Agent or Planner.
- All models from this provider become available for AUTO mode and manual selection.
- Support for local models is especially welcome.
