# PolicyHelper - Workspace Guide

Welcome to **PolicyHelper**, an internal AI chatbot and company policy search assistant.

---

## 1. Directory Overview

| Directory / File                           | Description                                                                              | Link                                            |
| :----------------------------------------- | :--------------------------------------------------------------------------------------- | :---------------------------------------------- |
| [`apps/`](apps/)                           | Houses the frontend and backend micro-applications.                                      | [View `apps/guide.md`](apps/guide.md)           |
| [`ARCHITECTURE.md`](ARCHITECTURE.md)       | Detailed architecture, system design, schema, and workflow specifications.               | [View `ARCHITECTURE.md`](ARCHITECTURE.md)       |
| [`PLAN.md`](PLAN.md)                       | Step-by-step 9-phase implementation roadmap and task breakdown.                          | [View `PLAN.md`](PLAN.md)                       |
| [`docker-compose.yml`](docker-compose.yml) | Local multi-container development infrastructure (PostgreSQL with `pgvector`, MinIO S3). | [View `docker-compose.yml`](docker-compose.yml) |
| [`README.md`](README.md)                   | Project quickstart, prerequisites, and setup instructions.                               | [View `README.md`](README.md)                   |

---

## 2. Applications Structure

- **Frontend (`apps/web`)**: Next.js 15 App Router application built with TypeScript, Tailwind CSS, shadcn/ui, TanStack React Query, and Axios.
- **Backend (`apps/api`)**: FastAPI async API built with Python 3.11+, LangChain, LangGraph, pgvector, and managed with `uv`.

---

## 3. Documentation Guidelines

Every subdirectory across `apps/web` and `apps/api` contains a dedicated `guide.md` file explaining:

1. **Purpose**: What the directory contains and its responsibility.
2. **File Index**: Summary of every file with relative links.
3. **Subfolder Index**: Links to child directories and their guides.
4. **Conventions**: Specific rules, architectural patterns, or constraints applicable to that folder.
