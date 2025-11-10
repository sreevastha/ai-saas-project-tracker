from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import Base, Project, Milestone, Risk, ProjectStatus, MilestoneStatus, RiskSeverity
from datetime import datetime, timedelta
import csv
import io
import os

app = Flask(__name__)
CORS(app)

# Database setup
engine = create_engine('sqlite:///projecttracker.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Helper function to get session
def get_session():
    return Session()

# Helper function to calculate project completion
def calculate_completion(project, session):
    milestones = session.query(Milestone).filter_by(project_id=project.id).all()
    if not milestones:
        return project.completion_percentage
    
    completed = sum(1 for m in milestones if m.status == MilestoneStatus.COMPLETED)
    return (completed / len(milestones)) * 100 if milestones else 0

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/projects')
def projects_page():
    return render_template('projects.html')

# API Routes - Projects
@app.route('/api/projects', methods=['GET'])
def get_projects():
    session = get_session()
    try:
        projects = session.query(Project).all()
        return jsonify([p.to_dict() for p in projects])
    finally:
        session.close()

@app.route('/api/projects', methods=['POST'])
def create_project():
    session = get_session()
    try:
        data = request.json
        project = Project(
            name=data['name'],
            owner=data['owner'],
            description=data.get('description', ''),
            status=ProjectStatus[data.get('status', 'NOT_STARTED').upper().replace(' ', '_')],
            start_date=datetime.fromisoformat(data['start_date']),
            deadline=datetime.fromisoformat(data['deadline']),
            completion_percentage=data.get('completion_percentage', 0.0)
        )
        session.add(project)
        session.commit()
        return jsonify(project.to_dict()), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    session = get_session()
    try:
        project = session.query(Project).filter_by(id=project_id).first()
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        return jsonify(project.to_dict())
    finally:
        session.close()

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    session = get_session()
    try:
        project = session.query(Project).filter_by(id=project_id).first()
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.json
        if 'name' in data:
            project.name = data['name']
        if 'owner' in data:
            project.owner = data['owner']
        if 'description' in data:
            project.description = data['description']
        if 'status' in data:
            project.status = ProjectStatus[data['status'].upper().replace(' ', '_')]
        if 'start_date' in data:
            project.start_date = datetime.fromisoformat(data['start_date'])
        if 'deadline' in data:
            project.deadline = datetime.fromisoformat(data['deadline'])
        if 'completion_percentage' in data:
            project.completion_percentage = data['completion_percentage']
        
        project.updated_at = datetime.utcnow()
        session.commit()
        return jsonify(project.to_dict())
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    session = get_session()
    try:
        project = session.query(Project).filter_by(id=project_id).first()
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        session.delete(project)
        session.commit()
        return jsonify({'message': 'Project deleted successfully'})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

# API Routes - Milestones
@app.route('/api/milestones', methods=['GET'])
def get_milestones():
    session = get_session()
    try:
        project_id = request.args.get('project_id')
        query = session.query(Milestone)
        if project_id:
            query = query.filter_by(project_id=project_id)
        milestones = query.all()
        return jsonify([m.to_dict() for m in milestones])
    finally:
        session.close()

@app.route('/api/milestones', methods=['POST'])
def create_milestone():
    session = get_session()
    try:
        data = request.json
        milestone = Milestone(
            project_id=data['project_id'],
            name=data['name'],
            description=data.get('description', ''),
            target_date=datetime.fromisoformat(data['target_date']),
            status=MilestoneStatus[data.get('status', 'PENDING').upper().replace(' ', '_')]
        )
        if 'completion_date' in data and data['completion_date']:
            milestone.completion_date = datetime.fromisoformat(data['completion_date'])
        session.add(milestone)
        session.commit()
        
        # Update project completion percentage
        project = session.query(Project).filter_by(id=data['project_id']).first()
        if project:
            project.completion_percentage = calculate_completion(project, session)
            session.commit()
        
        return jsonify(milestone.to_dict()), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

@app.route('/api/milestones/<int:milestone_id>', methods=['PUT'])
def update_milestone(milestone_id):
    session = get_session()
    try:
        milestone = session.query(Milestone).filter_by(id=milestone_id).first()
        if not milestone:
            return jsonify({'error': 'Milestone not found'}), 404
        
        data = request.json
        if 'name' in data:
            milestone.name = data['name']
        if 'description' in data:
            milestone.description = data['description']
        if 'target_date' in data:
            milestone.target_date = datetime.fromisoformat(data['target_date'])
        if 'completion_date' in data:
            milestone.completion_date = datetime.fromisoformat(data['completion_date']) if data['completion_date'] else None
        if 'status' in data:
            milestone.status = MilestoneStatus[data['status'].upper().replace(' ', '_')]
        
        milestone.updated_at = datetime.utcnow()
        session.commit()
        
        # Update project completion percentage
        project = session.query(Project).filter_by(id=milestone.project_id).first()
        if project:
            project.completion_percentage = calculate_completion(project, session)
            session.commit()
        
        return jsonify(milestone.to_dict())
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

@app.route('/api/milestones/<int:milestone_id>', methods=['DELETE'])
def delete_milestone(milestone_id):
    session = get_session()
    try:
        milestone = session.query(Milestone).filter_by(id=milestone_id).first()
        if not milestone:
            return jsonify({'error': 'Milestone not found'}), 404
        project_id = milestone.project_id
        session.delete(milestone)
        session.commit()
        
        # Update project completion percentage
        project = session.query(Project).filter_by(id=project_id).first()
        if project:
            project.completion_percentage = calculate_completion(project, session)
            session.commit()
        
        return jsonify({'message': 'Milestone deleted successfully'})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

# API Routes - Risks
@app.route('/api/risks', methods=['GET'])
def get_risks():
    session = get_session()
    try:
        project_id = request.args.get('project_id')
        query = session.query(Risk)
        if project_id:
            query = query.filter_by(project_id=project_id)
        risks = query.all()
        return jsonify([r.to_dict() for r in risks])
    finally:
        session.close()

@app.route('/api/risks', methods=['POST'])
def create_risk():
    session = get_session()
    try:
        data = request.json
        risk = Risk(
            project_id=data['project_id'],
            name=data['name'],
            description=data.get('description', ''),
            severity=RiskSeverity[data['severity'].upper()],
            mitigation_plan=data.get('mitigation_plan', ''),
            status=data.get('status', 'Open')
        )
        session.add(risk)
        session.commit()
        return jsonify(risk.to_dict()), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

@app.route('/api/risks/<int:risk_id>', methods=['PUT'])
def update_risk(risk_id):
    session = get_session()
    try:
        risk = session.query(Risk).filter_by(id=risk_id).first()
        if not risk:
            return jsonify({'error': 'Risk not found'}), 404
        
        data = request.json
        if 'name' in data:
            risk.name = data['name']
        if 'description' in data:
            risk.description = data['description']
        if 'severity' in data:
            risk.severity = RiskSeverity[data['severity'].upper()]
        if 'mitigation_plan' in data:
            risk.mitigation_plan = data['mitigation_plan']
        if 'status' in data:
            risk.status = data['status']
        
        risk.updated_at = datetime.utcnow()
        session.commit()
        return jsonify(risk.to_dict())
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

@app.route('/api/risks/<int:risk_id>', methods=['DELETE'])
def delete_risk(risk_id):
    session = get_session()
    try:
        risk = session.query(Risk).filter_by(id=risk_id).first()
        if not risk:
            return jsonify({'error': 'Risk not found'}), 404
        session.delete(risk)
        session.commit()
        return jsonify({'message': 'Risk deleted successfully'})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

# API Routes - KPIs
@app.route('/api/kpis', methods=['GET'])
def get_kpis():
    session = get_session()
    try:
        projects = session.query(Project).all()
        milestones = session.query(Milestone).all()
        risks = session.query(Risk).all()
        
        now = datetime.utcnow()
        
        # Calculate metrics
        total_projects = len(projects)
        if total_projects == 0:
            return jsonify({
                'projects_on_track': 0,
                'avg_delay_percentage': 0,
                'high_risk_count': 0,
                'total_projects': 0,
                'avg_completion': 0,
                'milestone_completion': 0
            })
        
        # Projects on track (not past deadline or completed)
        on_track = sum(1 for p in projects 
                      if p.deadline >= now or p.status == ProjectStatus.COMPLETED)
        projects_on_track_pct = (on_track / total_projects) * 100
        
        # Average delay percentage
        delays = []
        for p in projects:
            if p.deadline < now and p.status != ProjectStatus.COMPLETED:
                days_past = (now - p.deadline).days
                total_days = (p.deadline - p.start_date).days
                if total_days > 0:
                    delay_pct = (days_past / total_days) * 100
                    delays.append(delay_pct)
        avg_delay = sum(delays) / len(delays) if delays else 0
        
        # High risk count
        high_risk_count = sum(1 for r in risks if r.severity == RiskSeverity.HIGH and r.status != 'Closed')
        
        # Average completion
        avg_completion = sum(p.completion_percentage for p in projects) / total_projects
        
        # Milestone completion
        total_milestones = len(milestones)
        completed_milestones = sum(1 for m in milestones if m.status == MilestoneStatus.COMPLETED)
        milestone_completion_pct = (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0
        
        return jsonify({
            'projects_on_track': round(projects_on_track_pct, 2),
            'avg_delay_percentage': round(avg_delay, 2),
            'high_risk_count': high_risk_count,
            'total_projects': total_projects,
            'avg_completion': round(avg_completion, 2),
            'milestone_completion': round(milestone_completion_pct, 2)
        })
    finally:
        session.close()

# Export to CSV
@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    session = get_session()
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Project Name', 'Owner', 'Status', 'Start Date', 'Deadline', 
                        'Completion %', 'Milestone Name', 'Milestone Status', 'Risk Name', 
                        'Risk Severity', 'Risk Status'])
        
        projects = session.query(Project).all()
        for project in projects:
            milestones = session.query(Milestone).filter_by(project_id=project.id).all()
            risks = session.query(Risk).filter_by(project_id=project.id).all()
            
            max_rows = max(len(milestones), len(risks), 1)
            
            for i in range(max_rows):
                row = [
                    project.name if i == 0 else '',
                    project.owner if i == 0 else '',
                    project.status.value if i == 0 else '',
                    project.start_date.strftime('%Y-%m-%d') if i == 0 else '',
                    project.deadline.strftime('%Y-%m-%d') if i == 0 else '',
                    project.completion_percentage if i == 0 else '',
                    milestones[i].name if i < len(milestones) else '',
                    milestones[i].status.value if i < len(milestones) else '',
                    risks[i].name if i < len(risks) else '',
                    risks[i].severity.value if i < len(risks) else '',
                    risks[i].status if i < len(risks) else ''
                ]
                writer.writerow(row)
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='project_export.csv'
        )
    finally:
        session.close()

