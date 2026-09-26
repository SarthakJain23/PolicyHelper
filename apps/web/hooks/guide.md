# Frontend Hooks Guide (`apps/web/hooks/`)

Custom React hooks encapsulating TanStack Query state, data mutations, and SSE token streaming.

---

## Hook Index

| Hook              | File                                       | Description                                                                                            |
| :---------------- | :----------------------------------------- | :----------------------------------------------------------------------------------------------------- |
| `useAuth`         | [`useAuth.ts`](useAuth.ts)                 | Login, token persistence, mandatory first-login password change, and current user queries.             |
| `useDepartments`  | [`useDepartments.ts`](useDepartments.ts)   | List, create, update, and deactivate company departments.                                              |
| `useUsers`        | [`useUsers.ts`](useUsers.ts)               | List users, invite users with generated temp passwords, assign roles/departments.                      |
| `useDocuments`    | [`useDocuments.ts`](useDocuments.ts)       | Document catalog, background polling for indexing status, upload, and deletion.                        |
| `useChatSessions` | [`useChatSessions.ts`](useChatSessions.ts) | Conversation sessions management (list, create, rename, pin, archive, delete).                         |
| `useChatStream`   | [`useChatStream.ts`](useChatStream.ts)     | Real-time Server-Sent Events (SSE) streaming hook reading citations, tokens, and auto-titling updates. |
