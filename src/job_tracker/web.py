"""Local web dashboard for the job tracker."""

import json
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

from .database import list_jobs, update_job_status
from .matcher import match_job


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "jobs.db"
PROFILE_PATH = PROJECT_ROOT / "sample_data" / "user_profile.json"

app = Flask(__name__)


def load_recommendations() -> list[dict]:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    recommendations = []

    for job in list_jobs(DATABASE_PATH):
        requirements = {
            "minimum_education": job["minimum_education"],
            "minimum_experience_years": job["minimum_experience_years"],
            "required_skills": job["required_skills"],
            "preferred_skills": job["preferred_skills"],
            "location": job["location"],
            "salary_min_hkd": job["salary_min_hkd"],
            "salary_max_hkd": job["salary_max_hkd"],
        }
        recommendations.append({**job, **match_job(requirements, profile)})

    return sorted(recommendations, key=lambda job: job["match_score"], reverse=True)


@app.get("/")
def dashboard():
    return render_template("jobs.html", jobs=load_recommendations())


@app.post("/jobs/<int:job_id>/status")
def update_status(job_id: int):
    status = request.form.get("status", "").strip()
    update_job_status(DATABASE_PATH, job_id, status)
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