# AI Summarization (Optional)
@app.route('/api/ai/summarize/<int:project_id>', methods=['POST'])
def summarize_project(project_id):
    session = get_session()
    try:
        project = session.query(Project).filter_by(id=project_id).first()
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        milestones = session.query(Milestone).filter_by(project_id=project_id).all()
        risks = session.query(Risk).filter_by(project_id=project_id).all()
        
        # Use AI summarizer if available
        try:
            from ai_summarizer import summarizer
            project_dict = project.to_dict()
            milestones_dict = [m.to_dict() for m in milestones]
            risks_dict = [r.to_dict() for r in risks]
            summary = summarizer.generate_summary(project_dict, milestones_dict, risks_dict)
        except ImportError:
            # Fallback to basic summary
            summary = f"""
Project Summary: {project.name}
Owner: {project.owner}
Status: {project.status.value}
Completion: {project.completion_percentage}%

Milestones: {len(milestones)} total
- Completed: {sum(1 for m in milestones if m.status == MilestoneStatus.COMPLETED)}
- In Progress: {sum(1 for m in milestones if m.status == MilestoneStatus.IN_PROGRESS)}
- Pending: {sum(1 for m in milestones if m.status == MilestoneStatus.PENDING)}

Risks: {len(risks)} total
- High: {sum(1 for r in risks if r.severity == RiskSeverity.HIGH)}
- Medium: {sum(1 for r in risks if r.severity == RiskSeverity.MEDIUM)}
- Low: {sum(1 for r in risks if r.severity == RiskSeverity.LOW)}
            """
        
        return jsonify({'summary': summary.strip()})
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

