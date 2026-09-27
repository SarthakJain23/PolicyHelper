# PolicyHelper - Web Client

Modern web application for PolicyHelper built with Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, and TanStack React Query.

---

## 🛠️ Tech Stack

- **Framework**: Next.js 15 (App Router) + React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4 + `shadcn/ui` + Lucide Icons
- **Data Fetching**: TanStack React Query (`@tanstack/react-query`) + Axios
- **Streaming**: Server-Sent Events (SSE) via custom `useChatStream` hook
- **Markdown & Citations**: `react-markdown` + `remark-gfm`

---

## 🚀 Getting Started

### 1. Install Dependencies

Using `pnpm`:

```bash
pnpm install
```

### 2. Environment Configuration

Optionally configure `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 3. Run Development Server

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) to access the application.

---

## 📂 Key Features & Routes

- **`/chat`**: Interactive AI policy assistant with multi-session history, SSE streaming responses, and clickable citation drawer.
- **`/documents`**: Document management & upload modal with department scoping and indexing progress.
- **`/departments`**: Department CRUD and policy segregation.
- **`/users`**: Team member invitations and role management.
- **`/logs`**: Comprehensive system audit log viewer.
- **`/settings`**: Dynamic LLM provider configuration (OpenAI, Anthropic Claude, Google Gemini).
