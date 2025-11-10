"""
Jira CSV Export Script
Exports Project Tracker data to Jira-compatible CSV format
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Project, Milestone, Risk, ProjectStatus, MilestoneStatus, RiskSeverity
from datetime import datetime
import csv

# Database setup
engine = create_engine('sqlite:///projecttracker.db', echo=False)
Session = sessionmaker(bind=engine)

def map_status_to_jira(project_status):
    """Map Project Tracker status to Jira status"""
    status_map = {
        'Not Started': 'To Do',
        'In Progress': 'In Progress',
        'On Hold': 'On Hold',
        'Completed': 'Done',
        'Cancelled': 'Cancelled'
    }
    return status_map.get(project_status, 'To Do')

def map_milestone_status_to_jira(milestone_status):
    """Map Milestone status to Jira status"""
    status_map = {
        'Pending': 'To Do',
        'In Progress': 'In Progress',
        'Completed': 'Done',
        'Delayed': 'In Progress'  # Delayed items are still in progress
    }
    return status_map.get(milestone_status, 'To Do')

def map_priority(severity):
    """Map risk severity to Jira priority"""
    priority_map = {
        'High': 'Highest',
        'Medium': 'High',
        'Low': 'Medium'
    }
    return priority_map.get(severity, 'Medium')

def export_to_jira_csv(project_key='PT', assignee=None):
    """
    Export all projects, milestones, and risks to Jira CSV format
    
    Args:
        project_key: Your Jira project key (default: PT)
        assignee: Assignee username (leave None to leave unassigned)
    """
    session = Session()
    
    try:
        # Open CSV file for writing
        filename = f'jira_import_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Jira CSV Import Headers
            # Note: Epic Name field ID may vary - you might need to adjust customfield_10011
            headers = [
                'Work Item ID',     # Unique identifier for each issue (required)
                'Summary',           # Issue title
                'Work Type',        # Epic, Story, Task (required - alternative to Issue Type)
                'Issue Type',       # Epic, Story, Task (keep for compatibility)
                'Project Key',      # Your Jira project key
                'Description',      # Issue description
                'Epic Name',        # For Epics
                'Epic Link',        # For Stories (links to Epic)
                'Parent ID',        # Parent work item ID (required for linking)
                'Parent',           # Alternative to Epic Link
                'Priority',         # Highest, High, Medium, Low
                'Status',           # To Do, In Progress, Done, etc.
                'Labels',           # Comma-separated labels
                'Due Date',         # YYYY-MM-DD format
                'Assignee',         # Jira username (optional)
                'Story Points',     # For Stories
            ]
            
            writer.writerow(headers)
            
            projects = session.query(Project).all()
            epic_keys = {}  # Store Epic keys for linking stories
            epic_work_ids = {}  # Store Work Item IDs for Epics (for Parent ID linking)
            work_item_counter = 1  # Counter for unique Work Item IDs
            
            # First pass: Create Epics
            for project in projects:
                # Create Epic
                epic_name = project.name
                epic_key = f"{project_key}-EPIC-{project.id}"  # Temporary key for reference
                epic_keys[project.id] = epic_name
                epic_work_id = f"EPIC-{work_item_counter}"  # Unique Work Item ID for this Epic
                epic_work_ids[project.id] = epic_work_id
                work_item_counter += 1
                
                # Build description
                description = f"""Owner: {project.owner}
Status: {project.status.value}
Completion: {project.completion_percentage}%
Start Date: {project.start_date.strftime('%Y-%m-%d')}
Deadline: {project.deadline.strftime('%Y-%m-%d')}

{project.description or 'No description provided'}"""
                
                # Determine priority based on deadline
                now = datetime.now()
                days_remaining = (project.deadline - now).days
                if days_remaining < 0:
                    priority = 'Highest'
                elif days_remaining < 15:
                    priority = 'High'
                else:
                    priority = 'Medium'
                
                # Build labels
                labels = ['project-tracker', project.status.value.lower().replace(' ', '-')]
                if project.completion_percentage >= 80:
                    labels.append('high-completion')
                
                row = [
                    epic_work_id,          # Work Item ID
                    epic_name,              # Summary
                    'Epic',                 # Work Type
                    'Epic',                 # Issue Type (for compatibility)
                    project_key,            # Project Key
                    description,           # Description
                    epic_name,             # Epic Name (required for Epic type)
                    '',                    # Epic Link (not needed for Epics)
                    '',                    # Parent ID (Epics have no parent)
                    '',                    # Parent (alternative)
                    priority,             # Priority
                    map_status_to_jira(project.status.value),  # Status
                    ','.join(labels),      # Labels
                    project.deadline.strftime('%Y-%m-%d'),  # Due Date
                    assignee or '',        # Assignee
                    '',                    # Story Points (not for Epics)
                ]
                writer.writerow(row)
            
            # Second pass: Create Stories (from Milestones)
            for project in projects:
                milestones = session.query(Milestone).filter_by(project_id=project.id).all()
                
                for milestone in milestones:
                    # Build description
                    description = f"""Target Date: {milestone.target_date.strftime('%Y-%m-%d')}
Status: {milestone.status.value}

