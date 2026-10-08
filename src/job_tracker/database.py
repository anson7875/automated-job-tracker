"""SQLite storage for parsed job listings."""

import json
import sqlite3
from contextlib import closing
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT,
    source_file TEXT NOT NULL,
    description TEXT NOT NULL,
    minimum_education TEXT,
    minimum_experience_years INTEGER,
    required_skills TEXT NOT NULL,
    preferred_skills TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'discovered',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

VALID_STATUSES = {
    "discovered",
    "interested",
    "applied",
    "interview",
    "rejected",
    "archived",
}


def initialize_database(database_path: Path) -> None:
    """Create the database and jobs table if they do not exist."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(SCHEMA)


def save_job(
    database_path: Path,
    *,
    title: str,
    company: str | None,
    source_file: str,
    description: str,
    requirements: dict,
    status: str = "discovered",
) -> int:
    """Save one job and return its database ID."""
    initialize_database(database_path)

    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO jobs (
                    title, company, source_file, description,
                minimum_education, minimum_experience_years,
                    required_skills, preferred_skills, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    title,
                    company,
                    source_file,
                    description,
                    requirements["minimum_education"],
                    requirements["minimum_experience_years"],
                    json.dumps(requirements["required_skills"]),
                    json.dumps(requirements["preferred_skills"]),
                    status,
                ),
            )
            return cursor.lastrowid


def list_jobs(database_path: Path) -> list[dict]:
    """Return all saved jobs with JSON skill fields decoded."""
    initialize_database(database_path)

    with closing(sqlite3.connect(database_path)) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT id, title, company, source_file,
                   minimum_education, minimum_experience_years,
                   required_skills, preferred_skills, status, created_at
            FROM jobs
            ORDER BY id
            """
        ).fetchall()

    jobs = []
    for row in rows:
        job = dict(row)
        job["required_skills"] = json.loads(job["required_skills"])
        job["preferred_skills"] = json.loads(job["preferred_skills"])
        jobs.append(job)
    return jobs


def update_job_status(database_path: Path, job_id: int, status: str) -> bool:
    """Update one job's status and return whether the job existed."""
    if status not in VALID_STATUSES:
        valid_statuses = ", ".join(sorted(VALID_STATUSES))
        raise ValueError(f"Invalid status. Choose one of: {valid_statuses}")

    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            cursor = connection.execute(
                "UPDATE jobs SET status = ? WHERE id = ?",
                (status, job_id),
            )
            return cursor.rowcount == 1
