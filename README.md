# 🔎 Automated LinkedIn Job Search

This project fully automates your job search workflow:

1. **Playwright Scraper**  
   Opens LinkedIn → Uses your saved login session → Scrapes all job postings →  
   Expands "...more" → Extracts title, company, description, and URL →  
   Saves results into `jobs.csv`

2. **Claude Code Scoring**  
   Reads your resume (`score_jobs.claud`) → Reads `jobs.csv` →  
   Scores each job (0–10) with reasoning + flags → Writes `scored_jobs.csv`  
   *No API key required — Claude Code runs locally.*

---

## 🚀 Features

### ✔ Automated Scraping
- Handles pagination  
- Expands hidden descriptions  
- Detects sponsorship red flags  
- Saves clean structured job data  

### ✔ AI Scoring (Free, Local, Fully Automated)
- Uses **Claude Code**, not an API  
- Reads your resume once  
- Scores jobs based on:  
  - Tech stack  
  - Role fit  
  - Seniority  
  - Cloud tools  
  - AI/ML experience  
- Generates:  
  - `fit_score`  
  - `reasoning`  
  - `red_flags`  
  - Recommended action (Apply / Skip)

### ✔ Resume + CSV → Scored Spreadsheet
- Clean Excel or CSV output  
- Rank jobs  
- Focus on best-fit roles  
- Avoid senior-level & sponsorship-blocked roles  

---

## 📁 Project Structure

```text
job-search/
│
├── main.py               # Playwright job scraper (multi-page)
├── save_state.py         # Saves LinkedIn login cookies (one-time)
├── linkedin_state.json   # Auto-generated cookie/session state
│
├── jobs.csv              # Raw scraped job data (output of main.py)
├── scored_jobs.csv       # AI-evaluated scoring file (Claude output)
│
├── score_jobs.claud      # Claude scoring instructions + your resume
├── score_jobs.py         # Local scoring (Python-only)
│
├── scoring_skills.py     # Keyword definitions used in scoring
│
├── README.md             # <— this file
├── pyproject.toml        
├── uv.lock
└── .venv/                # Python virtual environment


⸻

## 🛠 Installation

1. Clone the project

git clone <your-repo-url>
cd job-search

2. Install dependencies

Uses uv or pip — either works.

uv sync

or:

pip install -r requirements.txt

3. Install Playwright browsers

playwright install


⸻

## 🔐 Step 1 — Save your LinkedIn login session

Run this once:

python save_state.py

A Chrome window opens.
Log in manually → wait until your feed loads → return to terminal → press Enter.

This saves:

linkedin_state.json

All future scrapes will load your session automatically.

⸻

## 🕷 Step 2 — Run the job scraper

python main.py

It will:
	-	Navigate to LinkedIn job search results
	-	Iterate pages (Next button)
	-	Collect each job card
	-	Click one-by-one
	-	Expand “…more”
	-	Extract full job description
	-	Save everything into:

jobs.csv

Example CSV structure

job_id,title,company,location,description,linkedin_url
1,Data Engineer,Cisco,Remote,"full jd text...",https://linkedin.com/jobs/view/...


⸻

🤖 Step 3 — Score your jobs using Claude Code (FREE)

1. Install Claude Code

(If you haven’t already)
https://docs.anthropic.com/claude-code

2. Place your resume inside score_jobs.claud

Your scoring prompt already contains:
	-	Your tech stack
	-	Your experience
	-	Your seniority
	-	Your preferences

3. Run scoring

Use the job-scorer skill to score my jobs.csv

Basic usage:

claude code score_jobs.claud jobs.csv

Save output:

claude code score_jobs.claud jobs.csv --output scored_jobs.csv

Filter top matches:

claude code score_jobs.claud jobs.csv --filter "score >= 7" --output top_jobs.csv


⸻

⭐ Scoring Breakdown

Claude assigns:

Column	Meaning
fit_score	0–10 compatibility rating
score_reasoning	Why it scored that way
red_flags	Seniority mismatch, 5+ years required, internship, etc
recommendation	Apply / Consider / Skip

Example:

job_id,title,company,fit_score,score_reasoning,recommendation
1,Jr Data Engineer,CAA,8,"Azure + Python match; perfect seniority",Apply
3,Senior Data Engineer,Meta,2,"Requires 7+ years exp",Skip


⸻

## 🧠 Resume Updating

Whenever you gain new skills:
	1.	Open score_jobs.claud
	2.	Update your profile section
	3.	Claude will use your new skillset automatically

Highly recommended to keep this updated since it directly impacts score accuracy.

⸻

This system lets you:
	-	Automatically collect jobs
	-	Automatically score jobs
	-	Avoid both senior roles & internships
	-	Save hours of manual review
	-	Auto-rank opportunities based on your exact background
