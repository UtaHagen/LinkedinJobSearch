#!/usr/bin/env python3
"""
Score scraped LinkedIn jobs against my profile and write a new CSV.

Usage:
    python score_jobs.py                 # uses linkedin_jobs_checkpoint.csv → linkedin_jobs_scored.csv
    python score_jobs.py input.csv       # custom input file
    python score_jobs.py input.csv -o out.csv
"""

import argparse
import csv
from dataclasses import dataclass
from typing import Dict, List, Tuple
from openpyxl import Workbook
import os


# =========================
#  CONFIG: MY SKILL PROFILE
# =========================

# Core strengths – you want these to light up
PRIMARY_KEYWORDS = [
    # Cloud / Azure
    "azure",
    "azure databricks",
    "databricks",
    "azure data factory",
    "adf",
    "azure functions",
    "azure devops",
    "blob storage",
    "delta lake",
    "unity catalog",
    "git",
    "github",
    # Data engineering
    "pyspark",
    "spark",
    "etl",
    "elt",
    "data pipeline",
    "data engineer",
    "data engineering",
    "analytics engineer",
    "data platform engineer",
    "star schema",
    "dimensional modeling",
    "dimensional model",
    "data warehouse",
    "duckdb",
    "sql server",
    "parquet",
    "json",
    # BI / analytics
    "power bi",
    "dax",
    "tableau",
    "databricks sql",
]

# Secondary / nice-to-have skills
SECONDARY_KEYWORDS = [
    # AI / ML / RAG
    "llm",
    "large language model",
    "rag",
    "retrieval augmented generation",
    "langchain",
    "openai",
    "vector database",
    "pinecone",
    "qdrant",
    "chroma",
    "mlflow",
    "prophet",
    "nixtla",
    "k-means",
    "clustering",
    # Dev / web
    "python",
    "fastapi",
    "next.js",
    "supabase",
    "clerk",
    "vercel",
    "rest",
    "api",
    # Platforms
    "sql server",
    "microsoft sql server",
    "unity catalog",
]

# Stuff you have limited / learning experience with
LIMITED_EXPERIENCE_KEYWORDS = [
    "aws",
    "amazon web services",
    "s3",
    "lambda",
    "bedrock",
    "gcp",
    "google cloud",
    "bigquery",
    "kafka",
    "airflow",
    "pytorch",
    "tensorflow",
]

# Titles or phrases that indicate seniority level
SENIOR_KEYWORDS = [
    "senior",
    "sr.",
    "staff",
    "principal",
    "lead",
    "manager",
    "director",
    "architect",
    "head of",
    "vp ",
    "vice president",
]

MID_OK_KEYWORDS = [
    "data engineer",
    "analytics engineer",
    "data platform engineer",
    "data engineering",
    "software engineer data",
    "ml engineer",
]

JUNIOR_KEYWORDS = [
    "junior",
    "entry level",
    "early career",
    "associate",
    "level i",
    "level 1",
]

INTERN_KEYWORDS = [
    "intern",
    "internship",
    "co-op",
    "co op",
    "summer analyst",
    "summer associate",
    "student program",
    "campus program",
]

# Roles you like / dislike
TARGET_ROLE_KEYWORDS = [
    "data engineer",
    "data engineering",
    "analytics engineer",
    "data platform engineer",
]

AVOID_ROLE_KEYWORDS = [
    "senior manager",
    "director",
    "solutions architect",
    "enterprise architect",
]


@dataclass
class JobScore:
    score: float
    reasoning: List[str]
    red_flags: List[str]


# ==============
#  UTIL HELPERS
# ==============


def normalize(text: str) -> str:
    return (text or "").lower()


def count_keywords(text: str, keywords: List[str]) -> int:
    t = normalize(text)
    return sum(1 for kw in keywords if kw in t)


def has_any(text: str, keywords: List[str]) -> bool:
    return count_keywords(text, keywords) > 0


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


# =====================
#  SCORING LOGIC
# =====================


