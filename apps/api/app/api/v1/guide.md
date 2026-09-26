# API v1 Router Guide (`apps/api/app/api/v1/`)

Version 1.0 REST and Server-Sent Events (SSE) API endpoint controllers.

---

## Endpoint Modules

| Module                             | Route Prefix          | Description                                                                               |
| :--------------------------------- | :-------------------- | :---------------------------------------------------------------------------------------- |
| [`auth.py`](auth.py)               | `/api/v1/auth`        | Login, password change, current user profile (`/me`).                                     |
| [`departments.py`](departments.py) | `/api/v1/departments` | Full CRUD operations for company departments.                                             |
| [`users.py`](users.py)             | `/api/v1/users`       | Admin user creation with auto-generated temp password, user updates, and password resets. |
| [`roles.py`](roles.py)             | `/api/v1/roles`       | System roles and permission bitmasks listing.                                             |
| [`documents.py`](documents.py)     | `/api/v1/documents`   | Policy document upload, catalog list, download, and deletion.                             |
| [`chat.py`](chat.py)               | `/api/v1/chat`        | Multi-session conversations and real-time SSE token streaming (`/stream`).                |
| [`router.py`](router.py)           | `/api/v1`             | Root router aggregating all v1 sub-routers.                                               |