{milestone.description or 'No description provided'}"""
                    
                    if milestone.completion_date:
                        description += f"\nCompleted: {milestone.completion_date.strftime('%Y-%m-%d')}"
                    
                    # Estimate story points based on milestone position
                    # You can adjust this logic
                    story_points = 5  # Default
                    if 'Planning' in milestone.name or 'Design' in milestone.name:
                        story_points = 3
                    elif 'Development' in milestone.name or 'Implementation' in milestone.name:
                        story_points = 8
                    elif 'Testing' in milestone.name or 'QA' in milestone.name:
                        story_points = 5
                    elif 'Deployment' in milestone.name or 'Release' in milestone.name:
                        story_points = 3
                    elif 'Documentation' in milestone.name:
                        story_points = 2
                    
                    # Determine priority
                    now = datetime.now()
                    if milestone.target_date < now and milestone.status.value != 'Completed':
                        priority = 'Highest'
                    elif (milestone.target_date - now).days < 7:
                        priority = 'High'
                    else:
                        priority = 'Medium'
                    
                    labels = ['project-tracker', 'milestone', milestone.status.value.lower().replace(' ', '-')]
                    
                    story_work_id = f"STORY-{work_item_counter}"  # Unique Work Item ID for this Story
                    work_item_counter += 1
                    parent_work_id = epic_work_ids[project.id]  # Parent Epic's Work Item ID
                    
                    row = [
                        story_work_id,     # Work Item ID
                        milestone.name,   # Summary
                        'Story',          # Work Type
                        'Story',          # Issue Type (for compatibility)
                        project_key,      # Project Key
                        description,      # Description
                        '',               # Epic Name (not for Stories)
                        epic_keys[project.id],  # Epic Link (links to parent Epic)
                        parent_work_id,   # Parent ID (links to Epic's Work Item ID)
                        '',               # Parent (alternative)
                        priority,        # Priority
                        map_milestone_status_to_jira(milestone.status.value),  # Status
                        ','.join(labels), # Labels
                        milestone.target_date.strftime('%Y-%m-%d'),  # Due Date
                        assignee or '',   # Assignee
                        str(story_points),  # Story Points
                    ]
                    writer.writerow(row)
            
            # Third pass: Create Risk Issues
            for project in projects:
                risks = session.query(Risk).filter_by(project_id=project.id).all()
                
                for risk in risks:
                    # Build description
                    description = f"""Severity: {risk.severity.value}
Status: {risk.status}

{risk.description or 'No description provided'}"""
                    
                    if risk.mitigation_plan:
                        description += f"\n\nMitigation Plan:\n{risk.mitigation_plan}"
                    
                    labels = ['project-tracker', 'risk', risk.severity.value.lower(), risk.status.lower()]
                    
                    # Map risk status to Jira status
                    if risk.status == 'Closed':
                        jira_status = 'Done'
                    elif risk.status == 'Mitigated':
                        jira_status = 'In Progress'
                    else:
                        jira_status = 'To Do'
                    
                    risk_work_id = f"RISK-{work_item_counter}"  # Unique Work Item ID for this Risk
                    work_item_counter += 1
                    parent_work_id = epic_work_ids[project.id]  # Parent Epic's Work Item ID
                    
                    row = [
                        risk_work_id,     # Work Item ID
                        risk.name,        # Summary
                        'Task',           # Work Type
                        'Task',           # Issue Type (for compatibility)
                        project_key,      # Project Key
                        description,      # Description
                        '',               # Epic Name
                        epic_keys[project.id],  # Epic Link
                        parent_work_id,   # Parent ID (links to Epic's Work Item ID)
                        '',               # Parent (alternative)
                        map_priority(risk.severity.value),  # Priority
                        jira_status,      # Status
                        ','.join(labels), # Labels
                        '',               # Due Date (risks don't have due dates)
                        assignee or '',   # Assignee
                        '',               # Story Points (not for risks)
                    ]
                    writer.writerow(row)
        
        print(f"Successfully exported to {filename}")
        print(f"  - Epics: {len(projects)}")
        
        total_milestones = sum(len(session.query(Milestone).filter_by(project_id=p.id).all()) for p in projects)
        total_risks = sum(len(session.query(Risk).filter_by(project_id=p.id).all()) for p in projects)
        
        print(f"  - Stories: {total_milestones}")
        print(f"  - Risks: {total_risks}")
        print(f"  - Total Issues: {len(projects) + total_milestones + total_risks}")
        print(f"\nNext steps:")
        print(f"1. Open Jira -> Issues -> Import Issues from CSV")
        print(f"2. Select the file: {filename}")
        print(f"3. Map the columns (they should auto-detect)")
        print(f"4. Click 'Begin Import'")
        
        return filename
        
    except Exception as e:
        print(f"Error exporting to Jira CSV: {e}")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    # Configuration
    PROJECT_KEY = 'PT'  # Change this to your Jira project key (e.g., 'PT', 'PROJ', 'TRACK')
    ASSIGNEE = None      # Set to your Jira username if you want to assign all issues, or leave None
    
    print("Exporting Project Tracker data to Jira CSV format...")
    print(f"Project Key: {PROJECT_KEY}")
    print(f"Assignee: {ASSIGNEE or 'Unassigned'}")
    print("-" * 50)
    
    export_to_jira_csv(project_key=PROJECT_KEY, assignee=ASSIGNEE)