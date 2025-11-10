# AI SaaS Project Tracker and KPI Dashboard

A compact platform that simulates enterprise software delivery tracking, analytics, and AI-driven executive summaries. Create projects, log milestones and risks, compute KPIs, export data for Power BI / Jira, and generate narrative stakeholder updates.

## Table of contents
- Key highlights
- Quick start
- Exports & analysis
- Folder structure
- AI summaries
- Security & roadmap
- License & author

## Key highlights
- Full project + milestone CRUD with automatic progress recalculation
- Risk register with severity, mitigation plans and heatmap visualizations
- KPI dashboard: On-Track %, Average Delay, High-Risk Count, Completion rates
- Exports: Power BI-ready normalized CSVs and Jira-compatible import CSVs
- AI summaries: local Hugging Face model (google/flan-t5-small) with a rule-based fallback

## Quick start
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS / Linux
   .venv\Scripts\activate   # Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Install charting libs:
   ```bash
   pip install matplotlib seaborn
   ```
4. Initialize DB and seed sample data:
   ```bash
   python init_db.py
   python sample_data.py
   ```
5. Run the app:
   ```bash
   python app.py
   ```
Open http://localhost:5000 in your browser.

## Exports & analysis
- Power BI CSVs: `python powerbi_csv_export.py` → saved to `/docs`
- Jira CSV: `python jira_csv_export.py` (Jira import columns: Work Item ID, Work Type, Parent ID, Summary/Description)
- Offline KPI charts & animations: `python kpi.py` → saved to `/charts`

## Folder structure (overview)
AI-SaaS-Tracker/
├── app.py                     # Flask server and API endpoints
├── models.py                  # SQLAlchemy ORM models
├── static/                    # CSS, JS, frontend assets
├── templates/                 # HTML templates
├── docs/                      # Power BI CSV exports
├── charts/                    # Offline KPI visualizations
├── requirements.txt
└── ProjectReport.pdf          # Full technical report with visuals

## AI summaries
- AI-Model Mode: uses `google/flan-t5-small` (requires `transformers` and `torch`) to generate executive-style updates per project.
- Rule-Based Mode: deterministic fallback when models are unavailable — ensures summaries can be produced in restricted environments.

## Security & roadmap (brief)
Planned improvements:
- Role-based access control and multi-user support
- Live API connectors for Jira and Power BI
- Real-time alerts for overdue milestones and high-risk items
- Enhanced AI summarization and automated performance analytics

## License & author
All content © 2025 Sreevastha Thotamsetty — for educational and demonstration purposes.

Author: Sreevastha Thotamsetty (GitHub: sreevastha, Hyderabad, India)