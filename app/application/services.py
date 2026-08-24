from __future__ import annotations
from typing import List, Optional

from dataclasses import dataclass
from datetime import datetime

from app.core.security import hash_password, verify_password
from app.domain.entities import Task, User
from app.domain.repositories import TaskRepository, UserRepository


class DuplicateEmailError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class TaskNotFoundError(Exception):
    pass


@dataclass
class UserService:
    users: UserRepository

    def register(self, email: str, password: str) -> User:
        normalized = email.strip().lower()
        if self.users.get_by_email(normalized):
            raise DuplicateEmailError(normalized)
        return self.users.create(normalized, hash_password(password))

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email.strip().lower())
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        return user


@dataclass
class TaskService:
    tasks: TaskRepository

    def create(self, owner_id: int, title: str, description: str, due_date: Optional[datetime]) -> Task:
        return self.tasks.create(Task(title=title, owner_id=owner_id, description=description, due_date=due_date))

    def list(self, owner_id: int) -> List[Task]:
        return self.tasks.list_by_owner(owner_id)

    def get(self, task_id: int, owner_id: int) -> Task:
        task = self.tasks.get(task_id, owner_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def complete(self, task_id: int, owner_id: int) -> Task:
        task = self.get(task_id, owner_id)
        task.mark_completed()
        return self.tasks.update(task)

    def update(self, task_id: int, owner_id: int, title: Optional[str], description: Optional[str],
               due_date: Optional[datetime], completed: Optional[bool]) -> Task:
        task = self.get(task_id, owner_id)
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if due_date is not None:
            task.due_date = due_date
        if completed is not None:
            task.completed = completed
        return self.tasks.update(task)

    def delete(self, task_id: int, owner_id: int) -> None:
        task = self.get(task_id, owner_id)
        self.tasks.delete(task)
