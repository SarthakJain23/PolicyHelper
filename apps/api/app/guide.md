# Backend Core Application Guide (`apps/api/app/`)

This directory contains the FastAPI backend code structure.

---

## Directory Index

| Directory / File         | Description                                                                        | Link                                          |
| :----------------------- | :--------------------------------------------------------------------------------- | :-------------------------------------------- |
| [`core/`](core/)         | Global configuration, security/JWT utilities, and async database session.          | [View `core/guide.md`](core/guide.md)         |
| [`models/`](models/)     | SQLAlchemy 2.0 database models with `pgvector` mappings.                           | [View `models/guide.md`](models/guide.md)     |
| [`schemas/`](schemas/)   | Pydantic request and response validation schemas.                                  | [View `schemas/guide.md`](schemas/guide.md)   |
| [`api/`](api/)           | REST and SSE streaming API routers organized by version.                           | [View `api/guide.md`](api/guide.md)           |
| [`services/`](services/) | Strategy patterns (Storage, LLM), document ingestion, and LangGraph RAG workflows. | [View `services/guide.md`](services/guide.md) |
| [`main.py`](main.py)     | Application entrypoint with CORS, error handlers, and lifespan manager.            | [View `main.py`](main.py)                     |
