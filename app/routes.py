"""HTTP routes for task operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response, status

from app.models import TaskSort, TaskStatus
from app.schemas import ErrorResponse, TaskCreate, TaskResponse, TaskUpdate
from app.services import TaskService

router = APIRouter(
    prefix="/api/tasks",
    tags=["tasks"],
    responses={422: {"model": ErrorResponse}},
)


def get_task_service(request: Request) -> TaskService:
    return request.app.state.task_service


TaskServiceDependency = Annotated[TaskService, Depends(get_task_service)]


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    task_service: TaskServiceDependency,
    status_filter: Annotated[TaskStatus, Query(alias="status")] = "all",
    sort: TaskSort | None = None,
) -> list[TaskResponse]:
    return [
        TaskResponse.model_validate(task)
        for task in task_service.list(status=status_filter, sort=sort)
    ]


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(task: TaskCreate, task_service: TaskServiceDependency) -> TaskResponse:
    return TaskResponse.model_validate(task_service.create(task))


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_task(task_id: int, task_service: TaskServiceDependency) -> TaskResponse:
    return TaskResponse.model_validate(task_service.get(task_id))


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    responses={404: {"model": ErrorResponse}},
)
def update_task(
    task_id: int,
    task: TaskUpdate,
    task_service: TaskServiceDependency,
) -> TaskResponse:
    return TaskResponse.model_validate(task_service.update(task_id, task))


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_task(task_id: int, task_service: TaskServiceDependency) -> Response:
    task_service.delete(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
