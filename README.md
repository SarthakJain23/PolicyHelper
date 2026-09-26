# PolicyHelper

An internal, self-hosted AI chatbot and policy search assistant for company employees and HR/Admin teams.

---

## 📚 Documentation & Architecture

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Comprehensive architectural design, database schema, design patterns, and tech stack details.
- **[PLAN.md](PLAN.md)**: Step-by-step 9-phase implementation roadmap.
- **[guide.md](guide.md)**: Workspace directory navigation and component guide.

---

## 🛠️ Tech Stack Overview

- **Frontend**: Next.js 15 (App Router), TypeScript, pnpm, Tailwind CSS, shadcn/ui, TanStack React Query, Axios.
- **Backend**: FastAPI, Python 3.11+, uv, SQLAlchemy 2.0 (Async), Alembic, LangChain, LangGraph.
- **Database**: PostgreSQL 16+ with `pgvector` (Vectors, Full-text search, and relational data).
- **Storage**: Strategy pattern supporting Local Filesystem and S3 / MinIO.
- **LLMs**: Strategy pattern supporting OpenAI, Anthropic Claude, and Google Gemini.
