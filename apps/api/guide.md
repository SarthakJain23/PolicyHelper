# Backend API (`apps/api`) Guide

FastAPI-powered backend managing authentication, role-based access control, PostgreSQL vector indexing, document ingestion, and LangGraph RAG workflows.

---

## Directory Index

| Directory / File                   | Description                                                 | Link                                    |
| :--------------------------------- | :---------------------------------------------------------- | :-------------------------------------- |
| [`app/`](app/)                     | Core application code (models, schemas, routers, services). | [View `app/guide.md`](app/guide.md)     |
| [`alembic/`](alembic/)             | Database migration scripts and environment config.          | [View `alembic/`](alembic/)             |
| [`pyproject.toml`](pyproject.toml) | Python project dependencies and metadata managed via `uv`.  | [View `pyproject.toml`](pyproject.toml) |

---

## Architecture & Conventions

1. **Package Management**: All Python dependencies are managed with `uv`. Run `uv run uvicorn app.main:app --reload` to start development server.
2. **Strategy Patterns**:
   - Storage implementations in `app/services/storage/`
   - LLM provider implementations in `app/services/llm/`
3. **Database**: Async SQLAlchemy 2.0 with PostgreSQL 16+ `pgvector` extension.
