"""
Sample Data Generator for Project Tracker
Creates sample projects, milestones, and risks for testing
"""

from models import Project, Milestone, Risk, ProjectStatus, MilestoneStatus, RiskSeverity
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random

# Create database engine
engine = create_engine('sqlite:///projecttracker.db', echo=False)
Session = sessionmaker(bind=engine)

def create_sample_data():
    """Create sample projects with milestones and risks"""
    session = Session()
    
    try:
        # Sample projects
        projects_data = [
            {
                'name': 'Cloud Migration Initiative',
                'owner': 'Sarah Johnson',
                'description': 'Migrate legacy systems to cloud infrastructure',
                'status': ProjectStatus.IN_PROGRESS,
                'start_date': datetime.now() - timedelta(days=60),
                'deadline': datetime.now() + timedelta(days=30),
                'completion_percentage': 65.0
            },
            {
                'name': 'Mobile App Development',
                'owner': 'Michael Chen',
                'description': 'Build iOS and Android mobile applications',
                'status': ProjectStatus.IN_PROGRESS,
                'start_date': datetime.now() - timedelta(days=45),
                'deadline': datetime.now() + timedelta(days=15),
                'completion_percentage': 80.0
            },
            {
                'name': 'Data Analytics Platform',
                'owner': 'Emily Rodriguez',
                'description': 'Develop analytics dashboard for business intelligence',
                'status': ProjectStatus.IN_PROGRESS,
                'start_date': datetime.now() - timedelta(days=30),
                'deadline': datetime.now() + timedelta(days=60),
                'completion_percentage': 40.0
            },
            {
                'name': 'Security Audit & Compliance',
                'owner': 'David Kim',
                'description': 'Conduct security audit and ensure compliance',
                'status': ProjectStatus.ON_HOLD,
                'start_date': datetime.now() - timedelta(days=90),
                'deadline': datetime.now() - timedelta(days=10),
                'completion_percentage': 30.0
            },
            {
                'name': 'API Gateway Implementation',
                'owner': 'Lisa Wang',
                'description': 'Implement centralized API gateway for microservices',
                'status': ProjectStatus.COMPLETED,
                'start_date': datetime.now() - timedelta(days=120),
                'deadline': datetime.now() - timedelta(days=20),
                'completion_percentage': 100.0
            }
        ]
        
        # Milestone templates
        milestone_templates = [
            ['Planning & Design', 'Development Phase', 'Testing & QA', 'Deployment', 'Documentation'],
            ['Requirements Gathering', 'Architecture Design', 'Implementation', 'Integration', 'Go-Live'],
            ['Discovery', 'Prototype', 'Beta Release', 'Production Release'],
        ]
        
        # Risk templates
        risk_templates = [
            {
                'name': 'Resource Availability',
                'description': 'Key team members may not be available',
                'severity': RiskSeverity.MEDIUM
            },
            {
                'name': 'Technology Dependencies',
                'description': 'Third-party services may have delays',
                'severity': RiskSeverity.HIGH
            },
            {
                'name': 'Scope Creep',
                'description': 'Project requirements may expand',
                'severity': RiskSeverity.MEDIUM
            },
            {
                'name': 'Budget Constraints',
                'description': 'Project may exceed allocated budget',
                'severity': RiskSeverity.LOW
            },
            {
                'name': 'Integration Challenges',
                'description': 'Complex integration with existing systems',
                'severity': RiskSeverity.HIGH
            }
        ]
        
        projects = []
        for proj_data in projects_data:
            project = Project(**proj_data)
            session.add(project)
            session.flush()  # Get the project ID
            projects.append(project)
            
            # Add milestones
            template = random.choice(milestone_templates)
            milestone_count = len(template)
            project_duration = (project.deadline - project.start_date).days
            
            for i, milestone_name in enumerate(template):
                milestone_date = project.start_date + timedelta(
                    days=(project_duration * (i + 1) / (milestone_count + 1))
                )
                
                # Determine status based on date and project completion
                if milestone_date < datetime.now():
                    if project.status == ProjectStatus.COMPLETED:
                        status = MilestoneStatus.COMPLETED
                        completion_date = milestone_date
                    elif i < milestone_count * (project.completion_percentage / 100):
                        status = MilestoneStatus.COMPLETED
                        completion_date = milestone_date
                    else:
                        status = MilestoneStatus.DELAYED
                        completion_date = None
                else:
                    if i < milestone_count * (project.completion_percentage / 100):
                        status = MilestoneStatus.IN_PROGRESS
                        completion_date = None
                    else:
                        status = MilestoneStatus.PENDING
                        completion_date = None
                
                milestone = Milestone(
                    project_id=project.id,
                    name=milestone_name,
                    description=f'Complete {milestone_name.lower()} phase',
                    target_date=milestone_date,
                    completion_date=completion_date,
                    status=status
                )
                session.add(milestone)
            
            # Add risks
            num_risks = random.randint(1, 3)
            selected_risks = random.sample(risk_templates, min(num_risks, len(risk_templates)))
            
            for risk_template in selected_risks:
                risk = Risk(
                    project_id=project.id,
                    name=risk_template['name'],
                    description=risk_template['description'],
                    severity=risk_template['severity'],
                    mitigation_plan=f'Develop mitigation strategy for {risk_template["name"].lower()}',
                    status='Open' if random.random() > 0.3 else 'Mitigated'
                )
                session.add(risk)
        
        session.commit()
        print(f"Successfully created {len(projects)} sample projects with milestones and risks")
        print("Sample data has been added to the database.")
        
    except Exception as e:
        session.rollback()
        print(f"Error creating sample data: {e}")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    print("Creating sample data...")
    create_sample_data()
    print("Done! You can now run the Flask application.")


