"""SQLite connection management and database initialization."""

import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK (length(trim(title)) BETWEEN 1 AND 120),
    description TEXT CHECK (description IS NULL OR length(description) <= 2000),
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high')),
    due_date TEXT,
    completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
"""


@contextmanager
def database_connection(database_path: Path) -> Iterator[sqlite3.Connection]:
    """Open a transaction-scoped connection to a SQLite database file."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(database_path)) as connection:
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise


def initialize_database(database_path: Path) -> None:
    """Create the task table if it does not already exist."""
    with database_connection(database_path) as connection:
        connection.executescript(SCHEMA)
