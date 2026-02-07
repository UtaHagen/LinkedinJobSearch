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
```

---

## 🛠 Installation

### 1. Clone the project

```bash
git clone <your-repo-url>
cd job-search
```

### 2. Install dependencies

Use **uv** or **pip** — both work.

```bash
uv sync
```

or:

```bash
pip install -r requirements.txt
```

### 3. Install Playwright browsers

```bash
playwright install
```

---

## 🔐 Step 1 — Save your LinkedIn login session

Run this *once*:

```bash
python save_state.py
```

A Chrome window will open.

1. Log in to LinkedIn manually  
2. Wait for your feed to load  
3. Return to the terminal  
4. Press **Enter**  

This generates:

```
linkedin_state.json
```

All future scrapes will automatically load your saved login session.

---

## 🕷 Step 2 — Run the job scraper

```bash
python main.py
```

This script will:

- Open LinkedIn job search
- Iterate through pages (Next → Next → Next…)
- Collect all job cards
- Click each job
- Expand “**…more**” to reveal full description
- Extract:
  - Title  
  - Company  
  - Location  
  - Description  
  - URL  
- Save everything into:

```
jobs.csv
```

### Example CSV structure

```text
job_id,title,company,location,description,linkedin_url
1,Data Engineer,Cisco,Remote,"full jd text...",https://linkedin.com/jobs/view/...
```

---

## 🤖 Step 3 — Score your jobs using Claude Code (FREE)

### 1. Install Claude Code
If not installed:
https://docs.anthropic.com/claude-code

### 2. Put your resume inside `score_jobs.claud`
Your prompt already includes:

- Your tech stack  
- Your experience  
- Your seniority  
- Your job preferences  

Simply update that section as needed.

### 3. Run scoring

#### Basic scoring:
```bash
claude code score_jobs.claud jobs.csv
```

#### Save output:
```bash
claude code score_jobs.claud jobs.csv --output scored_jobs.csv
```

#### Filter top matches:
```bash
claude code score_jobs.claud jobs.csv --filter "score >= 7" --output top_jobs.csv
```

---

## ⭐ Scoring Breakdown

Claude outputs:

| Column           | Meaning                                       |
|------------------|-----------------------------------------------|
| `fit_score`      | 0–10 compatibility rating                     |
| `score_reasoning`| Why it scored that way                        |
| `red_flags`      | Seniority mismatch, 5+ YOE, internship, etc   |
| `recommendation` | Apply / Consider / Skip                       |

### Example Output

```text
job_id,title,company,fit_score,score_reasoning,recommendation
1,Jr Data Engineer,CAA,8,"Azure + Python match; perfect seniority",Apply
3,Senior Data Engineer,Meta,2,"Requires 7+ years experience",Skip
```

---

## 🧠 Resume Updating

Whenever your skillset changes:

1. Open `score_jobs.claud`
2. Update the **My Profile** section  
3. Claude will score future job descriptions based on your new skills automatically

Keeping this updated improves scoring accuracy significantly.

---

## 🎯 What This System Gives You

- Automated job scraping  
- Automated job scoring  
- Avoids senior roles + internships  
- Saves hours of manual review  
- Ranks roles automatically based on:  
  - Your tech stack  
  - Your seniority  
  - Your experience  
  - Your preferences  

---
