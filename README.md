# 🛡️ PolicyHelper

> **Self-hosted, privacy-first AI Policy & Knowledge Assistant for modern organizations.**  
> Empower your workforce with instant, accurate, and fully cited answers from internal handbooks, IT guidelines, compliance manuals, and departmental procedures.

---

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js 15](https://img.shields.io/badge/Frontend-Next.js%2015-000000?style=flat&logo=next.js&logoColor=white)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%20%2B%20pgvector-4169E1?style=flat&logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![LangGraph](https://img.shields.io/badge/AI%20Orchestration-LangChain%20%2F%20LangGraph-1C3C3C?style=flat&logo=langchain&logoColor=white)](https://www.langchain.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-v4-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌟 Why PolicyHelper?

Company knowledge is often scattered across dense PDF handbooks, Google Docs, intranet wikis, and internal drive folders. Employees waste hours searching or submitting repetitive HR/IT support tickets, while administrators struggle to keep documentation accessible and up to date.

**PolicyHelper** bridges this gap with an enterprise-grade, self-hosted AI chatbot powered by **Hybrid RAG (Retrieval-Augmented Generation)**. It understands complex company rules, scopes permissions by department, and guarantees that every answer comes with verifiable, clickable citations.

### 👥 Key Benefits

- ⚡ **For Employees**: Get immediate, 24/7 answers to questions about leave policies, travel reimbursements, medical benefits, and IT security without waiting on ticket queues.
- 🎯 **For HR & People Teams**: Automate up to 80% of repetitive policy inquiries while maintaining full control over document versioning and departmental access.
- 🔒 **For IT, Security & Compliance**: 100% self-hosted on your own infrastructure. Your private company documents and vector embeddings never leave your database. Complete audit trails record all queries and administrative activities.

---

## ✨ Features

### 🧠 Agentic RAG & Hybrid Retrieval

- **Hybrid Search**: Combines dense semantic vector search (`pgvector`) with sparse lexical BM25 full-text keyword search (`tsvector`) for precision and recall.
- **LangGraph Workflows**: Intelligent query rewriting, dynamic retrieval routing, and cross-encoder reranking.
- **Real-Time Token Streaming**: Server-Sent Events (SSE) deliver sub-second token streaming directly to the chat interface.
- **Strict Verifiable Citations**: Answers include exact source document names, page numbers, section headers, and direct text excerpts to eliminate hallucinations.

### 📄 Smart Document Ingestion Pipeline

- **Multi-Format Support**: Ingests `.pdf`, `.docx`, `.md`, and `.txt` documents.
- **Structure-Aware Chunking**: Hierarchical and header-aware chunkers preserve section context (e.g., _Section 4.2 > Parental Leave > Eligibility_) rather than breaking mid-sentence.
- **Pluggable Storage**: Strategy pattern supporting **Local Filesystem** or **Cloud Object Storage (AWS S3 / MinIO / Cloudflare R2)**.

### 🤖 Multi-LLM Provider Flexibility

- Dynamically configure model providers per organization from the Admin UI:
  - **OpenAI** (`gpt-4o`, `gpt-4o-mini`, `text-embedding-3-small`, etc.)
  - **Anthropic** (`claude-3-5-sonnet`, `claude-3-haiku`, etc.)
  - **Google Gemini** (`gemini-1.5-pro`, `gemini-1.5-flash`, etc.)
- API keys are encrypted at rest using Fernet encryption (`app/core/crypto.py`).

### 🛡️ Granular RBAC & Department Scoping

- **Hierarchical Roles**: `Super Admin`, `HR Admin`, `Manager`, and `Employee`.
- **Department-Scoped Policies**: Assign documents to specific departments (e.g., Engineering, HR, Finance, Legal, General). Queries automatically respect the employee's department and role clearance.
- **Security First**: JWT authentication with HTTP-only cookies, password hashing with Argon2/bcrypt, and mandatory first-login password resets.

### 💬 Modern Chat Experience

- **Multi-Session History**: Persistent conversation threads organized by session.
- **Automatic AI Title Generation**: Automatically summarizes the topic into a concise chat title after early conversation turns.
- **Interactive Citation Drawer**: Click citations to view exact matched excerpts, page numbers, and similarity scores.
- **Responsive Theme Support**: Sleek, accessible UI built with **shadcn/ui**, **Tailwind CSS**, and dark/light modes.

### 📊 Enterprise Audit Logging & Analytics

- Track all user queries, model responses, document uploads, department modifications, and authentication events in a searchable compliance log.

---

## 🏗️ Architecture Overview

```mermaid
graph TD
    subgraph Client ["Frontend (Next.js 15 + TypeScript)"]
        ChatUI["Employee Chat & Citations Portal"]
        AdminUI["Admin & HR Management Console"]
    end

    subgraph API ["Backend API (FastAPI + Async SQLAlchemy)"]
        AuthSvc["Auth & RBAC (JWT, Argon2)"]
        DocSvc["Document Ingestion & Chunking"]
        ChatSvc["Chat & SSE Streaming API"]
        AdminSvc["Department, User & Config Management"]
    end

    subgraph RAGEngine ["AI & Orchestration (LangChain + LangGraph)"]
        QueryRewriter["Query Reformulation"]
        HybridRetriever["Hybrid Retrieval (Vector + Keyword)"]
        Reranker["Context Reranking"]
        LLMOrchestrator["Streaming LLM Generator"]
    end

    subgraph Storage ["Storage Layer"]
        LocalFS["Local Storage (Volume)"]
        S3Storage["AWS S3 / MinIO Object Storage"]
    end

    subgraph Database ["PostgreSQL 16+ (All-in-One Engine)"]
        PG_Relational[("Relational Data (Users, Orgs, Sessions, Logs)")]
        PG_Vector[("pgvector (Embeddings & Semantic Search)")]
        PG_FTS[("tsvector (BM25 Full-Text Keyword Search)")]
    end

    subgraph LLMs ["Supported LLM Providers"]
        OpenAI["OpenAI (GPT-4o / Embeddings)"]
        Anthropic["Anthropic (Claude 3.5 Sonnet)"]
        Gemini["Google Gemini (1.5 Pro / Flash)"]
    end

    Client -->|HTTP / REST| API
    Client -->|SSE Stream| ChatSvc

    DocSvc --> Storage
    DocSvc --> PG_Relational
    DocSvc --> PG_Vector

    ChatSvc --> RAGEngine
    RAGEngine --> PG_Vector
    RAGEngine --> PG_FTS
    RAGEngine --> LLMs

    API --> PG_Relational
```

---

## 🛠️ Technology Stack

| Domain                   | Technology                                                                                         | Purpose                                                              |
| :----------------------- | :------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------- |
| **Frontend Framework**   | [Next.js 15 (App Router)](https://nextjs.org/)                                                     | Modern React 19 framework with Server Components & dynamic routing   |
| **Styling & Components** | [Tailwind CSS v4](https://tailwindcss.com/) + [shadcn/ui](https://ui.shadcn.com/)                  | Accessible, enterprise-ready UI design system                        |
| **Client State & Data**  | [TanStack React Query](https://tanstack.com/query) + [Axios](https://axios-http.com/)              | Declarative data fetching, caching, and optimistic UI updates        |
| **Backend Framework**    | [FastAPI](https://fastapi.tiangolo.com/) + [Python 3.11+](https://www.python.org/)                 | High-performance asynchronous REST API with automatic OpenAPI docs   |
| **Package Management**   | [uv](https://github.com/astral-sh/uv) (Python) & [pnpm](https://pnpm.io/) (Node.js)                | Lightning-fast dependency management and monorepo tooling            |
| **AI Orchestration**     | [LangChain](https://www.langchain.com/) + [LangGraph](https://langchain-ai.github.io/langgraph/)   | Agentic RAG workflows, query rewriting, and token streaming          |
| **Database & Search**    | [PostgreSQL 16](https://www.postgresql.org/) + [pgvector](https://github.com/pgvector/pgvector)    | Relational storage, dense vector search, and BM25 full-text indexing |
| **ORM & Migrations**     | [SQLAlchemy 2.0 (Async)](https://www.sqlalchemy.org/) + [Alembic](https://alembic.sqlalchemy.org/) | Async database access and schema migrations                          |
| **Security & Auth**      | JWT (`python-jose`) + `passlib` (Argon2 / bcrypt)                                                  | Secure authentication with role-based authorization                  |

---

## 🚀 Getting Started

Follow these steps to set up PolicyHelper locally on your development machine.

### 📋 Prerequisites

Ensure you have the following installed:

- **Docker & Docker Compose** (for running PostgreSQL with `pgvector`)
- **Python 3.11+** (or [`uv`](https://docs.astral.sh/uv/) for fast Python package management)
- **Node.js 20+** and **pnpm** (`npm install -g pnpm`)

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-org/PolicyHelper.git
cd PolicyHelper
```

---

### Step 2: Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Review `.env` and adjust settings if necessary. Key default values:

```env
# Server
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:3000

# Security (Replace with a random 32+ character string)
JWT_SECRET_KEY=change_this_to_a_very_secure_random_secret_key_in_production

# Initial Super Admin (Seeded on first run)
FIRST_SUPERUSER_EMAIL=admin@company.internal
FIRST_SUPERUSER_PASSWORD=AdminInitialPass123!
FIRST_SUPERUSER_NAME="System Administrator"

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432
POSTGRES_DB=policyhelper_db
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/policyhelper_db

# Document Storage Strategy ("local" or "s3")
STORAGE_TYPE=local
LOCAL_STORAGE_DIR=./data/policies
```

---

### Step 3: Start the PostgreSQL Database

Start the PostgreSQL database equipped with `pgvector`:

```bash
docker compose up -d
```

Verify that the database is healthy:

```bash
docker compose ps
```

---

### Step 4: Setup and Run the Backend API

1. Navigate to the API folder:

   ```bash
   cd apps/api
   ```

2. Install Python dependencies using `uv` (recommended) or standard `pip`:

   ```bash
   # Using uv:
   uv sync

   # Or using standard venv + pip:
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

3. Run database migrations:

   ```bash
   # Using uv:
   uv run alembic upgrade head

   # Or using active virtual environment:
   alembic upgrade head
   ```

4. Start the FastAPI server:

   ```bash
   # Using uv:
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # Or using active virtual environment:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

> 💡 **Auto-Seeding**: Upon startup, PolicyHelper automatically seeds the default organization, departments (HR, Engineering, Finance, Legal, General), default roles, the initial Super Admin account, and test users.

Interactive API documentation will be available at:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### Step 5: Setup and Run the Web Frontend

1. Open a new terminal tab and navigate to the web directory:

   ```bash
   cd apps/web
   ```

2. Install frontend dependencies:

   ```bash
   pnpm install
   ```

3. Start the Next.js development server:

   ```bash
   pnpm dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🔑 Default Seeded Accounts

The initial database seed provisions the following ready-to-use accounts:

| Email                            | Password               | Role            | Department  | Purpose                                                  |
| :------------------------------- | :--------------------- | :-------------- | :---------- | :------------------------------------------------------- |
| `admin@company.internal`         | `AdminInitialPass123!` | **Super Admin** | General     | Full system configuration, LLM setup & user management   |
| `hr.admin@company.internal`      | `Password123!`         | **HR Admin**    | HR          | Document uploads, department policies & user invitations |
| `eng.manager@company.internal`   | `Password123!`         | **Manager**     | Engineering | Team-level policy search & manager queries               |
| `sales.manager@company.internal` | `Password123!`         | **Manager**     | Sales       | Team-level policy search & manager queries               |
| `john.doe@company.internal`      | `Password123!`         | **Employee**    | Engineering | Standard employee policy chat & search                   |
| `jane.smith@company.internal`    | `Password123!`         | **Employee**    | Finance     | Standard employee policy chat & search                   |
| `alice.wong@company.internal`    | `Password123!`         | **Employee**    | Legal       | Standard employee policy chat & search                   |

---

## 📖 Admin & User Walkthrough

### 1. Connect Your LLM Provider

1. Log in as `admin@company.internal`.
2. Navigate to **Settings** (`/settings`).
3. Select your preferred provider (**OpenAI**, **Anthropic**, or **Google Gemini**).
4. Enter your API key and select your preferred Chat model (e.g. `gpt-4o`) and Embedding model (e.g. `text-embedding-3-small`).
5. Click **Save Configuration**. The API key is securely encrypted before storage.

### 2. Ingest Policy Documents

1. Navigate to **Documents** (`/documents`).
2. Click **Upload Document**.
3. Select a PDF, DOCX, Markdown, or TXT file (e.g., _Employee Handbook_, _Travel & Expense Policy_, _Remote Work Guidelines_).
4. Assign the document to a department (or select **General / Company-Wide** for organization-wide access).
5. The background pipeline extracts text, generates hierarchical chunks, and indexes embeddings in `pgvector`.

### 3. Ask Questions & Search

1. Navigate to **Chat** (`/chat`).
2. Start a new session and ask policy questions in natural language:
   - _"How many days of paid parental leave do full-time employees receive?"_
   - _"What is the maximum daily meal allowance during business travel?"_
   - _"What is the procedure for requesting a new software license?"_
3. Watch the answer stream in real time. Click on any citation badge to view the exact page and section from which the answer was retrieved.

---

## 📁 Project Structure

```
PolicyHelper/
├── apps/
│   ├── api/                     # FastAPI Backend Application
│   │   ├── alembic/             # Database migrations
│   │   ├── app/
│   │   │   ├── api/v1/          # REST & SSE API endpoints
│   │   │   ├── core/            # Config, DB connection, security & seeding
│   │   │   ├── models/          # SQLAlchemy ORM models
│   │   │   ├── schemas/         # Pydantic validation schemas
│   │   │   └── services/        # Business logic & services
│   │   │       ├── chat/        # Session management & title generation
│   │   │       ├── ingestion/   # Document parsers & header-aware splitters
│   │   │       ├── llm/         # LLM provider strategies (OpenAI, Anthropic, Gemini)
│   │   │       ├── rag/         # LangGraph hybrid retrieval & rerank pipeline
│   │   │       └── storage/     # Storage strategies (Local, S3/MinIO)
│   │   ├── pyproject.toml       # Python project configuration & dependencies
│   │   └── README.md
│   │
│   └── web/                     # Next.js 15 Frontend Application
│       ├── app/
│       │   ├── (auth)/          # Login & password change pages
│       │   └── (dashboard)/     # Chat, Documents, Users, Departments, Logs, Settings
│       ├── components/          # Reusable UI components & dialogs
│       ├── hooks/               # Custom React hooks (TanStack Query, SSE stream)
│       ├── lib/                 # API client, query provider, utilities
│       ├── package.json         # Node.js dependencies & scripts
│       └── README.md
│
├── data/
│   └── policies/                # Default local storage directory for uploaded files
├── ARCHITECTURE.md              # Detailed technical design & schema documentation
├── docker-compose.yml           # PostgreSQL 16 with pgvector service
├── .env.example                 # Environment variables template
└── README.md                    # Project README
```

---

## 🔧 Environment Variables Reference

| Variable                       | Default                 | Description                                                         |
| :----------------------------- | :---------------------- | :------------------------------------------------------------------ |
| `ENVIRONMENT`                  | `development`           | Deployment environment (`development` or `production`)              |
| `LOG_LEVEL`                    | `INFO`                  | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)                 |
| `API_HOST`                     | `0.0.0.0`               | API bind address                                                    |
| `API_PORT`                     | `8000`                  | API server port                                                     |
| `FRONTEND_URL`                 | `http://localhost:3000` | Allowed CORS origin for web client                                  |
| `JWT_SECRET_KEY`               | _(Required)_            | Secret key for signing authentication tokens                        |
| `JWT_ALGORITHM`                | `HS256`                 | JWT signing algorithm                                               |
| `ACCESS_TOKEN_EXPIRE_MINUTES`  | `60`                    | Lifespan of JWT access tokens                                       |
| `REFRESH_TOKEN_EXPIRE_DAYS`    | `7`                     | Lifespan of refresh tokens                                          |
| `DATABASE_URL`                 | _(Asyncpg URL)_         | Async connection string for PostgreSQL                              |
| `STORAGE_TYPE`                 | `local`                 | Document storage provider: `local` or `s3`                          |
| `LOCAL_STORAGE_DIR`            | `./data/policies`       | Directory path for local file storage                               |
| `S3_ENDPOINT_URL`              | `http://localhost:9000` | S3 or MinIO API endpoint (if `STORAGE_TYPE=s3`)                     |
| `S3_BUCKET_NAME`               | `policies`              | Target S3 bucket name                                               |
| `CHUNK_SIZE`                   | `800`                   | Maximum character length per text chunk                             |
| `CHUNK_OVERLAP`                | `120`                   | Overlap characters between consecutive chunks                       |
| `RETRIEVAL_TOP_K`              | `15`                    | Number of candidate chunks retrieved across vector & keyword search |
| `RERANK_TOP_K`                 | `4`                     | Top candidate chunks provided to LLM context after reranking        |
| `AUTO_TITLE_MESSAGE_THRESHOLD` | `2`                     | Number of chat turns before automatic title generation runs         |

---

## 📚 Further Documentation

For deep technical insights into database schemas, chunking algorithms, LangGraph nodes, and design patterns, explore:

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — In-depth architectural specification and database entity diagrams.
- **[apps/api/guide.md](apps/api/guide.md)** — Backend architecture and service design guide.
- **[apps/web/guide.md](apps/web/guide.md)** — Frontend architecture, component hierarchy, and state management guide.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
