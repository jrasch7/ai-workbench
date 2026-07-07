# Core

**Responsibility**: Shared primitives, schemas, security basics, configuration, and utilities that do not belong to any specific provider or layer.

**Key Contents**:
- Common data models (Task, Run, Decision, Artifact)
- Security primitives (path validation, secret masking)
- Workspace resolution basics
- Logging and error contracts

**Dependencies**: None (lowest layer)

**Consumers**: All other components
