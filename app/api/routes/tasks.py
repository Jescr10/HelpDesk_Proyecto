"""Tareas integradas en la misma API y unidad de trabajo de HelpDesk."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.api.dependencies import CurrentUser, DbSession, ServicesDep
from app.repositories.tasks import SqlAlchemyTaskRepository
from app.schemas.tasks import TaskCreate, TaskOut
from app.services.tasks import TaskService

router = APIRouter(prefix="/tickets/{ticket_id}/tasks", tags=["tasks"])
PositiveId = Annotated[int, Path(gt=0)]


def get_tasks(db: DbSession, services: ServicesDep) -> TaskService:
    return TaskService(SqlAlchemyTaskRepository(db), services.tickets)


TasksDep = Annotated[TaskService, Depends(get_tasks)]


@router.get("", response_model=list[TaskOut])
def list_tasks(ticket_id: PositiveId, user: CurrentUser, tasks: TasksDep):
    return tasks.list(user, ticket_id)


@router.post("", response_model=TaskOut, status_code=201)
def add_task(ticket_id: PositiveId, body: TaskCreate, user: CurrentUser, tasks: TasksDep):
    return tasks.add(user, ticket_id, body.descripcion)


@router.post("/{task_id}/complete", response_model=TaskOut)
def complete_task(ticket_id: PositiveId, task_id: PositiveId, user: CurrentUser, tasks: TasksDep):
    return tasks.complete(user, ticket_id, task_id)
