"""Integration tests — full API against a real database (needs PostgreSQL)."""
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.database import Base, get_db
from app.main import app

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg2://task_user:task_pass@localhost:5432/task_manager")
engine = create_engine(DATABASE_URL, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="module")
def token():
    email, password = "tester@example.com", "s3cure-pass"
    client.post("/auth/register", json={"email": email, "password": password})
    resp = client.post("/auth/login", data={"username": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_healthz():
    assert client.get("/healthz").json()["status"] == "ok"


def test_task_lifecycle(token):
    headers = {"Authorization": f"Bearer {token}"}
    created = client.post("/tasks", headers=headers, json={"title": "First task", "description": "hello"}).json()
    assert created["title"] == "First task"

    listed = client.get("/tasks", headers=headers).json()
    assert any(t["id"] == created["id"] for t in listed)

    updated = client.patch(f"/tasks/{created['id']}", headers=headers, json={"completed": True}).json()
    assert updated["completed"] is True

    assert client.delete(f"/tasks/{created['id']}", headers=headers).status_code == 204


def test_unauthenticated_is_rejected():
    assert client.get("/tasks").status_code == 401
