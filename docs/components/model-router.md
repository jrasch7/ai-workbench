# Model Router

**Responsibility**: Intelligent selection of which model/provider to use for a given task.

**Key Features**:
- AUTO mode
- Constraint-based routing (cost, latency, quality)
- Fallback support
- Decision logging for observability

**Inputs**: Task, AgentProfile, constraints
**Outputs**: Chosen provider + model + parameters + rationale
