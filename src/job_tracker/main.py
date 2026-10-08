import argparse
import json
from pathlib import Path

if __package__:
    from .csv_importer import read_jobs_from_csv
    from .database import list_jobs, save_job, update_job_status
    from .extractor import extract_requirements
    from .matcher import match_job
    from .jobsdb_collector import collect_jobs as collect_jobs_from_url
else:
    from csv_importer import read_jobs_from_csv
    from database import list_jobs, save_job, update_job_status
    from extractor import extract_requirements
    from matcher import match_job
    from jobsdb_collector import collect_jobs as collect_jobs_from_url


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
    parser.add_argument(
        "--import-csv",
        type=Path,
        help="Import multiple job listings from a CSV file.",
    )
    parser.add_argument(
        "--jobsdb-url",
        help="Collect JobsDB jobs from a filtered search URL.",
    )
    parser.add_argument(
        "--jobsdb-max-jobs",
        type=int,
        default=20,
        help="Maximum JobsDB detail pages to process.",
    )
    parser.add_argument(
        "--match-profile",
        type=Path,
        help="Match saved jobs against a user profile JSON file.",
    )
    parser.add_argument(
        "--recommend",
        type=Path,
        help="Rank saved jobs against a user profile JSON file.",
    )
    parser.add_argument(
        "--minimum-score",
        type=int,
        default=0,
        help="Only show recommendations at or above this score.",
    )
    parser.add_argument("--title", help="Job title. Defaults to the file name.")
    parser.add_argument("--company", help="Company name.")
    parser.add_argument("--url", help="Original job listing URL.")
    parser.add_argument("--location", help="Job location.")
    parser.add_argument("--salary-min-hkd", type=int, help="Minimum salary in HKD.")
    parser.add_argument("--salary-max-hkd", type=int, help="Maximum salary in HKD.")
    parser.add_argument(
        "--database",
        type=Path,
        default=Path("data/jobs.db"),
        help="SQLite database path.",
    )

    args = parser.parse_args()

    if args.match_profile or args.recommend:
        profile_path = args.recommend or args.match_profile
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile file not found: {profile_path}")

        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        matched_jobs = []
        for job in list_jobs(args.database):
            requirements = {
                "minimum_education": job["minimum_education"],
                "minimum_experience_years": job["minimum_experience_years"],
                "required_skills": job["required_skills"],
                "preferred_skills": job["preferred_skills"],
                "location": job["location"],
                "salary_min_hkd": job["salary_min_hkd"],
                "salary_max_hkd": job["salary_max_hkd"],
            }
            matched_jobs.append({
                "database_id": job["id"],
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                **match_job(requirements, profile),
            })

        if args.recommend:
            matched_jobs = [
                job for job in matched_jobs
                if job["match_score"] >= args.minimum_score
            ]
            matched_jobs.sort(key=lambda job: job["match_score"], reverse=True)

        print(json.dumps(matched_jobs, indent=2, ensure_ascii=False))
        return

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

    if args.import_csv:
        if not args.import_csv.exists():
            raise FileNotFoundError(f"CSV file not found: {args.import_csv}")

        imported_jobs = []
        for job in read_jobs_from_csv(args.import_csv):
            requirements = extract_requirements(job["description"])
            job_id = save_job(
                args.database,
                title=job["title"],
                company=job["company"],
                source_file=str(args.import_csv),
                description=job["description"],
                requirements=requirements,
                source_url=job["url"],
                location=job["location"],
                salary_min_hkd=job["salary_min_hkd"],
                salary_max_hkd=job["salary_max_hkd"],
            )
            imported_jobs.append({"database_id": job_id, **job, **requirements})

        print(json.dumps(imported_jobs, indent=2, ensure_ascii=False))
        return

    if args.jobsdb_url:
        imported_jobs = []
        for job in collect_jobs_from_url(args.jobsdb_url, args.jobsdb_max_jobs):
            requirements = extract_requirements(job["description"])
            job_id = save_job(
                args.database,
                title=job["title"],
                company=job["company"],
                source_file="jobsdb:search-url",
                description=job["description"],
                requirements=requirements,
                source_url=job["url"],
                location=job["location"],
                salary_min_hkd=job["salary_min_hkd"],
                salary_max_hkd=job["salary_max_hkd"],
            )
            imported_jobs.append({"database_id": job_id, **job, **requirements})

        print(json.dumps(imported_jobs, indent=2, ensure_ascii=False))
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
        source_url=args.url,
        location=args.location,
        salary_min_hkd=args.salary_min_hkd,
        salary_max_hkd=args.salary_max_hkd,
    )

    print(json.dumps({"database_id": job_id, **requirements}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
