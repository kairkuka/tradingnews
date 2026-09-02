# News Impact Intelligence Bot

Historical news impact and market reaction intelligence system.

Project rule: keep source code, documentation, configuration examples, and small fixtures in git. Keep raw market data, local databases, caches, dependencies, exports, and build artifacts outside git.

Main architecture:

```text
DATA
 ↓
STATISTICS
 ↓
AI
 ↓
PRESENTATION
```

See [docs/technical-spec.md](docs/technical-spec.md) for the full technical specification.

## Phase 1 Scope

Phase 1 establishes the foundation:

- FastAPI app shell
- Pydantic settings
- SQLAlchemy models
- Alembic migrations
- Structured JSON logging
- PostgreSQL and Redis Docker services
- Unit tests for startup, configuration, models, migrations, logging, and timezone validation

No production data providers are implemented in Phase 1.

## Local Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --no-cache-dir -e ".[dev]"
```

Create local environment values only when needed:

```bash
cp .env.example .env
```

Do not commit `.env`.

## Run

```bash
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://localhost:8000/health
```

## Database

Start PostgreSQL and Redis:

```bash
docker compose up -d postgres redis
```

Run migrations:

```bash
alembic upgrade head
```

Run the app stack:

```bash
docker compose up --build app
```

## Checks

```bash
pytest
ruff check .
mypy app
```

## Data Storage

The `data/` folder is ignored by default except for documentation files. Keep heavy files out of git:

- raw market data
- local databases
- parquet/feather/HDF files
- model artifacts
- exports
- logs
