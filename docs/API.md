# 🔌 API Reference

> Interactive docs: `http://localhost:8000/docs` (Swagger) · `http://localhost:8000/redoc`.
> All task endpoints require `Authorization: Bearer <token>`.

## Auth

### `POST /auth/register` — create account
Body: `{"email": "you@example.com", "password": "min-8-chars"}`
→ `201` `{"id": 1, "email": "you@example.com"}` · `409` email exists

### `POST /auth/login` — get token (OAuth2 form)
Body (form): `username` · `password`
→ `200` `{"access_token": "eyJ...", "token_type": "bearer"}` · `401` invalid

## Tasks

### `GET /tasks` — list my tasks
→ `200` `[{"id":1,"title":"...","description":"...","due_date":null,"completed":false,"owner_id":1,"created_at":"..."}]`

### `POST /tasks` — create
Body: `{"title": "required 1–255", "description": "optional", "due_date": "optional ISO-8601"}`
→ `201` task object

### `GET /tasks/{id}` — get one (only if yours)
→ `200` task · `404` not found / not yours

### `PATCH /tasks/{id}` — partial update
Body: any of `{"title","description","due_date","completed"}`
→ `200` updated task · `404`

### `DELETE /tasks/{id}` — delete
→ `204` no content · `404`

## Ops

### `GET /healthz` — liveness
→ `200` `{"status":"ok","app":"Task Manager API"}`

## Error format
```json
{"detail": "human-readable message"}
```
| Status | Meaning |
|---|---|
| 401 | missing/expired/invalid token |
| 404 | resource not found (or not yours) |
| 409 | duplicate email |
| 422 | validation failed (see `detail` array) |
