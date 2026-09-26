# Core Module Guide (`apps/api/app/core/`)

Provides application-wide utilities, configuration, async database engine, and security handlers.

---

## File Index

| File                         | Description                                                                              |
| :--------------------------- | :--------------------------------------------------------------------------------------- |
| [`config.py`](config.py)     | Pydantic Settings loading environment variables (`.env`) for DB, LLMs, Storage, and JWT. |
| [`database.py`](database.py) | SQLAlchemy async engine, session factory, and declarative `Base` class.                  |
| [`security.py`](security.py) | JWT creation/verification, password hashing, and dependency injection guards.            |
