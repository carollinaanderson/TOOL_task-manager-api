from __future__ import annotations
from typing import Optional

from dataclasses import dataclass, field
from datetime import datetime, timezone


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class User:
    email: str
    password_hash: str
    id: Optional[int] = None
    created_at: datetime = field(default_factory=_utcnow)

    @property
    def is_registered(self) -> bool:
        return self.id is not None


@dataclass
class Task:
    title: str
    owner_id: int
    description: str = ""
    due_date: Optional[datetime] = None
    completed: bool = False
    id: Optional[int] = None
    created_at: datetime = field(default_factory=_utcnow)

    def mark_completed(self) -> None:
        self.completed = True

    def belongs_to(self, user_id: int) -> bool:
        return self.owner_id == user_id
