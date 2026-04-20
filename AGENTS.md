# AGENTS.md - Day 13 Observability Lab

## Setup

```bash
# Create venv (required - don't use system Python)
python -m venv .venv
source .venv/bin/activate

# Install dependencies (may need PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 on Python 3.14+)
pip install -r requirements.txt
# If pydantic-core fails on Python 3.14: pip install 'pydantic>=2.10' 'pydantic-core>=2.27'

# Copy env template
cp .env.example .env

# Run app
uvicorn app.main:app --reload
```

## Key Commands

```bash
# Validate logging implementation
python scripts/validate_logs.py

# Load test
python scripts/load_test.py --concurrency 5

# Inject incident scenarios
python scripts/inject_incident.py --scenario rag_slow

# Check metrics
curl http://localhost:8000/metrics
```

## Langfuse v4 Migration (IMPORTANT)

The repo uses **Langfuse v4** SDK. Do NOT use v3 APIs:

| v3 (WRONG) | v4 (CORRECT) |
|------------|--------------|
| `from langfuse.decorators import observe, langfuse_context` | `from langfuse import observe, propagate_attributes, get_client` |
| `langfuse_context.update_current_trace(...)` | `with propagate_attributes(user_id=..., session_id=..., tags=[...]):` |
| `langfuse_context.update_current_observation(...)` | Set `metadata=` inside `propagate_attributes()` |

## Env Vars Required

Must set in `.env`:
```
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://hipaa.cloud.langfuse.com  # or your region
```

## App Entry Points

- `app/main.py` - FastAPI app, requires `load_dotenv()` at top
- `app/agent.py` - LabAgent with `@observe()` decorator
- `app/tracing.py` - Langfuse helpers
- `app/middleware.py` - Correlation ID middleware

## Passing Criteria

- `validate_logs.py` score ≥ 80/100
- ≥10 traces visible in Langfuse dashboard
- Dashboard with 6 panels (use Langfuse built-in or create custom)

## Gotchas

- Python 3.14+ has build issues with pydantic-core - use ABI3 compatibility flag
- Must activate `.venv` before running - system Python lacks dependencies
- Langfuse traces require `tracing_enabled()` to return True (check env vars loaded)
