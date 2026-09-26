# Frontend Web Application (`apps/web`) Guide

Next.js 15 App Router web application providing employee chat, semantic search, document ingestion, and admin management.

---

## Directory Index

| Directory / File               | Description                                                           | Link                                              |
| :----------------------------- | :-------------------------------------------------------------------- | :------------------------------------------------ |
| [`app/`](app/)                 | Next.js App Router pages and layout groups (`(auth)`, `(dashboard)`). | [View `app/guide.md`](app/guide.md)               |
| [`components/`](components/)   | Modular, reusable UI components and feature-specific parts.           | [View `components/guide.md`](components/guide.md) |
| [`hooks/`](hooks/)             | Custom TanStack React Query and SSE streaming hooks.                  | [View `hooks/guide.md`](hooks/guide.md)           |
| [`lib/`](lib/)                 | Centralized Axios client, React Query client, and utility helpers.    | [View `lib/guide.md`](lib/guide.md)               |
| [`package.json`](package.json) | Node package dependencies managed via `pnpm`.                         | [View `package.json`](package.json)               |

---

## Conventions & Design Philosophy

1. **Design**: Subtle, classic enterprise aesthetic with high information density, neutral tones, and no gimmicky AI animations.
2. **DRY & Modular**: Components are broken into single-purpose sub-components under 150-200 lines.
3. **Data Fetching**: All mutations and queries use TanStack React Query + Axios. Real-time streaming uses Server-Sent Events (SSE).
