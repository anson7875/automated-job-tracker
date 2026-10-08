import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from job_tracker.matcher import match_job


class MatcherTests(unittest.TestCase):
    def test_matches_user_profile_against_job_requirements(self):
        profile = {
            "education": "Bachelor's degree",
            "experience_years": 0,
            "skills": ["Python", "Java", "MySQL"],
            "salary_min_hkd": 15000,
            "salary_max_hkd": 24000,
            "preferred_locations": ["Hong Kong"],
        }
        requirements = {
            "minimum_education": "Bachelor's degree",
            "minimum_experience_years": 0,
            "required_skills": ["Python", "MySQL"],
            "preferred_skills": ["Java"],
            "salary_min_hkd": 18000,
            "salary_max_hkd": 22000,
            "location": "Hong Kong",
        }

        result = match_job(requirements, profile)

        self.assertEqual(result["match_score"], 100)
        self.assertEqual(result["missing_required_skills"], [])
        self.assertEqual(result["matched_preferred_skills"], ["Java"])

    def test_reports_missing_skill_and_experience(self):
        result = match_job(
            {
                "minimum_education": "Bachelor's degree",
                "minimum_experience_years": 2,
                "required_skills": ["Python", "Docker"],
                "preferred_skills": [],
            },
            {
                "education": "Bachelor's degree",
                "experience_years": 0,
                "skills": ["Python"],
            },
        )

        self.assertEqual(result["missing_required_skills"], ["Docker"])
        self.assertIn("Experience requirement is not met", result["warnings"])


if __name__ == "__main__":
    unittest.main()
