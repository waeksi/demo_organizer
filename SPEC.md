# Task Organizer - Specification

## 1. Goal

Build a small web application for managing personal tasks.

The project is intended to demonstrate AI-assisted software development using GitHub Copilot Agents, including planning, implementation, testing, code review, and debugging.

## 2. Tech Stack

- **Backend:** Python with FastAPI
- **Database:** SQLite
- **Frontend:** HTML, CSS, and vanilla JavaScript
- **Testing:** pytest and FastAPI TestClient
- **Version control:** Git and GitHub

Keep the architecture simple. Avoid unnecessary dependencies and abstractions.

## 3. Core Features

### 3.1 Task Management

Users must be able to:
- Create a task with a title, description, priority, and optional due date.
- View all tasks.
- Edit existing tasks.
- Mark tasks as completed or reopen them.
- Delete tasks.

### 3.2 Filtering and Sorting

Users must be able to:
- Filter tasks by status: all, open, or completed.
- Sort tasks by due date or priority.

### 3.3 Validation

- Task titles are required and must contain between 1 and 120 characters after trimming whitespace.
- Descriptions are optional and limited to 2,000 characters.
- Priority must be one of: low, medium, high.
- Due dates are optional.
- Invalid input must produce a clear error message.

## 4. Data Model

Each task contains:
- `id`: unique identifier
- `title`: required string
- `description`: optional string
- `priority`: low, medium, or high
- `due_date`: optional date
- `completed`: boolean
- `created_at`: timestamp

## 5. API

Implement REST endpoints for:
- `GET /api/tasks` - list tasks, with optional filtering and sorting
- `POST /api/tasks` - create a task
- `GET /api/tasks/{id}` - retrieve a task
- `PUT /api/tasks/{id}` - update a task
- `DELETE /api/tasks/{id}` - delete a task

Use appropriate HTTP status codes and return consistent JSON responses.

## 6. User Interface

Create a simple, responsive interface that:
- Displays tasks clearly.
- Provides a form to create and edit tasks.
- Shows priority and completion status.
- Supports filtering and sorting.
- Displays useful validation and error messages.
- Handles empty task lists gracefully.

No frontend framework is required.

## 7. Quality Requirements

- Separate API, business logic, and database access where appropriate.
- Use type hints and clear naming in Python.
- Handle errors explicitly.
- Write automated tests for core functionality and validation.
- Tests must not depend on an external service.
- Do not hardcode secrets or credentials.
- The application must run locally using documented instructions.

## 8. Agent Workflow

Use GitHub Copilot Agents throughout development.

- Ask the agent to analyze the specification and propose an implementation plan before coding.
- Implement the application in small, reviewable steps.
- Use agents to write tests, review code, and investigate failures.
- Review generated changes yourself and verify them by running tests.
- Document at least one example where agent output required correction or human intervention.

Record relevant prompts, decisions, mistakes, and lessons learned in `AGENT_WORKFLOW.md`.

## 9. Out of Scope

- User accounts and authentication
- LLM integration into the application itself
- Multi-user collaboration
- Cloud deployment
- Complex permissions or roles

## 10. Definition of Done

The project is complete when:
- All core task operations work.
- Filtering and sorting work.
- Input validation is implemented.
- Automated tests pass.
- The application can be started locally using the README instructions.
- The public repository contains the specification and agent workflow documentation.