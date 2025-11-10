"""
Power BI CSV Export Script
Exports Project Tracker data to Power BI-friendly CSV format
Creates separate CSV files for Projects, Milestones, and Risks (best practice for Power BI)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Project, Milestone, Risk, ProjectStatus, MilestoneStatus, RiskSeverity
from datetime import datetime
import csv
import os

# Database setup
engine = create_engine('sqlite:///projecttracker.db', echo=False)
Session = sessionmaker(bind=engine)

def export_to_powerbi_csv():
    """
    Export all projects, milestones, and risks to Power BI-friendly CSV format
    Creates separate CSV files for each entity type (best practice for Power BI)
    """
    session = Session()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        projects = session.query(Project).all()
        milestones = session.query(Milestone).all()
        risks = session.query(Risk).all()
        
        # Export Projects Table
        projects_filename = f'powerbi_projects_{timestamp}.csv'
        with open(projects_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Projects table headers
            headers = [
                'Project ID',
                'Project Name',
                'Owner',
                'Description',
                'Status',
                'Start Date',
                'Deadline',
                'Completion Percentage',
                'Days Remaining',
                'Is Overdue',
                'Is On Track',
                'Created At',
                'Updated At'
            ]
            writer.writerow(headers)
            
            now = datetime.now(datetime.UTC) if hasattr(datetime, 'UTC') else datetime.utcnow()
            for project in projects:
                days_remaining = (project.deadline - now).days
                is_overdue = project.deadline < now and project.status != ProjectStatus.COMPLETED
                is_on_track = not is_overdue or project.status == ProjectStatus.COMPLETED
                
                row = [
                    project.id,
                    project.name,
                    project.owner,
                    project.description or '',
                    project.status.value,
                    project.start_date.strftime('%Y-%m-%d'),
                    project.deadline.strftime('%Y-%m-%d'),
                    project.completion_percentage,
                    days_remaining,
                    'Yes' if is_overdue else 'No',
                    'Yes' if is_on_track else 'No',
                    project.created_at.strftime('%Y-%m-%d %H:%M:%S') if project.created_at else '',
                    project.updated_at.strftime('%Y-%m-%d %H:%M:%S') if project.updated_at else ''
                ]
                writer.writerow(row)
        
        # Export Milestones Table
        milestones_filename = f'powerbi_milestones_{timestamp}.csv'
        with open(milestones_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Milestones table headers
            headers = [
                'Milestone ID',
                'Project ID',
                'Project Name',
                'Milestone Name',
                'Description',
                'Target Date',
                'Completion Date',
                'Status',
                'Is Overdue',
                'Is Completed',
                'Days Until Target',
                'Days Past Target',
                'Created At',
                'Updated At'
            ]
            writer.writerow(headers)
            
            now = datetime.now(datetime.UTC) if hasattr(datetime, 'UTC') else datetime.utcnow()
            for milestone in milestones:
                project = session.query(Project).filter_by(id=milestone.project_id).first()
                days_until_target = (milestone.target_date - now).days if milestone.target_date > now else 0
                days_past_target = (now - milestone.target_date).days if milestone.target_date < now else 0
                is_overdue = milestone.target_date < now and milestone.status != MilestoneStatus.COMPLETED
                is_completed = milestone.status == MilestoneStatus.COMPLETED
                
                row = [
                    milestone.id,
                    milestone.project_id,
                    project.name if project else '',
                    milestone.name,
                    milestone.description or '',
                    milestone.target_date.strftime('%Y-%m-%d'),
                    milestone.completion_date.strftime('%Y-%m-%d') if milestone.completion_date else '',
                    milestone.status.value,
                    'Yes' if is_overdue else 'No',
                    'Yes' if is_completed else 'No',
                    days_until_target,
                    days_past_target,
                    milestone.created_at.strftime('%Y-%m-%d %H:%M:%S') if milestone.created_at else '',
                    milestone.updated_at.strftime('%Y-%m-%d %H:%M:%S') if milestone.updated_at else ''
                ]
                writer.writerow(row)
        
        # Export Risks Table
        risks_filename = f'powerbi_risks_{timestamp}.csv'
        with open(risks_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Risks table headers
            headers = [
                'Risk ID',
                'Project ID',
                'Project Name',
                'Risk Name',
                'Description',
                'Severity',
                'Severity Level',  # Numeric: 1=Low, 2=Medium, 3=High
                'Mitigation Plan',
                'Status',
                'Is High Risk',
                'Is Open',
                'Created At',
                'Updated At'
            ]
            writer.writerow(headers)
            
            severity_level_map = {
                RiskSeverity.LOW: 1,
                RiskSeverity.MEDIUM: 2,
                RiskSeverity.HIGH: 3
            }
            
            for risk in risks:
                project = session.query(Project).filter_by(id=risk.project_id).first()
                is_high_risk = risk.severity == RiskSeverity.HIGH
                is_open = risk.status == 'Open'
                
                row = [
                    risk.id,
                    risk.project_id,
                    project.name if project else '',
                    risk.name,
                    risk.description or '',
                    risk.severity.value,
                    severity_level_map.get(risk.severity, 0),
                    risk.mitigation_plan or '',
                    risk.status,
                    'Yes' if is_high_risk else 'No',
                    'Yes' if is_open else 'No',
                    risk.created_at.strftime('%Y-%m-%d %H:%M:%S') if risk.created_at else '',
                    risk.updated_at.strftime('%Y-%m-%d %H:%M:%S') if risk.updated_at else ''
                ]
                writer.writerow(row)
        
        print(f"Successfully exported Power BI data files:")
        print(f"  - Projects: {projects_filename} ({len(projects)} rows)")
        print(f"  - Milestones: {milestones_filename} ({len(milestones)} rows)")
        print(f"  - Risks: {risks_filename} ({len(risks)} rows)")
        print(f"\nTotal records: {len(projects) + len(milestones) + len(risks)}")
        print(f"\nNext steps:")
        print(f"1. Open Power BI Desktop")
        print(f"2. Get Data -> Text/CSV")
        print(f"3. Import all three CSV files")
        print(f"4. Create relationships:")
        print(f"   - Projects[Project ID] -> Milestones[Project ID]")
        print(f"   - Projects[Project ID] -> Risks[Project ID]")
        print(f"5. Create your visualizations!")
        
        return {
            'projects': projects_filename,
            'milestones': milestones_filename,
            'risks': risks_filename
        }
        
    except Exception as e:
        print(f"Error exporting to Power BI CSV: {e}")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    print("Exporting Project Tracker data to Power BI CSV format...")
    print("-" * 50)
    export_to_powerbi_csv()

