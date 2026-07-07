# Agent Runtime

**Responsibility**: The main execution engine that orchestrates a task using a chosen profile.

**Flow**:
1. Receive task + profile
2. Use Model Router (if AUTO)
3. Invoke Planner
4. Execute steps via Execution layer
5. Enrich with Context
6. Apply Policy/Isolation at every decision point
7. Persist artifacts and decisions

**Must remain independent** of specific Model or Execution providers.
