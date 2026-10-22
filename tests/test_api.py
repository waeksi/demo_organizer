from fastapi.testclient import TestClient


def create_task(
    client: TestClient,
    title: str,
    priority: str = "medium",
    **fields: object,
) -> dict[str, object]:
    response = client.post(
        "/api/tasks",
        json={"title": title, "priority": priority, **fields},
    )
    assert response.status_code == 201
    return response.json()


def test_create_and_list_tasks(client: TestClient) -> None:
    task = create_task(
        client,
        "  Plan weekend  ",
        "high",
        description="Make a short list",
        due_date="2026-10-20",
    )

    assert task["title"] == "Plan weekend"
    assert task["description"] == "Make a short list"
    assert task["priority"] == "high"
    assert task["due_date"] == "2026-10-20"
    assert task["completed"] is False
    assert task["id"] > 0
    assert task["created_at"]
    assert client.get("/api/tasks").json() == [task]


def test_create_accepts_validation_boundaries(client: TestClient) -> None:
    task = create_task(
        client,
        "t" * 120,
        description="d" * 2000,
    )

    assert len(task["title"]) == 120
    assert len(task["description"]) == 2000
    assert task["due_date"] is None


def test_get_update_completion_reopen_and_delete(client: TestClient) -> None:
    task = create_task(client, "Write report")
    task_id = task["id"]
    assert client.get(f"/api/tasks/{task_id}").json() == task

    update = {
        "title": "Review report",
        "description": None,
        "priority": "low",
        "due_date": None,
        "completed": True,
    }
    response = client.put(f"/api/tasks/{task_id}", json=update)
    assert response.status_code == 200
    assert response.json()["title"] == "Review report"
    assert response.json()["completed"] is True
    assert response.json()["description"] is None
    assert response.json()["created_at"] == task["created_at"]

    update["completed"] = False
    reopened = client.put(f"/api/tasks/{task_id}", json=update)
    assert reopened.status_code == 200
    assert reopened.json()["completed"] is False

    assert client.delete(f"/api/tasks/{task_id}").status_code == 204
    assert client.get(f"/api/tasks/{task_id}").status_code == 404
    assert client.delete(f"/api/tasks/{task_id}").status_code == 404


def test_list_filters_by_status(client: TestClient) -> None:
    open_task = create_task(client, "Open task")
    completed_task = create_task(client, "Finished task")
    updated = client.put(
        f"/api/tasks/{completed_task['id']}",
        json={
            "title": completed_task["title"],
            "description": completed_task["description"],
            "priority": completed_task["priority"],
            "due_date": completed_task["due_date"],
            "completed": True,
        },
    )
    assert updated.status_code == 200

    assert [task["id"] for task in client.get("/api/tasks?status=open").json()] == [
        open_task["id"]
    ]
    assert [
        task["id"] for task in client.get("/api/tasks?status=completed").json()
    ] == [completed_task["id"]]
    assert len(client.get("/api/tasks?status=all").json()) == 2


def test_list_sorts_by_due_date_and_priority(client: TestClient) -> None:
    no_date = create_task(client, "No date", "high")
    later = create_task(client, "Later", "low", due_date="2026-10-20")
    earlier = create_task(client, "Earlier", "medium", due_date="2026-10-10")
    another_high = create_task(client, "Another high", "high")

    due_date_ids = [
        task["id"] for task in client.get("/api/tasks?sort=due_date").json()
    ]
    assert due_date_ids == [earlier["id"], later["id"], no_date["id"], another_high["id"]]

    priority_values = [
        task["priority"] for task in client.get("/api/tasks?sort=priority").json()
    ]
    assert priority_values == ["high", "high", "medium", "low"]
    priority_ids = [
        task["id"] for task in client.get("/api/tasks?sort=priority").json()
    ]
    assert priority_ids[:2] == [no_date["id"], another_high["id"]]


def test_missing_task_responses_use_error_envelope(client: TestClient) -> None:
    response = client.get("/api/tasks/98765")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": "Task not found",
            "details": [],
        }
    }


def test_validation_errors_are_clear_and_consistent(client: TestClient) -> None:
    invalid_payloads = [
        ({"title": "   ", "priority": "low"}, "title"),
        ({"title": "t" * 121, "priority": "low"}, "title"),
        ({"title": "Valid", "priority": "urgent"}, "priority"),
        ({"title": "Valid", "priority": "low", "description": "d" * 2001}, "description"),
        ({"title": "Valid", "priority": "low", "due_date": "not-a-date"}, "due_date"),
    ]

    for payload, expected_field in invalid_payloads:
        response = client.post("/api/tasks", json=payload)
        assert response.status_code == 422
        error = response.json()["error"]
        assert error["code"] == "validation_error"
        assert error["message"] == "Request validation failed"
        assert expected_field in {issue["field"] for issue in error["details"]}

    invalid_filter = client.get("/api/tasks?status=archived")
    assert invalid_filter.status_code == 422
    assert invalid_filter.json()["error"]["code"] == "validation_error"


def test_put_requires_all_editable_fields_and_rejects_unknown_fields(
    client: TestClient,
) -> None:
    missing_completion = client.put(
        "/api/tasks/1",
        json={
            "title": "Task",
            "priority": "low",
            "description": None,
            "due_date": None,
        },
    )
    assert missing_completion.status_code == 422
    assert "completed" in {
        issue["field"] for issue in missing_completion.json()["error"]["details"]
    }

    extra_field = client.post(
        "/api/tasks",
        json={"title": "Task", "priority": "low", "unexpected": True},
    )
    assert extra_field.status_code == 422


def test_ui_and_static_assets_are_served(client: TestClient) -> None:
    page = client.get("/")
    assert page.status_code == 200
    assert "Task organizer" in page.text
    assert client.get("/static/styles.css").status_code == 200
    assert client.get("/static/app.js").status_code == 200
