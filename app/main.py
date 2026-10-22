"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.database import initialize_database
from app.repository import TaskRepository
from app.routes import router
from app.schemas import ErrorResponse, ValidationIssue
from app.services import TaskNotFoundError, TaskService


def create_app(database_path: Path | None = None) -> FastAPI:
    resolved_path = database_path or Path(
        os.getenv(
            "TASK_ORGANIZER_DB_PATH",
            str(Path(__file__).parent / "data" / "tasks.sqlite3"),
        )
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        initialize_database(resolved_path)
        app.state.task_service = TaskService(TaskRepository(resolved_path))
        yield

    app = FastAPI(title="Task Organizer API", lifespan=lifespan)
    app.include_router(router)
    static_directory = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_directory), name="static")

    @app.get("/", include_in_schema=False)
    async def task_organizer_ui() -> FileResponse:
        return FileResponse(static_directory / "index.html")

    @app.exception_handler(TaskNotFoundError)
    async def task_not_found_handler(
        request: Request,
        exc: TaskNotFoundError,
    ) -> JSONResponse:
        error = ErrorResponse(
            error={
                "code": "not_found",
                "message": "Task not found",
            }
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error.model_dump(mode="json"),
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        issues = [
            ValidationIssue(
                field=".".join(
                    str(part)
                    for part in error["loc"]
                    if part not in {"body", "query", "path", "header"}
                ),
                message=error["msg"],
            )
            for error in exc.errors()
        ]
        error = ErrorResponse(
            error={
                "code": "validation_error",
                "message": "Request validation failed",
                "details": issues,
            }
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error.model_dump(mode="json"),
        )

    return app


app = create_app()
