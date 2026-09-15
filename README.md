# task manager api

> A production-shaped REST API built with **Clean Architecture** — task CRUD, JWT authentication, PostgreSQL persistence, containerized, tested, and CI/CD-ready.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Architecture](https://img.shields.io/badge/Architecture-Clean-6a4fa3.svg)](#-architecture)
[![Database](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)](https://www.postgresql.org/)
[![Tests](https://img.shields.io/badge/Tests-pytest-red.svg)](https://docs.pytest.org/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF.svg)](.github/workflows/ci.yml)
[![Security](https://img.shields.io/badge/Security-DevSecOps-brightgreen.svg)](#-devsecops)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A deliberately small domain, engineered with the same discipline used in production systems:

- **Clean Architecture** — domain, application, and infrastructure layers that respect dependency rules.
- **DevOps-ready** — Docker Compose for local parity, GitHub Actions CI, twelve-factor configuration.
- **DevSecOps-minded** — secrets never in code, dependency pinning, security linter in CI, JWT best practices.
- **Data Engineering hygiene** — schema migrations as versioned, idempotent artifacts (Alembic), structured logs.

---

## ✨ Features

| Feature | Detail |
|---|---|
| 🔐 JWT authentication | OAuth2 password flow, `bcrypt` hashing, token expiry |
| ✅ Task CRUD | Create, read, update, delete with ownership isolation |
| 🧱 Clean Architecture | `domain → application → infrastructure`, testable in isolation |
| 🐘 PostgreSQL | SQLAlchemy 2.0 ORM, Alembic migrations |
| 🐳 Containers | `docker compose up` = full stack (API + Postgres) |
| 🔍 Validation | Pydantic v2 schemas, typed contracts at the edge |
| 🧪 Testing | pytest suite: unit (services), integration (API + DB) |
| 🔒 DevSecOps | `bandit` static security scan in CI, pinned deps |
| 📊 Observability | structured JSON logs, request IDs |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        HTTP (FastAPI)                        │
├─────────────────────────────────────────────────────────────┤
│  api/        →  routers · schemas (Pydantic) · dependencies  │
├─────────────────────────────────────────────────────────────┤
│  application →  services · use-cases · DTOs                  │
├─────────────────────────────────────────────────────────────┤
│  domain      →  entities · business rules (no framework)     │
├─────────────────────────────────────────────────────────────┤
│  infrastructure →  repositories · database · security        │
├─────────────────────────────────────────────────────────────┤
│                PostgreSQL  ·  Alembic migrations             │
└─────────────────────────────────────────────────────────────┘
```

**Dependency rule:** code points *inward*. The domain layer knows nothing about FastAPI, SQLAlchemy, or PostgreSQL — which is what makes the business logic unit-testable in milliseconds and the infrastructure swappable.

```
├── app/
│   ├── main.py              # FastAPI entrypoint, lifespan wiring
│   ├── core/                # config (pydantic-settings), security (JWT/bcrypt)
│   ├── domain/              # entities + business rules (pure Python)
│   ├── application/         # services/use-cases
│   ├── infrastructure/      # database, repositories, auth providers
│   ├── api/                 # routers, schemas, dependencies
│   └── migrations/          # Alembic (versioned, idempotent)
├── tests/                   # unit + integration
├── docker-compose.yml       # API + Postgres
├── Dockerfile               # slim, non-root, multi-stage
└── .github/workflows/ci.yml # lint → test → security scan
```

---

## 🚀 Quickstart

### Prerequisites
- Python 3.12+, Docker Desktop (optional but recommended)

### Option A — Docker Compose (recommended)
```bash
docker compose up --build
# API → http://localhost:8000/docs   (Swagger UI)
```

### Option B — Local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# PostgreSQL running? point APP_DATABASE_URL at it, then:
alembic upgrade head
uvicorn app.main:app --reload
```

### First request
```bash
# 1. Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"s3cure-pass"}'

# 2. Login → copy the access token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"s3cure-pass"}'

# 3. Create a task (use Authorization: Bearer <token>)
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Ship the MVP","description":"Clean architecture first","due_date":"2026-09-23"}'
```

Full walkthrough → [TUTORIAL.md](TUTORIAL.md)

---

## 🧪 Testing & CI

```bash
pytest                                # unit + integration
pytest -m unit                        # domain/services only (no DB)
bandit -r app/                        # static security scan
```

The pipeline in [`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs **lint → tests → security scan → build** on every push/PR — green checks are the contract.

---

## 🔒 DevSecOps practices applied

| Practice | Where |
|---|---|
| No secrets in code | `.env.example` only; config read from environment (12-factor) |
| Password hashing | `bcrypt` (never plaintext, never reversible) |
| JWT hardening | expiry + typed claims; no sensitive data in token |
| Dependency pinning | `requirements.txt` with exact versions |
| Static security scan | `bandit` step in CI |
| Least-privilege container | non-root user in final Docker stage |
| Ownership isolation | every query filtered by `owner_id` (IDOR defense) |

---

## 🗄 Data Engineering practices applied

| Practice | Where |
|---|---|
| Versioned migrations | Alembic — schema is code, auditable, reversible |
| Idempotent setup | `alembic upgrade head` runs safely any number of times |
| Structured logging | JSON lines + request ID for traceability |
| Config as code | `pydantic-settings`, single source of truth, env-driven |

---

## 🗺 Roadmap

- [ ] Pagination, filtering & sorting on task listing
- [ ] Refresh-token rotation & logout endpoint
- [ ] Rate limiting (slowapi) + basic audit log table
- [ ] Prometheus metrics endpoint + `/healthz` readiness probe
- [ ] Terraform module for managed Postgres deploy
- [ ] OpenAPI client generation + contract tests

---

## 📚 Documentation

- [TUTORIAL.md](TUTORIAL.md) — end-to-end walkthrough for newcomers
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — deep dive into each layer
- [docs/API.md](docs/API.md) — endpoint reference (also live at `/docs`)

## 🤝 Contributing

1. Fork it · 2. Create a feature branch · 3. Add tests for anything new · 4. Ensure `pytest` and `bandit` pass · 5. Open a PR with a clear description.

## 📄 License

MIT — use it, learn from it, build on it.
