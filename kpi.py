import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

sns.set_theme(style="whitegrid")

# Source files
PROJECTS_FILE = "powerbi_projects_20251110_123837.csv"
MILESTONES_FILE = "powerbi_milestones_20251110_123837.csv"
RISKS_FILE = "powerbi_risks_20251110_123837.csv"

projects = pd.read_csv(PROJECTS_FILE)
milestones = pd.read_csv(MILESTONES_FILE)
risks = pd.read_csv(RISKS_FILE)

# Parse numeric/datetime columns
projects["Completion Percentage"] = pd.to_numeric(projects["Completion Percentage"], errors="coerce")
projects["Days Remaining"] = pd.to_numeric(projects["Days Remaining"], errors="coerce")
projects["Start Date"] = pd.to_datetime(projects["Start Date"], errors="coerce")
projects["Deadline"] = pd.to_datetime(projects["Deadline"], errors="coerce")

milestones["Target Date"] = pd.to_datetime(milestones["Target Date"], errors="coerce")
milestones["Completion Date"] = pd.to_datetime(milestones["Completion Date"], errors="coerce")

risks["Severity Level"] = pd.to_numeric(risks["Severity Level"], errors="coerce")

# KPI summary
total_projects = len(projects)
completed = (projects["Status"].str.upper() == "COMPLETED").sum()
avg_progress = projects["Completion Percentage"].mean()
total_risks = len(risks)
open_high_risks = (
    (risks["Severity"].str.upper() == "HIGH") &
    (risks["Status"].str.upper() != "CLOSED")
).sum()

print(f"Total Projects: {total_projects}")
print(f"Completed Projects: {completed}")
print(f"Average Completion: {avg_progress:.1f}%")
print(f"Total Risks Logged: {total_risks}")
print(f"Open High-Severity Risks: {open_high_risks}")

# Output folder for charts
output_dir = Path("charts")
output_dir.mkdir(exist_ok=True)

# 1. Project status distribution (pie)
projects["Status"].value_counts().plot.pie(autopct="%1.0f%%", ylabel="")
plt.title("Project Status Distribution")
plt.tight_layout()
plt.savefig(output_dir / "status_distribution.png")
plt.close()

# 2. Average completion by owner (bar)
(
    projects.groupby("Owner")["Completion Percentage"]
    .mean()
    .sort_values()
    .plot.barh(color="#3B82F6")
)
plt.title("Average Completion by Owner")
plt.xlabel("Completion (%)")
plt.tight_layout()
plt.savefig(output_dir / "completion_by_owner.png")
plt.close()

# 3. Project status by owner (stacked bar)
status_owner = (
    projects.pivot_table(index="Owner", columns="Status",
                         values="Project ID", aggfunc="count")
    .fillna(0)
)
status_owner.plot(kind="bar", stacked=True, colormap="tab20c")
plt.title("Project Status by Owner")
plt.ylabel("Project Count")
plt.tight_layout()
plt.savefig(output_dir / "status_by_owner.png")
plt.close()

# 4. Risk severity distribution (bar)
risks["Severity"].value_counts().reindex(["High", "Medium", "Low"]).plot.bar(
    color=["#DC2626", "#F59E0B", "#10B981"]
)
plt.title("Risk Severity Distribution")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(output_dir / "risk_severity.png")
plt.close()

# 5. Completion vs days remaining (scatter)
sns.scatterplot(
    data=projects,
    x="Days Remaining",
    y="Completion Percentage",
    hue="Is On Track",
    palette={"Yes": "#10B981", "No": "#F97316"},
    style="Status"
)
plt.title("Completion vs Days Remaining")
plt.xlabel("Days Remaining")
plt.ylabel("Completion (%)")
plt.tight_layout()
plt.savefig(output_dir / "completion_vs_days_remaining.png")
plt.close()

# 6. Milestones completed over time (line)
completed_milestones = milestones.dropna(subset=["Completion Date"])
if not completed_milestones.empty:
    monthly_counts = (
        completed_milestones
        .groupby(completed_milestones["Completion Date"].dt.to_period("M"))
        .size()
        .rename("Completed Milestones")
        .to_timestamp()
    )
    monthly_counts.plot(marker="o", color="#6366F1")
    plt.title("Milestones Completed Per Month")
    plt.xlabel("Month")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(output_dir / "milestones_completed_over_time.png")
    plt.close()

# 7. Risk heatmap by project and severity
if not risks.empty:
    risk_matrix = (
        risks.pivot_table(index="Project Name", columns="Severity",
                          values="Risk ID", aggfunc="count")
        .fillna(0)
        .reindex(columns=["High", "Medium", "Low"])
    )
    plt.figure(figsize=(8, max(4, 0.3 * len(risk_matrix))))
    sns.heatmap(risk_matrix, annot=True, fmt=".0f", cmap="YlOrRd")
    plt.title("Risk Count by Project and Severity")
    plt.xlabel("Severity")
    plt.ylabel("Project")
    plt.tight_layout()
    plt.savefig(output_dir / "risk_heatmap.png")
    plt.close()

print("Charts saved to:", output_dir.resolve())