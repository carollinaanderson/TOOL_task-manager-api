from __future__ import annotations
from typing import List

from abc import ABC, abstractmethod

from app.domain.entities import Task, User


class UserRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def create(self, email: str, password_hash: str) -> User: ...


class TaskRepository(ABC):
    @abstractmethod
    def get(self, task_id: int, owner_id: int) -> Task | None: ...

    @abstractmethod
    def list_by_owner(self, owner_id: int) -> List[Task]: ...

    @abstractmethod
    def create(self, task: Task) -> Task: ...

    @abstractmethod
    def update(self, task: Task) -> Task: ...

    @abstractmethod
    def delete(self, task: Task) -> None: ...
