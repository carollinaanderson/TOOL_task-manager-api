from __future__ import annotations
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pythonjsonlogger.json import JsonFormatter

from app.api.routes_auth import router as auth_router
from app.api.routes_tasks import router as tasks_router
from app.core.config import get_settings

settings = get_settings()

_log = logging.getLogger("app")
_handler = logging.StreamHandler()
_handler.setFormatter(JsonFormatter())
_log.addHandler(_handler)
_log.setLevel(logging.DEBUG if settings.app_debug else logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _log.info("starting", extra={"app": settings.app_name, "env": settings.app_env})
    yield
    _log.info("shutting down")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Task management REST API — Clean Architecture, JWT auth, PostgreSQL.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tasks_router)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/healthz", tags=["ops"])
def healthz() -> dict:
    return {"status": "ok", "app": settings.app_name}
