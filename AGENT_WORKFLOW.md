# Agent Workflow

This file records the prompts, decisions, corrections, and lessons from the
implementation process.

## Planning

- Prompt: “Read `SPEC.md` and analyze the requirements. Do not implement anything
  yet.”
- Human review approved a minimal FastAPI/SQLite/vanilla-JavaScript structure
  before implementation began.

## Decisions

- `PUT` replaces all editable fields and requires `completed`; clients send
  `null` when clearing optional description or due date.
- The task list defaults to creation-time ascending; due dates sort ascending
  with missing dates last, and priorities sort high, medium, then low.
- The repository receives an explicit SQLite path so API tests can use isolated
  temporary databases; local development uses `TASK_ORGANIZER_DB_PATH` or the
  application data directory.
- API validation and not-found errors share the documented JSON error envelope.

## Implementation notes and lessons

- During schema work, initial title-length validation ran before whitespace
  trimming, which could allow a whitespace-only title through the length check.
  The validator was corrected to trim before field constraints run. Lesson:
  test normalized values at their boundaries, not only ordinary valid inputs.
- The implementation was completed in small layers: schemas and contract,
  SQLite persistence, task operations and API endpoints, frontend, tests, then
  local run documentation.
- Prompt: “Proceed with the next step. remember to record relevant prompts,
  decisions, mistakes, and lessons learned in `AGENT_WORKFLOW.md`.”
- The service layer translates missing-task results into one explicit domain
  exception; the API maps it to a consistent `404` response. FastAPI request
  validation is mapped to the documented `422` envelope.
- Prompt: “Good. proceed with the next step.”
- The UI uses DOM text nodes for task-supplied content rather than HTML
  interpolation, and all updates—including completion toggles—send the full
  editable task representation required by `PUT`. UI smoke coverage is part of
  the upcoming automated test step.
- During UI review, create and update requests were separated explicitly:
  creation omits the update-only completion field, while edit mode preserves
  the existing completion state. Completion toggles construct a clean
  `TaskUpdate` payload instead of forwarding response-only fields. Lesson:
  keep API request payloads distinct from response objects, particularly when
  schemas reject unknown fields.
- Prompt: “good. proceed with the next path. remember to document relevant
  things”
- Tests use a new `tmp_path` SQLite file per client fixture. API checks cover
  CRUD, status filters, due-date/priority order, validation envelopes, and
  serving the UI assets; no external service is involved.
- Validation includes both exact maximum-length values and over-limit/blank
  values, alongside invalid filter values and incomplete full-update payloads.
  The first test run passed all eight tests; boundary cases were then expanded
  to guard the limits explicitly.
- Prompt: “Good. Proceed with the last step.”
- README instructions use a local virtual environment, install runtime or
  development dependencies, start Uvicorn, and run pytest. The default database
  is local to the app; `TASK_ORGANIZER_DB_PATH` allows selecting another path.
- A JavaScript syntax check initially could not find Node because the installer
  directory was not on the current shell's `PATH`; it passed when run using
  `C:\Program Files\nodejs\node.exe`. Lesson: distinguish an unavailable
  executable from a missing installation and verify using its installed path.
