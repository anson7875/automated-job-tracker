import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from job_tracker.csv_importer import read_jobs_from_csv


class CsvImporterTests(unittest.TestCase):
    def test_reads_job_records(self):
        csv_content = (
            "title,company,url,description\n"
            'Backend Developer,Example Company,https://example.com/1,"Python and Docker"\n'
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "jobs.csv"
            csv_path.write_text(csv_content, encoding="utf-8")

            jobs = read_jobs_from_csv(csv_path)

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["title"], "Backend Developer")
        self.assertEqual(jobs[0]["url"], "https://example.com/1")


if __name__ == "__main__":
    unittest.main()
