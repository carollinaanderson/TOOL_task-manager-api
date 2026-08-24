from __future__ import annotations
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.dependencies import get_current_user, get_task_service
from app.api.schemas import TaskCreate, TaskRead, TaskUpdate
from app.application.services import TaskNotFoundError, TaskService
from app.domain.entities import User

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _must_get(tasks: TaskService, task_id: int, user_id: int) -> TaskRead:
    try:
        return TaskRead(**vars(tasks.get(task_id, user_id)))
    except TaskNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")


@router.get("", response_model=List[TaskRead])
def list_tasks(current_user: User = Depends(get_current_user), tasks: TaskService = Depends(get_task_service)) -> List[TaskRead]:
    return [TaskRead(**vars(t)) for t in tasks.list(current_user.id)]


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, current_user: User = Depends(get_current_user),
                tasks: TaskService = Depends(get_task_service)) -> TaskRead:
    task = tasks.create(current_user.id, payload.title, payload.description, payload.due_date)
    return TaskRead(**vars(task))


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, current_user: User = Depends(get_current_user), tasks: TaskService = Depends(get_task_service)) -> TaskRead:
    return _must_get(tasks, task_id, current_user.id)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, current_user: User = Depends(get_current_user),
                tasks: TaskService = Depends(get_task_service)) -> TaskRead:
    _must_get(tasks, task_id, current_user.id)
    updated = tasks.update(
        task_id=task_id,
        owner_id=current_user.id,
        title=payload.title, description=payload.description,
        due_date=payload.due_date, completed=payload.completed,
    )
    return TaskRead(**vars(updated))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_task(task_id: int, current_user: User = Depends(get_current_user), tasks: TaskService = Depends(get_task_service)) -> Response:
    _must_get(tasks, task_id, current_user.id)
    tasks.delete(task_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
