from __future__ import annotations
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import Task, User
from app.domain.repositories import TaskRepository, UserRepository
from app.infrastructure.orm import TaskORM, UserORM


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_email(self, email: str) -> User | None:
        row = self._session.execute(select(UserORM).where(UserORM.email == email)).scalar_one_or_none()
        return None if row is None else User(id=row.id, email=row.email, password_hash=row.password_hash)

    def create(self, email: str, password_hash: str) -> User:
        row = UserORM(email=email, password_hash=password_hash)
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return User(id=row.id, email=row.email, password_hash=row.password_hash)


class SqlAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_entity(row: TaskORM) -> Task:
        return Task(
            id=row.id, title=row.title, description=row.description,
            due_date=row.due_date, completed=row.completed, owner_id=row.owner_id,
        )

    def get(self, task_id: int, owner_id: int) -> Task | None:
        row = self._session.execute(
            select(TaskORM).where(TaskORM.id == task_id, TaskORM.owner_id == owner_id)
        ).scalar_one_or_none()
        return None if row is None else self._to_entity(row)

    def list_by_owner(self, owner_id: int) -> List[Task]:
        rows = self._session.execute(select(TaskORM).where(TaskORM.owner_id == owner_id)).scalars().all()
        return [self._to_entity(r) for r in rows]

    def create(self, task: Task) -> Task:
        row = TaskORM(title=task.title, description=task.description, due_date=task.due_date,
                      completed=task.completed, owner_id=task.owner_id)
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return self._to_entity(row)

    def update(self, task: Task) -> Task:
        row = self._session.get(TaskORM, task.id)
        row.title, row.description, row.due_date, row.completed = task.title, task.description, task.due_date, task.completed
        self._session.commit()
        self._session.refresh(row)
        return self._to_entity(row)

    def delete(self, task: Task) -> None:
        row = self._session.get(TaskORM, task.id)
        self._session.delete(row)
        self._session.commit()
