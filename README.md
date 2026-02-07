Job Search Workflow:

Auto-collect LinkedIn job postings and automatically score them using Claude Code — no API costs, no copy-pasting.

This project fully automates your job search workflow:
1.	Playwright Scraper
	•	Opens LinkedIn
	•	Uses your saved login session
	•	Scrapes all pages of job postings
	•	Expands “…more”
	•	Extracts title, company, description, and URL
	•	Saves results into jobs.csv
2.	Claude Code Scoring
	•	Reads your resume (inside score_jobs.claud)
	•	Reads jobs.csv
	•	Scores each job (0–10), including fit reason + flags
	•	Writes scored_jobs.csv
	•	Automatically resumes from last checkpoint
	•	No API key required (Claude Code runs locally on your laptop)

⸻

🚀 Features

✔ Automated scraping
	•	Handles multiple pages
	•	Expands hidden job descriptions
	•	Detects sponsorship red flags
	•	Saves clean structured job data

✔ AI scoring without API cost
	•	Uses Claude Code, not an API
	•	Scans your resume once
	•	Scores each job based on experience, tech stack, seniority

✔ Resume + CSV → Scored spreadsheet
	•	Create ranked job lists
	•	Filter for best matches
	•	Avoid applying to senior roles / internship spam

⸻

📂 Project Structure

Your repo should look like this:

job-search/
│
├── main.py                 # Playwright job scraper (multi-page)
├── save_state.py           # Saves LinkedIn login cookies (one-time)
├── linkedin_state.json     # Auto-generated cookie/session state
│
├── jobs.csv                # Raw scraped job data (output of main.py)
├── scored_jobs.csv         # AI-evaluated scoring file (Claude output)
│
├── score_jobs.claud        # Claude scoring instructions + your resume
├── README.md               # <== this file
│
├── .venv/                  # Python virtual environment
├── pyproject.toml
└── uv.lock


⸻

🛠 Installation

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

🔐 Step 1 — Save your LinkedIn login session

Run this once:

python save_state.py

A Chrome window opens.
Log in manually → wait until your feed loads → return to terminal → press Enter.

This saves:

linkedin_state.json

All future scrapes will load your session automatically.

⸻

🕷 Step 2 — Run the job scraper

python main.py

It will:
	•	Navigate to LinkedIn job search results
	•	Iterate pages (Next button)
	•	Collect each job card
	•	Click one-by-one
	•	Expand “…more”
	•	Extract full job description
	•	Save everything into:

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
	•	Your tech stack
	•	Your experience
	•	Your seniority
	•	Your preferences

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

🧠 Resume Updating

Whenever you gain new skills:
	1.	Open score_jobs.claud
	2.	Update your profile section
	3.	Claude will use your new skillset automatically

Highly recommended to keep this updated since it directly impacts score accuracy.

⸻

🧱 Optional Improvements

You can extend this project with:
	•	Auto-apply to high-score jobs
	•	Auto-email tracking
	•	SQL database for storing job history
	•	Notion integration
	•	Cron scheduler for daily scans

⸻

🧪 Troubleshooting

Scraper finds 0 jobs

→ LinkedIn changed selectors; update CSS selectors in main.py
→ Or: LinkedIn blocked session — run save_state.py again.

“…more” fails to click

→ Add a longer wait
→ Try alternative selectors (button[data-testid="expandable-text-button"])

Claude Code runs slowly

→ Job descriptions are long; work in batches
→ Use filters to skip irrelevant jobs first

⸻

This system lets you:
	•	Automatically collect jobs
	•	Automatically score jobs
	•	Avoid both senior roles & internships
	•	Save hours of manual review
	•	Auto-rank opportunities based on your exact background