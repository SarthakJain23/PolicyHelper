# Models Guide (`apps/api/app/models/`)

Database entities and SQLAlchemy 2.0 ORM mappings for PostgreSQL.

---

## Model Index

| Model                                           | File                             | Description                                                                            |
| :---------------------------------------------- | :------------------------------- | :------------------------------------------------------------------------------------- |
| `Department`                                    | [`department.py`](department.py) | Company organizational units (Engineering, HR, etc.) with CRUD operations.             |
| `Role`                                          | [`role.py`](role.py)             | Dynamic user roles (`SUPER_ADMIN`, `HR_ADMIN`, `MANAGER`, `EMPLOYEE`).                 |
| `User` & `user_roles`                           | [`user.py`](user.py)             | Employee account entity with Many-to-Many role mapping and force password reset state. |
| `Document`                                      | [`document.py`](document.py)     | Metadata for uploaded policies (PDF, Word, Markdown) with RBAC permissions.            |
| `DocumentChunk`                                 | [`chunk.py`](chunk.py)           | Text chunks with `pgvector` vector embedding and `tsvector` full-text search index.    |
| `ChatSession`, `ChatMessage`, `MessageCitation` | [`chat.py`](chat.py)             | Multi-session chat conversations, turn-by-turn messages, and source citations.         |
| `AuditLog`                                      | [`audit.py`](audit.py)           | System security and compliance activity log.                                           |
