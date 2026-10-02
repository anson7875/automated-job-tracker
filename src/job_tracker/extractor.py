"""Extract basic requirements from a job description."""

import re


EDUCATION_PATTERNS = (
    (r"\b(ph\.?d\.?|doctorate|doctoral)\b", "PhD"),
    (r"\b(master'?s|m\.?sc\.?|m\.?eng\.?|mba)\b", "Master's degree"),
    (r"\b(bachelor'?s|b\.?sc\.?|b\.?eng\.?)\b", "Bachelor's degree"),
    (r"\b(diploma|associate'?s degree)\b", "Diploma"),
)

EXPERIENCE_PATTERN = re.compile(
    r"\b(?:at\s+least|minimum(?:\s+of)?|over)?\s*"
    r"(\d+)\s*(?:\+|-\s*\d+)?\s*years?"
    r"(?:\s+of)?\s+(?:relevant|professional|commercial|working)?\s*experience\b",
    re.IGNORECASE,
)

SKILL_PATTERNS = (
    ("Python", r"\bpython\b"),
    ("SQL", r"\bsql\b"),
    ("REST APIs", r"\brest\s+apis?\b"),
    ("AWS", r"\baws\b|amazon web services"),
    ("Docker", r"\bdocker\b"),
    ("PostgreSQL", r"\bpostgres(?:ql)?\b"),
    ("Git", r"\bgit\b"),
)

PREFERRED_MARKERS = ("preferred", "nice to have", "bonus", "advantage")


def extract_skills(text: str) -> tuple[list[str], list[str]]:
    """Return known skills split into required and preferred groups."""
    required_skills = []
    preferred_skills = []

    for sentence in re.split(r"[.!?\n]+", text.lower()):
        is_preferred = any(marker in sentence for marker in PREFERRED_MARKERS)
        matching_skills = preferred_skills if is_preferred else required_skills

        for skill, pattern in SKILL_PATTERNS:
            if re.search(pattern, sentence) and skill not in matching_skills:
                matching_skills.append(skill)

    preferred_skills = [
        skill for skill in preferred_skills if skill not in required_skills
    ]
    return required_skills, preferred_skills


def extract_requirements(text: str) -> dict:
    """Extract education, experience, and recognized skills from a job description."""
    normalized_text = text.lower()

    education = None
    for pattern, label in EDUCATION_PATTERNS:
        if re.search(pattern, normalized_text):
            education = label
            break

    experience_match = EXPERIENCE_PATTERN.search(normalized_text)
    minimum_experience_years = (
        int(experience_match.group(1)) if experience_match else None
    )
    required_skills, preferred_skills = extract_skills(text)

    return {
        "minimum_education": education,
        "minimum_experience_years": minimum_experience_years,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
    }
