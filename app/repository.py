"""SQLite persistence operations for tasks."""

import sqlite3
from datetime import date, datetime
from pathlib import Path

from app.database import database_connection
from app.models import Priority, TaskRecord, TaskSort, TaskStatus

_SORT_CLAUSES = {
    "due_date": "due_date IS NULL ASC, due_date ASC, created_at ASC, id ASC",
    "priority": (
        "CASE priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END ASC, "
        "created_at ASC, id ASC"
    ),
}


class TaskRepository:
    """Persist tasks using the configured SQLite database file."""

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path

    def create(
        self,
        title: str,
        priority: Priority,
        description: str | None = None,
        due_date: date | None = None,
    ) -> TaskRecord:
        with database_connection(self._database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (title, priority, description, due_date)
                VALUES (?, ?, ?, ?)
                """,
                (title, priority, description, due_date.isoformat() if due_date else None),
            )
            task = self._get(connection, cursor.lastrowid)
            if task is None:
                raise RuntimeError("Inserted task could not be retrieved")
            return task

    def list(
        self,
        status: TaskStatus = "all",
        sort: TaskSort | None = None,
    ) -> list[TaskRecord]:
        where_clause = ""
        parameters: tuple[int, ...] = ()
        if status == "open":
            where_clause = "WHERE completed = ?"
            parameters = (0,)
        elif status == "completed":
            where_clause = "WHERE completed = ?"
            parameters = (1,)

        order_clause = _SORT_CLAUSES.get(sort, "created_at ASC, id ASC")
        with database_connection(self._database_path) as connection:
            rows = connection.execute(
                f"SELECT * FROM tasks {where_clause} ORDER BY {order_clause}",
                parameters,
            ).fetchall()
            return [self._record_from_row(row) for row in rows]

    def get(self, task_id: int) -> TaskRecord | None:
        with database_connection(self._database_path) as connection:
            return self._get(connection, task_id)

    def update(
        self,
        task_id: int,
        title: str,
        priority: Priority,
        description: str | None,
        due_date: date | None,
        completed: bool,
    ) -> TaskRecord | None:
        with database_connection(self._database_path) as connection:
            cursor = connection.execute(
                """
                UPDATE tasks
                SET title = ?, priority = ?, description = ?, due_date = ?, completed = ?
                WHERE id = ?
                """,
                (
                    title,
                    priority,
                    description,
                    due_date.isoformat() if due_date else None,
                    int(completed),
                    task_id,
                ),
            )
            if cursor.rowcount == 0:
                return None
            return self._get(connection, task_id)

    def delete(self, task_id: int) -> bool:
        with database_connection(self._database_path) as connection:
            cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0

    @classmethod
    def _get(
        cls,
        connection: sqlite3.Connection,
        task_id: int | None,
    ) -> TaskRecord | None:
        if task_id is None:
            return None
        row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return cls._record_from_row(row) if row is not None else None

    @staticmethod
    def _record_from_row(row: sqlite3.Row) -> TaskRecord:
        due_date_value = row["due_date"]
        return TaskRecord(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            priority=row["priority"],
            due_date=date.fromisoformat(due_date_value) if due_date_value else None,
            completed=bool(row["completed"]),
            created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
        )
