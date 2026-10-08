# Automated Job Tracker

A rule-based personal job tracker. It imports job listings from CSV, extracts
basic requirements without AI, stores them in SQLite, and ranks jobs against a
user profile.

## Features

- Extract minimum education and experience with regular expressions
- Extract required and preferred skills
- Import multiple jobs from CSV
- Store jobs in SQLite
- Prevent duplicates with `source_url`
- Match education, experience, skills, salary, and location
- Track job status: `discovered`, `interested`, `applied`, `interview`, `rejected`, or `archived`

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

The project uses only Python's standard library, so no extra packages are required.

## CSV Format

Required columns:

```csv
title,company,url,description
```

Optional columns:

```csv
location,salary_min_hkd,salary_max_hkd
```

## Import Jobs

```powershell
py src\job_tracker\main.py --import-csv sample_data\jobs.csv
```

Use a separate database while experimenting:

```powershell
py src\job_tracker\main.py --import-csv sample_data\jobs.csv --database data\test.db
```

## View and Match Jobs

```powershell
py src\job_tracker\main.py --list
py src\job_tracker\main.py --match-profile sample_data\user_profile.json
py src\job_tracker\main.py --recommend sample_data\user_profile.json --minimum-score 50
```

## Update Status

```powershell
py src\job_tracker\main.py --status 1 applied
```

## Run Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The test suite covers extraction, CSV import, database storage, duplicate
prevention, matching, and the end-to-end import-to-recommendation workflow.
