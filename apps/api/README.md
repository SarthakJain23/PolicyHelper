# PolicyHelper - Backend API

FastAPI backend service powering PolicyHelper's document ingestion, hybrid RAG retrieval, and AI streaming completions.

---

## 🛠️ Tech Stack & Key Libraries

- **Framework**: FastAPI (Async)
- **Language**: Python 3.11+ (Managed with `uv`)
- **Database & Vectors**: PostgreSQL 16+ with `pgvector` & `tsvector`
- **ORM & Migrations**: SQLAlchemy 2.0 (Async) + Alembic
- **AI / RAG**: LangChain, LangGraph, OpenAI, Anthropic Claude, Google Gemini
- **Auth & Security**: JWT (`python-jose`), `passlib` (Argon2 / bcrypt), `cryptography` (Fernet)
- **Document Parsers**: `pypdf`, `docx2txt`

---

## 🚀 Quickstart

### 1. Environment Setup

Make sure PostgreSQL with `pgvector` is running (e.g., via root `docker compose up -d`).

### 2. Install Dependencies

Using [`uv`](https://docs.astral-sh/uv/) (recommended):

```bash
uv sync
```

Or using standard Python `venv`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. Run Database Migrations

```bash
# Using uv:
uv run alembic upgrade head

# Or with active venv:
alembic upgrade head
```

### 4. Start Development Server

```bash
# Using uv:
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or with active venv:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📚 API Documentation

Once the server is running, navigate to:

- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
