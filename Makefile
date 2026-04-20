.PHONY: install run stop test load flush validate

install:
	uv sync

run:
	set -a && . ./.env && set +a && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

stop:
	pkill -f "uvicorn app.main:app" || true

test:
	uv run pytest tests/

load:
	uv run python scripts/load_test.py

flush:
	set -a && . ./.env && set +a && uv run python -c "from langfuse import Langfuse; Langfuse().flush(); print('flushed')"

validate:
	uv run python scripts/validate_logs.py
