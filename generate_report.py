from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from pathlib import Path


def add_image(flow, path, max_width=500):
    p = Path(path)
    if not p.exists():
        return
    img = Image(str(p))
    # scale by width
    w, h = img.wrap(0, 0)
    if w > max_width:
        scale = max_width / w
        img._width = w * scale
        img._height = h * scale
    flow.append(img)
    flow.append(Spacer(1, 0.2 * inch))


def main():
    charts_dir = Path("charts")
    out = Path("ProjectReport.pdf")

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Body", fontName="Helvetica", fontSize=10.5, leading=14))
    styles.add(ParagraphStyle(name="Title2", fontName="Helvetica-Bold", fontSize=14, spaceAfter=8))

    story = []
    story.append(Paragraph("AI SaaS Project Tracker and KPI Dashboard", styles["Title2"]))
    story.append(Paragraph(
        "Objective: Build a compact platform to simulate enterprise software delivery tracking, including projects, milestones, risks, KPIs, data exports, and narrative summaries.",
        styles["Body"],
    ))
    story.append(Spacer(1, 0.25 * inch))

    story.append(Paragraph("Tech Stack", styles["Title2"]))
    story.append(Paragraph(
        "Backend Python Flask. Database SQLite with SQLAlchemy. Frontend HTML Bootstrap JavaScript. Charts Plotly Matplotlib Seaborn. AI Hugging Face transformers with google flan t5 small optional. Data Integration CSV to Jira and Power BI.",
        styles["Body"],
    ))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Key Features", styles["Title2"]))
    story.append(Paragraph(
        "Project management and progress tracking. Milestone workflow and auto recalculation. Risk register with severity. KPI dashboard. Power BI and Jira exports. AI executive summaries with robust fallback.",
        styles["Body"],
    ))
    story.append(Spacer(1, 0.25 * inch))

    story.append(Paragraph("KPI Visualizations", styles["Title2"]))
    for name in [
        "status_distribution.png",
        "completion_by_owner.png",
        "status_by_owner.png",
        "risk_severity.png",
        "completion_vs_days_remaining.png",
        "milestones_completed_over_time.png",
        "risk_heatmap.png",
    ]:
        add_image(story, charts_dir / name, max_width=460)

    story.append(Paragraph("Notes", styles["Title2"]))
    story.append(Paragraph(
        "All charts are generated from the latest Power BI exports under docs. Use python kpi.py to refresh visuals.",
        styles["Body"],
    ))

    doc = SimpleDocTemplate(str(out), pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    doc.build(story)
    print(f"Saved {out.resolve()}")


if __name__ == "__main__":
    main()



