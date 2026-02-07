LINKEDIN_SEARCH_URL = "https://www.linkedin.com/flagship-web/jobs/search-results/?currentJobId=4369275428&keywords=Data%20Engineer%20I%20posted%20in%20the%20past%2024%20hours&origin=SEMANTIC_SEARCH_LANDING_PAGE"

STATE_FILE = "linkedin_state.json"  # Playwright saved session
CHECKPOINT_CSV = "jobs.csv"  # Append as we go
PROGRESS_FILE = "linkedin_jobs_progress.json"  # Page + next_job_id
OUTPUT_XLSX = "linkedin_jobs_raw.xlsx"  # Final Excel export

VIEWPORT = {"width": 1600, "height": 900}
HEADLESS = False

PROMPT = """
Please please please help me evaluate the job fitness based on job description and my profile!!!
Here is my profile:SKILLS
•	Data Engineering: Python, SQL, Databricks (PySpark, Delta Lake, Unity Catalog), ETL/ELT Pipelines, Data Warehousing, Medallion Architecture, Data Quality Validation, REST API, SSIS
•	Cloud & Infrastructure: Azure (Azure Data Factory, Databricks, Azure Functions, Azure Blob Storage), CI/CD (Azure DevOps), Workflow Orchestration
•	ML & AI Tools: MLflow, Forecasting Models, Clustering, Applied LLMs for data processing
•	Platforms & Tools: DuckDB, Git, Power BI, Monitoring & Automation
EDUCATION
B.S., Actuarial Science (Minor: Data Science, Theatre)	Middle Tennessee State University May 2024 
B.S., in Mathematics & Applied Mathematics	Ningbo University May 2024	
EXPERIENCE
BI Consultant – Data Engineer	July 2024 – December 2025 LBMC 	Nashville, TN
•	Built and maintained scalable ETL/ELT pipelines in Databricks using PySpark and Delta Lake; migrated legacy SQL Server systems to a governed lakehouse with Unity Catalog, improving maintainability and cost efficiency.
•	Architected and deployed Medallion Architecture pipelines integrating IBM iAccess, Oracle, and API-driven sources via Azure Data Factory and Azure Functions, standardizing data ingestion across the organization.
•	Developed automated data validation and quality checks to deliver accurate, reliable datasets for analytics and ML workflows, while troubleshooting pipeline failures, performance issues, and schema inconsistencies.
•	Collaborated cross-functionally with engineering, analytics, and business teams to define requirements, design schema models, and deliver consistent analytical datasets aligned with operational and reporting needs.
Intern	January 2024 – July 2024 LBMC 	Nashville, TN
•	Set up a Machine Learning pipeline to predict retail sales through Prophet and Nixtla models using PySpark, SQL improved the predicting accuracy and tracking machine the model performance using MLflow.
•	Creating multiple Power BI dashboards for healthcare client, including HR KPI and referral KPI
Actuarial Intern	May 2023 – August 2023 Selective Insurance 	Branchville, NJ
•	Applied actuarial models and SQL-based analysis for insurance pricing evaluations across multiple states.
•	Collaborated on a project to assess pricing strategies and presented findings to executives.
PROJECTS	
Data-Driven Portfolio Management – Pebble	May 2024 – June 2025
•	Built a full-stack AI tutor using Next.js, FastAPI, Supabase, Clerk, featuring user analytics and progress tracking.
•	Designed an LLM-based agent with short-term and long-term memory to deliver personalized explanations.
•	Integrated a Reddit Sentiment Pipeline using DuckDB + Ollama to extract user needs and guide feature development.
Actuarial Exams Preparation website – YosoraAI
•	Built a full-stack AI tutor using Next.js, FastAPI, Supabase, Clerk, featuring user analytics and progress tracking.
•	Designed an LLM-based agent with short-term and long-term memory to deliver personalized explanations.
•	Integrated a Reddit Sentiment Pipeline using DuckDB + Ollama to extract user needs and guide feature development.

Here is a CSV with 5 jobs:
{jobs_csv}
For each job, return a CSV columns id, fit_score, recommendation, notes. Explanation: id (the id column from the input CSV), fit_score(shoule be in range of 0.0-10.0), recommendation(anything maybe like why fit or why not a fit or improvements for my resume it's very important), notes(why you gave that score longer explanation thank you).
Output in CSV file download link and name the file as "scored_{batch_number}.csv"
"""
