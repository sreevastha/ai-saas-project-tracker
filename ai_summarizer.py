"""
AI Summarization Module for Project Tracker
Uses Hugging Face transformers for generating project summaries
"""

try:
    from transformers import pipeline
    import torch
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("Warning: Transformers library not available. AI features will be disabled.")

class ProjectSummarizer:
    """Generates AI-powered summaries for projects"""
    
    def __init__(self):
        self.summarizer = None
        self.initialized = False
        
        if AI_AVAILABLE:
            try:
                # Use a lighter-weight summarization model to reduce download size
                model_name = "google/flan-t5-small"
                self.summarizer = pipeline(
                    "summarization",
                    model=model_name,
                    tokenizer=model_name,
                    device=-1,
                )
                self.initialized = True
            except Exception as e:
                print(f"Warning: Could not initialize AI summarizer: {e}")
                self.initialized = False
    
    def generate_summary(self, project_data, milestones_data, risks_data):
        """
        Generate a comprehensive project summary
        
        Args:
            project_data: Dictionary containing project information
            milestones_data: List of milestone dictionaries
            risks_data: List of risk dictionaries
        
        Returns:
            String containing the generated summary
        """
        recommendations = self._generate_recommendations(project_data, milestones_data, risks_data)

        if not self.initialized:
            body = self._generate_basic_body(project_data, milestones_data, risks_data)
            return self._format_output(body, recommendations)
        
        # Build context text
        context = self._build_context(project_data, milestones_data, risks_data)

        try:
            # Generate summary using AI model
            instruction = (
                "Summarize the following software project update in 3-4 sentences. "
                "Highlight overall progress, milestone status, and risk posture in a professional tone."
            )
            input_text = f"{instruction}\n\n{context}"
            summary = self.summarizer(
                input_text,
                max_length=220,
                min_length=80,
                do_sample=False
            )
            summary_text = summary[0]['summary_text'].strip()
        except Exception as e:
            print(f"Error generating AI summary: {e}")
            summary_text = self._generate_basic_body(project_data, milestones_data, risks_data)

        return self._format_output(summary_text, recommendations)
    
    def _build_context(self, project, milestones, risks):
        """Build context text from project data"""
        context_parts = []
        
        # Project information
        context_parts.append(f"Project Name: {project.get('name', 'Unknown')}")
        context_parts.append(f"Owner: {project.get('owner', 'Unknown')}")
        context_parts.append(f"Status: {project.get('status', 'Unknown')}")
        context_parts.append(f"Completion Percentage: {project.get('completion_percentage', 0)}%")
        
        if project.get('start_date'):
            context_parts.append(f"Start Date: {project.get('start_date')}")
        if project.get('deadline'):
            context_parts.append(f"Deadline: {project.get('deadline')}")
        if project.get('description'):
            context_parts.append(f"Project Description: {project['description']}")
        
        # Milestones
        if milestones:
            context_parts.append(f"Milestones ({len(milestones)} total):")
            for milestone in milestones:
                status = milestone.get('status', 'Unknown')
                name = milestone.get('name', 'Unknown')
                target_date = milestone.get('target_date')
                milestone_line = f"- {name} ({status}"
                if target_date:
                    milestone_line += f", target {target_date}"
                milestone_line += ")"
                context_parts.append(milestone_line)
        
        # Risks
        if risks:
            high_risks = [r for r in risks if r.get('severity') == 'HIGH']
            context_parts.append(f"Risks ({len(risks)} total, {len(high_risks)} high severity):")
            for risk in risks[:3]:  # Include up to top 3 risks
                context_parts.append(
                    f"- {risk.get('name', 'Unknown')} "
                    f"(severity {risk.get('severity')}, status {risk.get('status', 'Unknown')}) "
                    f"{risk.get('description', '')}"
                )
        
        return "\n".join(context_parts)
    
    def _generate_basic_body(self, project, milestones, risks):
        """Generate a structured summary without using AI"""
        from datetime import datetime
        
        def parse_date(value):
            if not value:
                return None
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return None
        
        def format_date(value):
            return value.strftime('%Y-%m-%d') if value else None
        
        now = datetime.utcnow()
        paragraphs = []
        
        name = project.get('name', 'Unknown Project')
        status = (project.get('status', 'Unknown') or 'Unknown').replace('_', ' ').title()
        completion = project.get('completion_percentage', 0)
        owner = project.get('owner', 'Unknown')
        description = project.get('description')
        
        start_dt = parse_date(project.get('start_date'))
        deadline_dt = parse_date(project.get('deadline'))
        
        timeline_parts = []
        if start_dt:
            timeline_parts.append(f"started on {format_date(start_dt)}")
        if deadline_dt:
            timeline_parts.append(f"targeting a deadline of {format_date(deadline_dt)}")
        
        sentence = f"{name} led by {owner} is currently {status.lower()} at {completion:.0f}% completion."
        if timeline_parts:
            sentence += " It " + " and ".join(timeline_parts) + "."
        
        if deadline_dt and status.lower() != "completed":
            if deadline_dt < now:
                overdue_days = (now - deadline_dt).days
                sentence += f" The project is overdue by {overdue_days} day(s)."
            else:
                remaining_days = (deadline_dt - now).days
                sentence += f" There are {remaining_days} day(s) remaining until the deadline."
        
        if description:
            sentence += f" The team is focused on {description}."
        
        paragraphs.append(sentence)
        
        if milestones:
            total = len(milestones)
            completed = sum(1 for m in milestones if m.get('status') == 'COMPLETED')
            in_progress = sum(1 for m in milestones if m.get('status') == 'IN_PROGRESS')
            pending = sum(1 for m in milestones if m.get('status') == 'PENDING')
            delayed = [m for m in milestones if m.get('status') == 'DELAYED']
            
            milestone_sentence = (
                f"{completed} of {total} milestones are complete, "
                f"{in_progress} in progress, and {pending} pending."
            )
            if delayed:
                names = ", ".join(m.get('name', 'Unnamed milestone') for m in delayed[:3])
                milestone_sentence += f" Attention is needed on delayed milestone(s): {names}."
            paragraphs.append(milestone_sentence)
        else:
            paragraphs.append("No milestones have been defined yet.")
        
        if risks:
            def is_high(risk):
                severity = (risk.get('severity', '') or '').upper()
                status = (risk.get('status', '') or '').upper()
                return severity == 'HIGH' and status != 'CLOSED'
            
            def is_open(risk):
                status = (risk.get('status', '') or '').upper()
                return status != 'CLOSED'
            
            high_risks = [r for r in risks if is_high(r)]
            open_risks = [r for r in risks if is_open(r)]
            risk_sentence = (
                f"There are {len(risks)} logged risks"
                f"{' with ' + str(len(high_risks)) + ' high severity item(s)' if high_risks else ''}."
            )
            if open_risks:
                top_risk_names = ", ".join(r.get('name', 'Unnamed risk') for r in open_risks[:3])
                risk_sentence += f" Active risks include: {top_risk_names}."
            paragraphs.append(risk_sentence)
        else:
            paragraphs.append("No risks have been reported for this project.")
        
        return "\n\n".join(paragraphs)

    def _generate_recommendations(self, project, milestones, risks):
        from datetime import datetime
        
        def parse_date(value):
            if not value:
                return None
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return None
        
        recommendations = []
        completion = project.get('completion_percentage', 0) or 0
        status = (project.get('status', '') or '').upper()
        deadline_dt = parse_date(project.get('deadline'))
        now = datetime.utcnow()
        
        if deadline_dt and status != 'COMPLETED':
            days_to_deadline = (deadline_dt - now).days
            if days_to_deadline < 0:
                recommendations.append("Escalate the overdue timeline and realign deliverables with stakeholders.")
            elif days_to_deadline <= 14:
                recommendations.append("Hold a schedule review to ensure remaining scope fits the upcoming deadline.")
        
        if completion < 50 and status not in ('NOT_STARTED', 'COMPLETED'):
            recommendations.append("Accelerate execution—completion is below 50%, so consider rebalancing resources.")
        
        delayed_milestones = [m for m in milestones if m.get('status') == 'DELAYED']
        if delayed_milestones:
            names = ", ".join(m.get('name', 'Unnamed milestone') for m in delayed_milestones[:3])
            recommendations.append(f"Resolve blockers for delayed milestone(s): {names}.")
        
        high_risks = [
            r for r in risks
            if (r.get('severity', '') or '').upper() == 'HIGH'
            and (r.get('status', '') or '').upper() != 'CLOSED'
        ]
        if high_risks:
            recommendations.append("Address high-severity risks immediately and update mitigation plans.")
        
        open_risks = [
            r for r in risks
            if (r.get('status', 'Open') or 'Open').upper() != 'CLOSED'
        ]
        if not recommendations and not open_risks:
            recommendations.append("Maintain current pace and continue regular status reviews.")
        
        return recommendations

    def _format_output(self, body, recommendations):
        body = body.strip()
        if not recommendations:
            return body
        
        recommendation_lines = "\n".join(f"- {item}" for item in recommendations)
        return f"{body}\n\nRecommendations:\n{recommendation_lines}"

# Global instance
summarizer = ProjectSummarizer()


