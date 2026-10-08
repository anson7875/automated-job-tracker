import argparse
import json
from pathlib import Path

if __package__:
    from .database import list_jobs, save_job, update_job_status
    from .extractor import extract_requirements
else:
    from database import list_jobs, save_job, update_job_status
    from extractor import extract_requirements


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract requirements from a job description."
    )
    parser.add_argument(
        "file",
        type=Path,
        nargs="?",
        help="Path to a text file containing the job description.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_saved_jobs",
        help="List jobs already stored in the database.",
    )
    parser.add_argument(
        "--status",
        nargs=2,
        metavar=("JOB_ID", "STATUS"),
        help="Update a job status, for example: --status 5 applied.",
    )
    parser.add_argument("--title", help="Job title. Defaults to the file name.")
    parser.add_argument("--company", help="Company name.")
    parser.add_argument(
        "--database",
        type=Path,
        default=Path("data/jobs.db"),
        help="SQLite database path.",
    )

    args = parser.parse_args()

    if args.list_saved_jobs:
        print(json.dumps(list_jobs(args.database), indent=2, ensure_ascii=False))
        return

    if args.status:
        try:
            job_id = int(args.status[0])
        except ValueError:
            parser.error("JOB_ID must be an integer")

        if not update_job_status(args.database, job_id, args.status[1]):
            parser.error(f"No job found with ID {job_id}")

        print(f"Updated job {job_id} status to {args.status[1]}")
        return

    if args.file is None:
        parser.error("file is required unless --list or --status is used")

    if not args.file.exists():
        raise FileNotFoundError(f"File not found: {args.file}")

    job_description = args.file.read_text(encoding="utf-8")
    requirements = extract_requirements(job_description)
    job_id = save_job(
        args.database,
        title=args.title or args.file.stem,
        company=args.company,
        source_file=str(args.file),
        description=job_description,
        requirements=requirements,
    )

    print(json.dumps({"database_id": job_id, **requirements}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
