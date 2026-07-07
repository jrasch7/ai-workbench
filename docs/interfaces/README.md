# AIW Interfaces

This directory defines the **public contracts** of the AI Workbench platform.

These interfaces are the foundation for making everything pluggable:
- Model Providers
- Execution Providers  
- Context Providers
- Model Router
- Agent Profiles
- Planners (future)

**Rule:** Any implementation must conform to these interfaces. Logic must never be coupled to a concrete provider.

See the main [../ARCHITECTURE.md](../ARCHITECTURE.md) for the overall picture.

## Interfaces

- [Model Provider](model-provider.md)
- [Execution Provider](execution-provider.md)
- [Context Provider](context-provider.md)
- [Model Router](model-router.md)
- [Agent Profile](agent-profile.md)
