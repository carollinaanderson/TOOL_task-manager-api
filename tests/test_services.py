"""Unit tests — domain + application layer (no database required)."""

from __future__ import annotations
from typing import List

import pytest

from app.application.services import DuplicateEmailError, InvalidCredentialsError, TaskNotFoundError, TaskService, UserService
from app.core.security import hash_password, verify_password
from app.domain.entities import Task, User
from app.domain.repositories import TaskRepository, UserRepository


class InMemoryUsers(UserRepository):
    def __init__(self):
        self._rows: dict[str, User] = {}

    def get_by_email(self, email: str) -> User | None:
        return self._rows.get(email)

    def create(self, email: str, password_hash: str) -> User:
        user = User(id=len(self._rows) + 1, email=email, password_hash=password_hash)
        self._rows[email] = user
        return user


class InMemoryTasks(TaskRepository):
    def __init__(self):
        self._rows: dict[int, Task] = {}
        self._seq = 0

    def get(self, task_id: int, owner_id: int) -> Task | None:
        return self._rows.get(task_id) if self._rows.get(task_id) and self._rows[task_id].owner_id == owner_id else None

    def list_by_owner(self, owner_id: int) -> List[Task]:
        return [t for t in self._rows.values() if t.owner_id == owner_id]

    def create(self, task: Task) -> Task:
        self._seq += 1
        task.id = self._seq
        self._rows[task.id] = task
        return task

    def update(self, task: Task) -> Task:
        self._rows[task.id] = task
        return task

    def delete(self, task: Task) -> None:
        del self._rows[task.id]


def test_password_hashing_roundtrip():
    hashed = hash_password("s3cure-pass")
    assert hashed != "s3cure-pass"
    assert verify_password("s3cure-pass", hashed)
    assert not verify_password("wrong", hashed)


def test_register_and_duplicate():
    users = UserService(InMemoryUsers())
    user = users.register("A@Example.com", "s3cure-pass")
    assert user.email == "a@example.com"
    with pytest.raises(DuplicateEmailError):
        users.register("a@example.com", "other-pass")


def test_authenticate_wrong_password():
    users = UserService(InMemoryUsers())
    users.register("a@example.com", "s3cure-pass")
    with pytest.raises(InvalidCredentialsError):
        users.authenticate("a@example.com", "nope")


def test_task_ownership_isolation():
    tasks = TaskService(InMemoryTasks())
    tasks.create(owner_id=1, title="mine", description="", due_date=None)
    with pytest.raises(TaskNotFoundError):
        tasks.get(task_id=1, owner_id=2)


def test_complete_task():
    tasks = TaskService(InMemoryTasks())
    task = tasks.create(owner_id=1, title="ship it", description="", due_date=None)
    done = tasks.complete(task.id, 1)
    assert done.completed is True
