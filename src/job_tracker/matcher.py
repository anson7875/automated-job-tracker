"""Rule-based matching between a user profile and extracted job requirements."""


EDUCATION_LEVELS = {
    "diploma": 1,
    "bachelor's degree": 2,
    "master's degree": 3,
    "phd": 4,
}


def match_job(requirements: dict, profile: dict) -> dict:
    """Return a transparent match score and the reasons behind it."""
    user_education = (profile.get("education") or "").lower()
    required_education = (requirements.get("minimum_education") or "").lower()
    education_score = 0
    if required_education is None:
        education_score = 1
    elif EDUCATION_LEVELS.get(user_education, 0) >= EDUCATION_LEVELS.get(
        required_education, 99
    ):
        education_score = 1

    user_experience = profile.get("experience_years", 0)
    required_experience = requirements.get("minimum_experience_years")
    experience_score = 1 if required_experience is None or user_experience >= required_experience else 0

    user_skills = {skill.lower() for skill in profile.get("skills", [])}
    required_skills = requirements.get("required_skills", [])
    preferred_skills = requirements.get("preferred_skills", [])
    matched_required = [skill for skill in required_skills if skill.lower() in user_skills]
    missing_required = [skill for skill in required_skills if skill.lower() not in user_skills]
    matched_preferred = [skill for skill in preferred_skills if skill.lower() in user_skills]

    required_skill_score = (
        len(matched_required) / len(required_skills) if required_skills else 1
    )
    preferred_skill_score = (
        len(matched_preferred) / len(preferred_skills) if preferred_skills else 1
    )

    profile_min_salary = profile.get("salary_min_hkd")
    profile_max_salary = profile.get("salary_max_hkd")
    job_min_salary = requirements.get("salary_min_hkd")
    job_max_salary = requirements.get("salary_max_hkd")
    salary_match = (
        True
        if not all(value is not None for value in (profile_min_salary, profile_max_salary, job_min_salary, job_max_salary))
        else job_max_salary >= profile_min_salary and job_min_salary <= profile_max_salary
    )

    preferred_locations = {location.lower() for location in profile.get("preferred_locations", [])}
    job_location = (requirements.get("location") or "").lower()
    location_match = (
        True
        if not preferred_locations or not job_location
        else any(location in job_location for location in preferred_locations)
    )

    score = round(
        (education_score * 20)
        + (experience_score * 20)
        + (required_skill_score * 35)
        + (preferred_skill_score * 10)
        + (int(salary_match) * 10)
        + (int(location_match) * 5)
    )

    warnings = []
    if not education_score:
        warnings.append("Education requirement is not met")
    if not experience_score:
        warnings.append("Experience requirement is not met")
    if missing_required:
        warnings.append("Required skills are missing")

    return {
        "match_score": score,
        "matched_required_skills": matched_required,
        "missing_required_skills": missing_required,
        "matched_preferred_skills": matched_preferred,
        "salary_match": salary_match,
        "location_match": location_match,
        "warnings": warnings,
    }
