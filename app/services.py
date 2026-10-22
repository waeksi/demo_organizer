"""Task operations between the API and persistence layers."""

from app.models import Priority, TaskRecord, TaskSort, TaskStatus
from app.repository import TaskRepository
from app.schemas import TaskCreate, TaskUpdate


class TaskNotFoundError(Exception):
    """Raised when an operation references a task that does not exist."""


class TaskService:
    """Apply task operations using the task repository."""

    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def create(self, task: TaskCreate) -> TaskRecord:
        return self._repository.create(
            title=task.title,
            priority=task.priority,
            description=task.description,
            due_date=task.due_date,
        )

    def list(self, status: TaskStatus, sort: TaskSort | None) -> list[TaskRecord]:
        return self._repository.list(status=status, sort=sort)

    def get(self, task_id: int) -> TaskRecord:
        task = self._repository.get(task_id)
        if task is None:
            raise TaskNotFoundError
        return task

    def update(self, task_id: int, task: TaskUpdate) -> TaskRecord:
        updated_task = self._repository.update(
            task_id=task_id,
            title=task.title,
            priority=task.priority,
            description=task.description,
            due_date=task.due_date,
            completed=task.completed,
        )
        if updated_task is None:
            raise TaskNotFoundError
        return updated_task

    def delete(self, task_id: int) -> None:
        if not self._repository.delete(task_id):
            raise TaskNotFoundError