def score_job(row: Dict[str, str]) -> JobScore:
    """
    Take a job row (dict from CSV) and return a JobScore.
    We combine title + company + description into one blob for matching.
    """
    title = row.get("title") or row.get("job_title") or ""
    company = row.get("company") or row.get("company_name") or ""
    desc = row.get("description") or row.get("job_description") or ""
    location = row.get("location") or ""

    full_text = normalize("\n".join([title, company, location, desc]))

    score = 0.0
    reasoning: List[str] = []
    red_flags: List[str] = []

    # 0) Hard filters: internships → basically no
    if has_any(full_text, INTERN_KEYWORDS):
        red_flags.append(
            "Internship / student program (you prefer full-time data engineer roles)."
        )
        return JobScore(
            score=0.0, reasoning=["Intern / co-op role"], red_flags=red_flags
        )

    # 1) Tech stack match (up to +6)
    primary_hits = count_keywords(full_text, PRIMARY_KEYWORDS)
    secondary_hits = count_keywords(full_text, SECONDARY_KEYWORDS)

    # Primary skills are strongest – up to +4
    primary_points = clamp(primary_hits * 0.8, 0, 4)
    # Secondary skills – up to +2
    secondary_points = clamp(secondary_hits * 0.4, 0, 2)

    tech_points = primary_points + secondary_points
    score += tech_points

    if tech_points >= 5:
        reasoning.append("Strong match to your Azure + data engineering + BI stack.")
    elif tech_points >= 3:
        reasoning.append("Good partial match to your technical stack.")
    elif tech_points > 0:
        reasoning.append("Some overlap with your skills, but not a strong core match.")
    else:
        reasoning.append("Very little overlap with your core technical skills.")

    # 2) Role alignment (up to +3, or negative if bad)
    role_points = 0.0

    if has_any(title, TARGET_ROLE_KEYWORDS) or has_any(desc, TARGET_ROLE_KEYWORDS):
        role_points += 2.0
        reasoning.append("Role looks like data/analytics engineering (good fit).")

    if has_any(title, AVOID_ROLE_KEYWORDS):
        role_points -= 2.0
        red_flags.append("Title suggests high-level managerial/architect role.")

    score += role_points

    # 3) Seniority alignment (from -3 to +2)
    seniority_points = 0.0

    if has_any(title, SENIOR_KEYWORDS):
        seniority_points -= 2.5
        red_flags.append("Title suggests senior/staff/lead level (often 5+ years).")
    elif has_any(title, JUNIOR_KEYWORDS):
        seniority_points += 1.0
        reasoning.append("Explicitly junior / entry-level friendly.")
    elif has_any(title, MID_OK_KEYWORDS):
        seniority_points += 1.5
        reasoning.append("Title suggests standard data engineer role (likely 2–4 YOE).")

    score += seniority_points

    # 4) Cloud alignment (+1.5 if Azure, +0.5 if other clouds only)
    cloud_points = 0.0
    if "azure" in full_text:
        cloud_points += 1.5
        reasoning.append("Specifically mentions Azure (your strongest cloud).")
    elif "aws" in full_text or "gcp" in full_text or "google cloud" in full_text:
        cloud_points += 0.5
        reasoning.append("Mentions AWS/GCP – your Azure skills should transfer.")

    score += cloud_points

    # 5) Light penalty if dominated by tools you have limited experience in
    limited_hits = count_keywords(full_text, LIMITED_EXPERIENCE_KEYWORDS)
    if limited_hits >= 4:
        score -= 1.5
        red_flags.append(
            "Heavily focused on tools where you have limited experience (AWS/GCP/Kafka/etc.)."
        )
    elif limited_hits >= 2:
        score -= 0.5
        red_flags.append("Some focus on tools where you have limited experience.")

    # 6) Clamp to 0–10
    final_score = clamp(round(score, 2), 0.0, 10.0)

    return JobScore(score=final_score, reasoning=reasoning, red_flags=red_flags)


# =====================
#  CSV I/O + CLI
# =====================


def read_jobs(path: str) -> Tuple[List[Dict[str, str]], List[str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    return rows, fieldnames


def write_scored_jobs(
    path: str, rows: List[Dict[str, str]], base_fields: List[str]
) -> None:
    # ensure new columns at the end
    extra_cols = ["fit_score", "score_reasoning", "red_flags"]
    fieldnames = base_fields.copy()
    for c in extra_cols:
        if c not in fieldnames:
            fieldnames.append(c)

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


# Write results to Excel using openpyxl
def write_excel(path: str, rows: list, fieldnames: list) -> None:
    wb = Workbook()
    ws = wb.active
    ws.append(fieldnames)
    for row in rows:
        ws.append([row.get(field, "") for field in fieldnames])
    wb.save(path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Score LinkedIn jobs in a CSV against my data engineer profile."
    )
    parser.add_argument(
        "input_csv",
        nargs="?",
        default="jobs.csv",
        help="Input CSV with scraped jobs (default: jobs.csv)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="jobs_scored.csv",
        help="Output CSV path (default: jobs_scored.csv)",
    )

    args = parser.parse_args()

    print(f"📥 Reading jobs from: {args.input_csv}")
    jobs, base_fields = read_jobs(args.input_csv)
    print(f"   Found {len(jobs)} rows")

    scored_rows: List[Dict[str, str]] = []

    for idx, row in enumerate(jobs, start=1):
        js = score_job(row)

        row["fit_score"] = js.score
        row["score_reasoning"] = " ".join(js.reasoning).strip()
        row["red_flags"] = " | ".join(js.red_flags).strip()

        scored_rows.append(row)

        if idx % 25 == 0 or idx == len(jobs):
            print(f"   Scored {idx}/{len(jobs)} jobs…")

    print(f"💾 Writing scored jobs to: {args.output}")
    write_scored_jobs(args.output, scored_rows, base_fields)
    # Also write to Excel
    excel_path = os.path.splitext(args.output)[0] + ".xlsx"
    write_excel(excel_path, scored_rows, base_fields)
    print("✅ Done.")


if __name__ == "__main__":
    main()
