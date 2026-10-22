# Task API Contract

All endpoints are under `/api`. Successful task responses use the `TaskResponse`
shape defined in `app/schemas.py`; dates are ISO 8601 calendar dates and
`created_at` is an ISO 8601 timestamp. IDs are server-generated positive integers.

## Endpoints

| Method and path | Request | Success response |
| --- | --- | --- |
| `GET /api/tasks` | Optional `status` and `sort` query parameters | `200`, JSON array of tasks |
| `POST /api/tasks` | `TaskCreate` JSON | `201`, created task |
| `GET /api/tasks/{id}` | — | `200`, task |
| `PUT /api/tasks/{id}` | Full `TaskUpdate` JSON | `200`, updated task |
| `DELETE /api/tasks/{id}` | — | `204`, empty body |

`TaskCreate` requires `title` and `priority`; `description` and `due_date` may be
omitted or null. New tasks are open. `TaskUpdate` requires `title`, `priority`,
`description`, `due_date`, and `completed`; nullable fields must be sent as null
when being cleared. Unknown request fields are rejected.

`status` accepts `all` (default), `open`, or `completed`. `sort` accepts
`due_date` or `priority`. Without a sort parameter, tasks are ordered oldest
first. Due-date sorting is ascending with tasks lacking a due date last;
priority sorting is high, medium, then low. Sorted results use creation time and
ID as stable tie-breakers.

Titles are trimmed and must contain 1–120 characters after trimming.
Descriptions may be null and are limited to 2,000 characters. Priority must be
`low`, `medium`, or `high`. Invalid input returns `422`; unknown task IDs return
`404`. Validation errors identify the affected field (using dotted paths for
nested values). Errors use the same envelope:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": [
      { "field": "title", "message": "Title must not be blank" }
    ]
  }
}
```

Validation details may be empty for errors without field-specific information.
