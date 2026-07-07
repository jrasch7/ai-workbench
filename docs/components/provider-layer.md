# Provider Layer

**Responsibility**: The central pillar of AIW. Defines and manages the three types of providers.

**Sub-components**:
- Model Providers
- Execution Providers
- Context Providers
- Provider Registries

**Principles**:
- All providers implement the interfaces in `aiw/interfaces/`
- No core logic depends on a specific provider implementation
- Registration is dynamic

**Why it's a pillar**:
This is what allows AIW to support any model, any execution environment, and any knowledge source without architecture changes.
