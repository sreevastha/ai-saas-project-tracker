PROJECT TITLE
AI SaaS Project Tracker and KPI Dashboard

OBJECTIVE
Design a compact SaaS style platform that simulates how an enterprise manages software projects, tracks milestones, monitors risks, and reports performance KPIs in a way that is portfolio ready for recruiters or stakeholders.

SOLUTION OVERVIEW
The solution delivers a Flask based backend with a SQLite database and a Bootstrap powered interface that mirrors an internal project operations console. Users can create projects, log milestones, capture risks, monitor KPI widgets, export structured data for analytics, and request AI generated summaries. The platform also ships with scripts and guides to mirror Jira and Power BI workflows so a reviewer can see end to end delivery management capabilities without standing up those systems.

METHODOLOGY
The build followed an incremental approach. Database schemas for projects, milestones, and risks were defined first, followed by REST endpoints and automated KPI calculations. Frontend templates and JavaScript modules were layered on next to create responsive dashboards, modals, and data tables. Optional AI capabilities were integrated with a lightweight transformer to generate narrative updates, while Power BI and Jira integrations were handled through dedicated export scripts that mirror enterprise tooling. Each feature was validated with sample data to ensure the experience feels realistic for a hiring manager walkthrough.

KEY FEATURES
Project portfolio management with CRUD operations and completion tracking.
Milestone workflow including status transitions and automatic progress recalculation.
Risk register with severity grading, mitigation notes, and high risk alerts.
Interactive KPI dashboard featuring on track percentage, delay analysis, and completion metrics.
CSV exports tailored for Jira issue imports and Power BI analytics models.
AI powered project summary generator that produces executive style updates even when models are unavailable by falling back to enriched rule based narratives.

FUTURE WORK
Add role based access control so teams can collaborate with tailored permissions.
Implement real time notifications for milestone slippage or escalating risks.
Introduce burndown and velocity analytics sourced from milestone histories.
Provide connectors for live Jira or Power BI APIs to enable automatic synchronization instead of manual exports.
Expand AI skills to draft sprint reviews, stakeholder emails, or mitigation playbooks using the latest small language models.

IMPACT
This project demonstrates full stack execution, product thinking, and integration awareness in a compact portfolio friendly package. Reviewers can clone the repository, seed sample data, explore dashboards, and review integration scripts to understand how the candidate approaches enterprise software delivery.
