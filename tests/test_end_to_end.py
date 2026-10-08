import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from job_tracker.csv_importer import read_jobs_from_csv
from job_tracker.database import list_jobs, save_job
from job_tracker.extractor import extract_requirements
from job_tracker.matcher import match_job


class EndToEndTests(unittest.TestCase):
    def test_csv_import_to_recommendation(self):
        csv_path = PROJECT_ROOT / "sample_data" / "jobs.csv"
        profile = json.loads(
            (PROJECT_ROOT / "sample_data" / "user_profile.json").read_text(
                encoding="utf-8"
            )
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "jobs.db"

            for job in read_jobs_from_csv(csv_path):
                requirements = extract_requirements(job["description"])
                save_job(
                    database_path,
                    title=job["title"],
                    company=job["company"],
                    source_file=str(csv_path),
                    description=job["description"],
                    requirements=requirements,
                    source_url=job["url"],
                    location=job["location"],
                    salary_min_hkd=job["salary_min_hkd"],
                    salary_max_hkd=job["salary_max_hkd"],
                )

            jobs = list_jobs(database_path)
            results = []
            for job in jobs:
                requirements = {
                    "minimum_education": job["minimum_education"],
                    "minimum_experience_years": job["minimum_experience_years"],
                    "required_skills": job["required_skills"],
                    "preferred_skills": job["preferred_skills"],
                    "location": job["location"],
                    "salary_min_hkd": job["salary_min_hkd"],
                    "salary_max_hkd": job["salary_max_hkd"],
                }
                results.append(match_job(requirements, profile))

        self.assertEqual(len(jobs), 2)
        self.assertEqual(len(results), 2)
        self.assertTrue(all("match_score" in result for result in results))
        self.assertTrue(all("warnings" in result for result in results))


if __name__ == "__main__":
    unittest.main()
