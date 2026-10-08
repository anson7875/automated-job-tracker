"""Import job listings from a CSV file."""

import csv
from pathlib import Path


REQUIRED_COLUMNS = {"title", "company", "url", "description"}


def read_jobs_from_csv(csv_path: Path) -> list[dict]:
    """Read and validate job records from a CSV file."""
    with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        columns = set(reader.fieldnames or [])
        missing_columns = REQUIRED_COLUMNS - columns
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"CSV is missing required columns: {missing}")

        return [
            {
                "title": row["title"].strip(),
                "company": row["company"].strip() or None,
                "url": row["url"].strip() or None,
                "description": row["description"].strip(),
                "location": row.get("location", "").strip() or None,
                "salary_min_hkd": _parse_salary(row.get("salary_min_hkd")),
                "salary_max_hkd": _parse_salary(row.get("salary_max_hkd")),
            }
            for row in reader
        ]


def _parse_salary(value: str | None) -> int | None:
    """Parse an optional salary value from a CSV cell."""
    if not value or not value.strip():
        return None
    return int(float(value.strip()))
