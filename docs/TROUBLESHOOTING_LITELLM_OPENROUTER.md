# Troubleshooting LiteLLM & OpenRouter Integration

This document lists common issues when using the local LiteLLM proxy together with OpenRouter and how to resolve them.

## 1. LiteLLM does not expose the `dev-coder` alias

- **Symptom**: OpenHands UI shows *Model not found* or returns a 404.
- **Fix**:
  1. Open `config/litellm.yaml` (or the environment variable `LITELLM_ALIAS`).
  2. Ensure the `model_list` contains an entry:
     ```yaml
     - model_name: dev-coder
       litellm_model_name: openai/dev-coder
     ```
  3. Restart the LiteLLM container: `docker compose restart litellm`.

## 2. OpenRouter returns HTTP 429 Too Many Requests

- **Cause**: Free tier models on OpenRouter are rate‑limited and may be throttled.
- **Work‑arounds**:
  - Reduce request frequency (e.g., add a short delay between calls).
  - Switch to a paid model or another provider in `LITELLM_MODEL`.
  - Configure a fallback provider in `config/litellm.yaml`:
    ```yaml
    fallback_models:
      - model_name: openai/gpt-4o-mini
        api_key: $OPENAI_API_KEY
    ```

## 3. OpenRouter integration fails with *adapter* error

- **Symptom**: LiteLLM logs show `adapter openrouter/... not found`.
- **Explanation**: LiteLLM expects an OpenAI‑compatible `api_base` URL, not the dedicated `openrouter/...` adapter.
- **Fix**: Set the environment variables:
  ```bash
  LITELLM_OPENROUTER_API_BASE=https://api.openrouter.ai/v1
  LITELLM_OPENROUTER_API_KEY=$OPENROUTER_API_KEY
  ```
  and ensure `api_base` is used in the request configuration.

## 4. Sandbox Docker cannot write files to the workspace

- **Symptom**: Generated code runs but no file appears in the mounted volume.
- **Fix**:
  1. Verify the volume mount in `docker-compose.yml` (e.g., `- ./workspace:/workspace`).
  2. Ensure the sandbox container has write permissions (`chmod -R 777 workspace`).
  3. Check container logs: `docker logs sandbox` for permission errors.

## 5. Model identifier mismatch

- **Symptom**: OpenHands sends `openai/dev-coder` but LiteLLM expects `dev-coder`.
- **Fix**: In `.env.example` set:
  ```
  OPENHANDS_MODEL=openai/dev-coder
  LITELLM_ALIAS=dev-coder
  ```
  LiteLLM will map the alias correctly.

## 6. General connectivity issues

- Verify that the host can reach `api.openrouter.ai` (run `curl -I https://api.openrouter.ai/v1`).
- Ensure no firewall blocks outbound traffic from the LiteLLM container.
- Check that the Docker network allows communication between `openhands` and `litellm` containers (`docker network ls`).

## 7. Restart the stack

Sometimes stale containers cause unexpected behavior. A clean restart often resolves issues:
```bash
docker compose down
docker compose up -d --build
```

---

If problems persist, consult the OpenHands and LiteLLM issue trackers or open a new issue with logs from the relevant containers.
