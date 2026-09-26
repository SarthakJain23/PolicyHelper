# Apps Directory Guide

This directory contains the decoupled frontend and backend applications for **PolicyHelper**.

---

## Subdirectories

| Directory      | Type                 | Stack                                                                        | Description                                                                                          | Guide Link                               |
| :------------- | :------------------- | :--------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------- | :--------------------------------------- |
| [`api/`](api/) | Backend Service      | FastAPI, Python 3.11+, uv, LangChain, LangGraph, pgvector                    | REST API, SSE streaming, RAG pipelines, authentication, and document storage strategies.             | [View `apps/api/guide.md`](api/guide.md) |
| [`web/`](web/) | Frontend Application | Next.js 15, TypeScript, pnpm, Tailwind CSS, shadcn/ui, TanStack Query, Axios | Single-page client interface for employee policy chat, search, document upload, and user management. | [View `apps/web/guide.md`](web/guide.md) |
