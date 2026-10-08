from pathlib import Path
import json
import sys
import tempfile
import unittest
from contextlib import closing


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from job_tracker.database import list_jobs, save_job, update_job_status


class DatabaseTests(unittest.TestCase):
    def test_saves_job_requirements(self):
        requirements = {
            "minimum_education": "Bachelor's degree",
            "minimum_experience_years": 2,
            "required_skills": ["Python", "SQL"],
            "preferred_skills": ["AWS"],
        }

        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "jobs.db"
            job_id = save_job(
                database_path,
                title="Software Engineer",
                company="Example Company",
                source_file="sample_data.txt",
                description="Sample description",
                requirements=requirements,
            )

            self.assertEqual(job_id, 1)

            import sqlite3

            with closing(sqlite3.connect(database_path)) as connection:
                row = connection.execute(
                    "SELECT title, required_skills, status FROM jobs WHERE id = ?",
                    (job_id,),
                ).fetchone()

            self.assertEqual(row[0], "Software Engineer")
            self.assertEqual(json.loads(row[1]), ["Python", "SQL"])
            self.assertEqual(row[2], "discovered")

            saved_jobs = list_jobs(database_path)
            self.assertTrue(update_job_status(database_path, job_id, "applied"))
            updated_jobs = list_jobs(database_path)

        self.assertEqual(saved_jobs[0]["id"], 1)
        self.assertEqual(saved_jobs[0]["title"], "Software Engineer")
        self.assertEqual(saved_jobs[0]["required_skills"], ["Python", "SQL"])
        self.assertEqual(saved_jobs[0]["preferred_skills"], ["AWS"])
        self.assertEqual(updated_jobs[0]["status"], "applied")


if __name__ == "__main__":
    unittest.main()
