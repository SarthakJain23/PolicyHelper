# Schemas Guide (`apps/api/app/schemas/`)

Pydantic V2 models for validating API requests and serializing responses.

---

## File Index

| File                             | Description                                                                       |
| :------------------------------- | :-------------------------------------------------------------------------------- |
| [`auth.py`](auth.py)             | Login, token issuance, password reset, and user profile schemas.                  |
| [`department.py`](department.py) | Department creation, update, and serialized output schemas.                       |
| [`role.py`](role.py)             | Role serialization with permissions bitmask/flags.                                |
| [`user.py`](user.py)             | User creation with auto-generated temp password, user updates, and profile views. |
| [`document.py`](document.py)     | Document upload metadata and document catalog views with status.                  |
| [`chat.py`](chat.py)             | Multi-session chat models, message streams, turn histories, and citation cards.   |
