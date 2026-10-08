import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from job_tracker.jobsdb_collector import JobPageParser, parse_job_posting


class JobsDBCollectorTests(unittest.TestCase):
    def test_finds_job_links(self):
        parser = JobPageParser("https://hk.jobsdb.com/search")
        parser.feed('<a href="/job/backend-developer-123">Backend</a>')

        self.assertEqual(
            parser.job_links,
            {"https://hk.jobsdb.com/job/backend-developer-123"},
        )

    def test_parses_job_posting_json_ld(self):
        blocks = [
            '{"@type":"JobPosting","title":"IT Support Specialist",'
            '"url":"https://example.com/job/1",'
            '"hiringOrganization":{"name":"Example Company"},'
            '"jobLocation":{"address":{"addressLocality":"Hong Kong"}},'
            '"description":"Diploma required."}'
        ]

        job = parse_job_posting(blocks)

        self.assertEqual(job["title"], "IT Support Specialist")
        self.assertEqual(job["company"], "Example Company")
        self.assertEqual(job["location"], "Hong Kong")


if __name__ == "__main__":
    unittest.main()
