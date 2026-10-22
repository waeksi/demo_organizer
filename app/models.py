"""Shared task types and domain data structures."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

Priority = Literal["low", "medium", "high"]
TaskStatus = Literal["all", "open", "completed"]
TaskSort = Literal["due_date", "priority"]


@dataclass(frozen=True)
class TaskRecord:
    id: int
    title: str
    description: str | None
    priority: Priority
    due_date: date | None
    completed: bool
    created_at: datetime
