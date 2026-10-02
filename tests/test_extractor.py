from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from job_tracker.extractor import extract_requirements


class ExtractRequirementsTests(unittest.TestCase):
    def test_extracts_requirements_from_sample_job_description(self):
        job_description = (PROJECT_ROOT / "sample_data" / "sample_data.txt").read_text(
            encoding="utf-8"
        )

        requirements = extract_requirements(job_description)

        print("\nExtracted requirements:")
        for field, value in requirements.items():
            print(f"  {field}: {value}")

        self.assertEqual(requirements["minimum_education"], "Bachelor's degree")
        self.assertEqual(requirements["minimum_experience_years"], 2)
        self.assertEqual(requirements["required_skills"], ["Python", "SQL", "REST APIs"])
        self.assertEqual(requirements["preferred_skills"], ["AWS"])

    def test_returns_none_when_a_requirement_is_not_mentioned(self):
        requirements = extract_requirements("We are looking for a curious Python developer.")

        self.assertIsNone(requirements["minimum_education"])
        self.assertIsNone(requirements["minimum_experience_years"])
        self.assertEqual(requirements["required_skills"], ["Python"])
        self.assertEqual(requirements["preferred_skills"], [])


if __name__ == "__main__":
    unittest.main()
