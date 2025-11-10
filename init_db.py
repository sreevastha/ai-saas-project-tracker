from models import Base, Project, Milestone, Risk, ProjectStatus, MilestoneStatus, RiskSeverity
from sqlalchemy import create_engine
from datetime import datetime, timedelta

# Create database engine
engine = create_engine('sqlite:///projecttracker.db', echo=False)

# Create all tables
Base.metadata.create_all(engine)

print("Database initialized successfully!")
print("You can now run the Flask application with: python app.py")


