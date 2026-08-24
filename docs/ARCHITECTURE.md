# 🏗 ARCHITECTURE — Task Manager API deep dive

> Why the code is arranged the way it is, and the rules that keep it that way.

## The Dependency Rule

> Source code dependencies **always point inward**. Nothing in an inner circle can know about something in an outer circle.

```
┌──────────────────────────────┐
│ api/          (HTTP layer)   │  ← knows everything below
├──────────────────────────────┤
│ application/  (use cases)    │  ← knows domain only
├──────────────────────────────┤
│ domain/       (entities)     │  ← pure Python, zero imports from app
├──────────────────────────────┤
│ infrastructure/ (adapters)   │  ← implements domain contracts
└──────────────────────────────┘
```

**Consequence:** `app/domain/entities.py` imports nothing from `app/` — run it on any machine, in any framework, and it works. That's what makes the domain testable in 2.5 seconds.

## The Layers

### `domain/` — the heart (pure Python)
- `entities.py` — `User`, `Task` dataclasses with behavior (`mark_completed`, `belongs_to`)
- `repositories.py` — abstract contracts (`TaskRepository`, `UserRepository`). The domain *defines* persistence; it doesn't care who implements it.

### `application/` — the use cases
- `services.py` — `UserService`, `TaskService`. Orchestrates entities + repositories. Exceptions here are business exceptions (`TaskNotFoundError`).

### `infrastructure/` — the adapters
- `database.py` — engine/session factory (SQLAlchemy)
- `orm.py` — the table mappings (`UserORM`, `TaskORM`) — the *only* place SQLAlchemy annotations live
- `repositories.py` — implementations of the domain contracts
- `migrations/` — Alembic: schema as versioned, auditable code

### `api/` — the edge
- `routes_*.py` — HTTP verbs, status codes, error translation (business error → 404/409/401)
- `schemas.py` — Pydantic contracts: what enters, what leaves
- `dependencies.py` — `get_current_user` (JWT decode), service factories (DI)

## Dependency Injection in practice

The API layer *wires* services to SQLAlchemy repositories:

```python
def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(SqlAlchemyTaskRepository(db))
```

In tests, we swap in `InMemoryTasks` — no database needed. Same `TaskService`, different backend. That is the payoff of depending on abstractions.

## Security posture (DevSecOps)

- Passwords: `bcrypt` hash only — plaintext never stored, no reversible encoding
- Tokens: JWT with expiry + issued-at; the only claim is `sub` (email)
- Authorization: every task query filters by `owner_id` — cross-user access is structurally impossible, not just discouraged
- Container: non-root user, minimal slim image
- CI: `bandit` scans every push

## Data Engineering posture

- Migrations are **versioned and idempotent**: `alembic upgrade head` is safe to run repeatedly (Alembic tracks applied revisions)
- Config is **environment-driven** (12-factor): same artifact, any environment
- Logs are **structured JSON** with request IDs → greppable, traceable, dashboard-ready
- The schema is deliberately small but migration-ready: adding a column = 1 revision file + 1 test

## Extension examples

| Change | Files touched |
|---|---|
| Add `priority` field | `orm.py` + migration + `schemas.py` + maybe `domain` |
| Change DB to MySQL | `infrastructure/` only |
| Add audit logging | `application/` (service wrapper) + `infrastructure/` |
| Add rate limiting | `api/` middleware |
| Add `GET /tasks?status=done` | `application/` + `api/` |
