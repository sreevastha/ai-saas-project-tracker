PROJECT TITLE
AI SaaS Project Tracker and KPI Dashboard

OBJECTIVE
Build a compact but realistic platform to simulate enterprise software delivery tracking. The app allows creating projects, logging milestones and risks, computing KPIs, exporting data for analytics, and producing narrative summaries suitable for stakeholder updates.

TECH STACK
Backend Python Flask for API and server pages
Database SQLite with SQLAlchemy ORM
Frontend HTML Bootstrap JavaScript
Charts Plotly for in app visuals Matplotlib Seaborn for offline charts
AI Summaries Hugging Face transformers with google flan t5 small optional and a robust rule based fallback
Data Integration CSV export for Jira import and Power BI analytics
Utilities Pandas Dateutil Requests

FEATURES
Project management create read update delete with deadlines owners and completion tracking
Milestone workflow status pending in progress completed delayed with automatic project progress recalculation
Risk register name severity low medium high mitigation plan and status open mitigated closed
KPI dashboard projects on track percentage average delay percentage high risk count average completion milestone completion
Exports Power BI friendly normalized tables projects milestones risks and Jira import ready CSV with work item id parent id and work type
AI summary executive style project update generated on demand with or without installed models

HOW TO RUN
Create virtual environment optional
python -m venv .venv
.venv\\Scripts\\activate on Windows

Install dependencies
pip install -r requirements.txt
If you plan to run kpi charts also install matplotlib and seaborn
pip install matplotlib seaborn

Initialize database and sample data
python init_db.py
python sample_data.py

Start the app
python app.py
Then open http colon slash slash localhost colon 5000

POWER BI AND OFFLINE KPI VISUALS
Export normalized CSVs
python powerbi_csv_export.py
Files are saved under docs folder

Generate presentation ready charts and an animated gif
python kpi.py
Charts are saved under charts folder

JIRA INTEGRATION VIA CSV
Generate Jira import CSV
python jira_csv_export.py
In Jira use Import issues from CSV and map columns including Work Item ID Work Type and Parent ID

AI SUMMARIES
The app provides an AI Summary tab inside the project details page
By default it uses a lightweight model google flan t5 small when transformers and torch are installed
Without models a rule based narrative summary is produced automatically

FOLDER STRUCTURE HIGHLIGHTS
app.py server and API endpoints
models.py database models
static css and js frontend assets
templates html templates
docs source CSV files for Power BI
charts generated images and animated gif for KPIs

SECURITY AND EXTENSIONS ROADMAP
Role based access control for multi user teams
Real time notifications for overdue milestones and high risks
Live API connectors for Jira and Power BI to automate synchronization
Richer AI workflows sprint review drafts and stakeholder briefings

AUTHOR NOTES
This repository demonstrates full stack delivery thinking data analytics awareness and pragmatic integrations that recruiters and hiring teams can review quickly. Clone run seed explore export and review the visuals and summaries.



