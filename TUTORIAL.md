# 🎓 TUTORIAL — Task Manager API end-to-end

> Learn Clean Architecture by building with this API. ~20 minutes. No prior FastAPI knowledge needed — a little Python helps.

## 0. What you'll build & learn

| You will | Concept learned |
|---|---|
| Run the stack locally | Containers, 12-factor config |
| Register + login | JWT auth flow, password hashing |
| Create/complete/delete tasks | CRUD, layered services, ownership |
| Read the tests | Unit vs integration, dependency injection |
| Extend with a new feature | Why the layers exist |

## 1. Run it

```bash
docker compose up --build
# Open http://localhost:8000/docs  →  interactive Swagger UI
```

No Docker? Local setup:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# point DATABASE_URL at a local PostgreSQL, then:
alembic upgrade head
uvicorn app.main:app --reload
```

## 2. Walk the happy path (3 minutes)

**Register** (in Swagger or curl):
```bash
curl -X POST localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"ana@example.com","password":"my-secret-1"}'
# → 201 {"id":1,"email":"ana@example.com"}
```

**Login** (form data):
```bash
curl -X POST localhost:8000/auth/login \
  -d "username=ana@example.com&password=my-secret-1"
# → {"access_token":"eyJ...","token_type":"bearer"}
```

> ⚠️ Copy the token — you'll use it as `Authorization: Bearer <token>` below. The token expires (default 30 min).

**Create a task:**
```bash
curl -X POST localhost:8000/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Finish tutorial","description":"Clean Architecture in practice","due_date":"2026-09-23T12:00:00Z"}'
```

**List, complete, delete:**
```bash
curl localhost:8000/tasks -H "Authorization: Bearer <token>"
curl -X PATCH localhost:8000/tasks/1 -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" -d '{"completed":true}'
curl -X DELETE localhost:8000/tasks/1 -H "Authorization: Bearer <token>"
```

## 3. Follow the request through the layers

A `POST /tasks` request travels:

```
HTTP request
   ↓
api/routes_tasks.py      → validates (Pydantic), extracts current user (JWT)
   ↓
application/services.py  → business rules (TaskService.create)
   ↓
domain/entities.py       → pure Python Task (no framework imports)
   ↓
infrastructure/repositories.py → SQLAlchemy writes to PostgreSQL
   ↓
back up the same way → JSON response
```

**Why this matters:** swap PostgreSQL for MongoDB → only `infrastructure/` changes. Add a business rule ("tasks can't be completed after due date") → only `application/` or `domain/` changes. Nothing else moves.

## 4. Make your first change (exercise)

**Task:** reject titles shorter than 3 characters at the *service* level.

1. Open `app/application/services.py` → `TaskService.create`
2. Add the rule there (the domain owns business rules — do it in the service to keep the exercise small)
3. Write a failing test in `tests/test_services.py` (look at `test_task_ownership_isolation` as a model)
4. `pytest -m unit` → watch it pass

**Challenge:** now add the same rule to `POST /tasks` (schema level) — what happens first? Why do we need both layers?

## 5. Run the quality gates (like a professional)

```bash
ruff check app tests   # style & correctness
bandit -r app -q       # security scanner
pytest                 # full suite (needs DATABASE_URL)
```

Every push also runs these in **GitHub Actions** (`.github/workflows/ci.yml`) — green badge = confidence.

## 6. What next?

- [ ] Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the deep dive
- [ ] Add pagination to `GET /tasks` (hint: service + schema + router)
- [ ] Add a `DELETE /auth/logout` with refresh tokens (see Roadmap in README)
