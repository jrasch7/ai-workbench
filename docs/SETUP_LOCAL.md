# Setup Local Development for **ai-workbench**

This guide contains the minimal steps required to clone the repository on a new machine and get the full stack running locally.

## 1. Clone the repository

```bash
git clone https://github.com/your-org/ai-workbench.git
cd ai-workbench
```

## 2. Create environment file

Copy the example file and fill in your own keys:

```bash
cp .env.example .env
# Edit .env and replace the placeholder values with real keys
```

> **Important**: do **not** commit the real ``.env`` file.

## 3. Build and start containers

```bash
# Build Docker images (if not already built)
docker compose build

# Start the stack in the background
docker compose up -d
```

The stack consists of:
- **OpenHands GUI** (exposes UI on ``http://host.docker.internal:4000``)
- **LiteLLM** (local LLM proxy, ports ``8011`` and ``8012`` as defined in `work_hosts`)
- **OpenRouter** (accessed via LiteLLM)
- **Sandbox Docker** (executes generated code)
- **Workspace volume** (where generated files are stored)

## 4. Verify the services

```bash
# List running containers
docker ps
```
You should see containers for `openhands`, `litellm`, and the sandbox.

## 5. Open the UI

Navigate to **http://host.docker.internal:4000** in your browser.

## 6. Model configuration

OpenHands expects the model identifier **openai/dev-coder**. LiteLLM must expose this model under the alias **dev-coder**.

## 7. OpenRouter integration (optional)

LiteLLM forwards requests to OpenRouter using an OpenAI‑compatible ``api_base`` URL (e.g. ``https://api.openrouter.ai/v1``). Direct use of the ``openrouter/...`` adapter is **not** supported.

### Known limitations
- Free OpenRouter models are unstable and may return HTTP 429 errors.
- For production workloads you should configure fallback providers or use a paid, reliable model.

## 8. End‑to‑end flow (validated)

1. **OpenHands GUI** → 2. **LiteLLM (local)** → 3. **OpenRouter** → 4. **Sandbox Docker** → 5. Generated file placed in the workspace.

---

**Next steps**: See `docs/TROUBLESHOOTING_LITELLM_OPENROUTER.md` for common issues.
