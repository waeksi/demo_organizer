"""Request and response schemas for the task API."""

from datetime import date, datetime


from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import Priority, TaskSort, TaskStatus


class TaskContent(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    title: str = Field(min_length=1, max_length=120)
    priority: Priority

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class TaskCreate(TaskContent):
    description: str | None = Field(default=None, max_length=2000)
    due_date: date | None = None


class TaskUpdate(TaskContent):
    description: str | None = Field(max_length=2000)
    due_date: date | None
    completed: bool


class TaskResponse(TaskContent):
    id: int = Field(gt=0)
    description: str | None = Field(max_length=2000)
    due_date: date | None
    completed: bool
    created_at: datetime


class TaskListQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: TaskStatus = "all"
    sort: TaskSort | None = None


class ValidationIssue(BaseModel):
    field: str
    message: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[ValidationIssue] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: ErrorDetail
