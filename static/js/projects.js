let projects = [];
let currentProjectId = null;
let milestones = [];
let risks = [];

// Load projects on page load
document.addEventListener('DOMContentLoaded', function() {
    loadProjects();
});

async function loadProjects() {
    try {
        const response = await fetch('/api/projects');
        projects = await response.json();
        renderProjects();
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

function renderProjects() {
    const container = document.getElementById('projectsContainer');
    
    if (projects.length === 0) {
        container.innerHTML = `
            <div class="col-12">
                <div class="alert alert-info text-center">
                    <h4>No projects yet</h4>
                    <p>Get started by adding your first project!</p>
                    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#projectModal" onclick="openProjectModal()">
                        <i class="bi bi-plus-circle"></i> Add Project
                    </button>
                </div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = projects.map(project => {
        const deadline = new Date(project.deadline);
        const isOverdue = deadline < new Date() && project.status !== 'COMPLETED';
        const statusClass = `status-${project.status.toLowerCase().replace('_', '-')}`;
        
        return `
            <div class="col-md-6 col-lg-4">
                <div class="card project-card">
                    <div class="card-body">
                        <h5 class="card-title">${project.name}</h5>
                        <p class="text-muted mb-2"><i class="bi bi-person"></i> ${project.owner}</p>
                        <p class="card-text">${project.description || 'No description'}</p>
                        <div class="mb-2">
                            <span class="status-badge ${statusClass}">${project.status.replace('_', ' ')}</span>
                        </div>
                        <div class="mb-2">
                            <small class="text-muted">Completion:</small>
                            <div class="progress">
                                <div class="progress-bar" role="progressbar" style="width: ${project.completion_percentage}%">
                                    ${project.completion_percentage}%
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <small class="text-muted">
                                <i class="bi bi-calendar-event"></i> Deadline: 
                                <span class="${isOverdue ? 'text-danger' : ''}">${deadline.toLocaleDateString()}</span>
                            </small>
                        </div>
                        <div class="btn-group w-100" role="group">
                            <button class="btn btn-sm btn-primary" onclick="viewProject(${project.id})">
                                <i class="bi bi-eye"></i> View
                            </button>
                            <button class="btn btn-sm btn-secondary" onclick="editProject(${project.id})">
                                <i class="bi bi-pencil"></i> Edit
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="deleteProject(${project.id})">
                                <i class="bi bi-trash"></i> Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function openProjectModal(projectId = null) {
    const modal = document.getElementById('projectModal');
    const form = document.getElementById('projectForm');
    const title = document.getElementById('projectModalTitle');
    
    form.reset();
    document.getElementById('projectId').value = '';
    
    if (projectId) {
        const project = projects.find(p => p.id === projectId);
        if (project) {
            title.textContent = 'Edit Project';
            document.getElementById('projectId').value = project.id;
            document.getElementById('projectName').value = project.name;
            document.getElementById('projectOwner').value = project.owner;
            document.getElementById('projectDescription').value = project.description || '';
            document.getElementById('projectStartDate').value = project.start_date.split('T')[0];
            document.getElementById('projectDeadline').value = project.deadline.split('T')[0];
            document.getElementById('projectStatus').value = project.status;
            document.getElementById('projectCompletion').value = project.completion_percentage;
        }
    } else {
        title.textContent = 'Add Project';
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('projectStartDate').value = today;
    }
}

async function saveProject() {
    const form = document.getElementById('projectForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const projectId = document.getElementById('projectId').value;
    const data = {
        name: document.getElementById('projectName').value,
        owner: document.getElementById('projectOwner').value,
        description: document.getElementById('projectDescription').value,
        start_date: document.getElementById('projectStartDate').value + 'T00:00:00',
        deadline: document.getElementById('projectDeadline').value + 'T00:00:00',
        status: document.getElementById('projectStatus').value,
        completion_percentage: parseFloat(document.getElementById('projectCompletion').value)
    };
    
    try {
        const url = projectId ? `/api/projects/${projectId}` : '/api/projects';
        const method = projectId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('projectModal'));
            modal.hide();
            loadProjects();
        } else {
            alert('Error saving project');
        }
    } catch (error) {
        console.error('Error saving project:', error);
        alert('Error saving project');
    }
}

async function viewProject(projectId) {
    currentProjectId = projectId;
    const project = projects.find(p => p.id === projectId);
    
    if (project) {
        document.getElementById('projectDetailTitle').textContent = project.name;
        await loadMilestones(projectId);
        await loadRisks(projectId);
        
        const modal = new bootstrap.Modal(document.getElementById('projectDetailModal'));
        modal.show();
    }
}

async function loadMilestones(projectId) {
    try {
        const response = await fetch(`/api/milestones?project_id=${projectId}`);
        milestones = await response.json();
        renderMilestones();
    } catch (error) {
        console.error('Error loading milestones:', error);
    }
}

function renderMilestones() {
    const container = document.getElementById('milestonesList');
    
    if (milestones.length === 0) {
        container.innerHTML = '<p class="text-muted">No milestones yet. Add one to get started!</p>';
        return;
    }
    
    container.innerHTML = milestones.map(milestone => {
        const targetDate = new Date(milestone.target_date);
        const isOverdue = targetDate < new Date() && milestone.status !== 'COMPLETED';
        
        return `
            <div class="milestone-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6>${milestone.name}</h6>
                        <p class="text-muted mb-1">${milestone.description || 'No description'}</p>
                        <small class="text-muted">
                            Target: <span class="${isOverdue ? 'text-danger' : ''}">${targetDate.toLocaleDateString()}</span>
                            ${milestone.completion_date ? ` | Completed: ${new Date(milestone.completion_date).toLocaleDateString()}` : ''}
                        </small>
                        <div class="mt-2">
                            <span class="badge bg-${milestone.status === 'COMPLETED' ? 'success' : milestone.status === 'IN_PROGRESS' ? 'primary' : 'secondary'}">
                                ${milestone.status.replace('_', ' ')}
                            </span>
                        </div>
                    </div>
                    <div>
                        <button class="btn btn-sm btn-outline-primary" onclick="editMilestone(${milestone.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteMilestone(${milestone.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

async function loadRisks(projectId) {
    try {
        const response = await fetch(`/api/risks?project_id=${projectId}`);
        risks = await response.json();
        renderRisks();
    } catch (error) {
        console.error('Error loading risks:', error);
    }
}

function renderRisks() {
    const container = document.getElementById('risksList');
    
    if (risks.length === 0) {
        container.innerHTML = '<p class="text-muted">No risks logged yet. Add one to track potential issues!</p>';
        return;
    }
    
    container.innerHTML = risks.map(risk => {
        const severityClass = risk.severity.toLowerCase();
        return `
            <div class="risk-item risk-${severityClass}">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6>${risk.name}</h6>
                        <p class="text-muted mb-1">${risk.description || 'No description'}</p>
                        <div class="mb-2">
                            <span class="badge bg-${severityClass === 'high' ? 'danger' : severityClass === 'medium' ? 'warning' : 'success'}">
                                ${risk.severity}
                            </span>
                            <span class="badge bg-secondary ms-2">${risk.status}</span>
                        </div>
                        ${risk.mitigation_plan ? `<p class="small"><strong>Mitigation:</strong> ${risk.mitigation_plan}</p>` : ''}
                    </div>
                    <div>
                        <button class="btn btn-sm btn-outline-warning" onclick="editRisk(${risk.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteRisk(${risk.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function openMilestoneModal(milestoneId = null) {
    const form = document.getElementById('milestoneForm');
    form.reset();
    document.getElementById('milestoneId').value = '';
    document.getElementById('milestoneProjectId').value = currentProjectId;
    
    if (milestoneId) {
        const milestone = milestones.find(m => m.id === milestoneId);
        if (milestone) {
            document.getElementById('milestoneId').value = milestone.id;
            document.getElementById('milestoneName').value = milestone.name;
            document.getElementById('milestoneDescription').value = milestone.description || '';
            document.getElementById('milestoneTargetDate').value = milestone.target_date.split('T')[0];
            document.getElementById('milestoneStatus').value = milestone.status;
        }
    }
    
    const modal = new bootstrap.Modal(document.getElementById('milestoneModal'));
    modal.show();
}

async function saveMilestone() {
    const form = document.getElementById('milestoneForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const milestoneId = document.getElementById('milestoneId').value;
    const data = {
        project_id: parseInt(document.getElementById('milestoneProjectId').value),
        name: document.getElementById('milestoneName').value,
        description: document.getElementById('milestoneDescription').value,
        target_date: document.getElementById('milestoneTargetDate').value + 'T00:00:00',
        status: document.getElementById('milestoneStatus').value
    };
    
    if (document.getElementById('milestoneStatus').value === 'COMPLETED' && !milestoneId) {
        data.completion_date = new Date().toISOString();
    }
    
    try {
        const url = milestoneId ? `/api/milestones/${milestoneId}` : '/api/milestones';
        const method = milestoneId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('milestoneModal'));
            modal.hide();
            await loadMilestones(currentProjectId);
            loadProjects(); // Refresh to update completion %
        } else {
            alert('Error saving milestone');
        }
    } catch (error) {
        console.error('Error saving milestone:', error);
        alert('Error saving milestone');
    }
}

function editMilestone(milestoneId) {
    openMilestoneModal(milestoneId);
}

async function deleteMilestone(milestoneId) {
    if (!confirm('Are you sure you want to delete this milestone?')) return;
    
    try {
        const response = await fetch(`/api/milestones/${milestoneId}`, { method: 'DELETE' });
        if (response.ok) {
            await loadMilestones(currentProjectId);
            loadProjects(); // Refresh to update completion %
        }
    } catch (error) {
        console.error('Error deleting milestone:', error);
    }
}

function openRiskModal(riskId = null) {
    const form = document.getElementById('riskForm');
    form.reset();
    document.getElementById('riskId').value = '';
    document.getElementById('riskProjectId').value = currentProjectId;
    
    if (riskId) {
        const risk = risks.find(r => r.id === riskId);
        if (risk) {
            document.getElementById('riskId').value = risk.id;
            document.getElementById('riskName').value = risk.name;
            document.getElementById('riskDescription').value = risk.description || '';
            document.getElementById('riskSeverity').value = risk.severity;
            document.getElementById('riskMitigation').value = risk.mitigation_plan || '';
            document.getElementById('riskStatus').value = risk.status;
        }
    }
    
    const modal = new bootstrap.Modal(document.getElementById('riskModal'));
    modal.show();
}

async function saveRisk() {
    const form = document.getElementById('riskForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const riskId = document.getElementById('riskId').value;
    const data = {
        project_id: parseInt(document.getElementById('riskProjectId').value),
        name: document.getElementById('riskName').value,
        description: document.getElementById('riskDescription').value,
        severity: document.getElementById('riskSeverity').value,
        mitigation_plan: document.getElementById('riskMitigation').value,
        status: document.getElementById('riskStatus').value
    };
    
    try {
        const url = riskId ? `/api/risks/${riskId}` : '/api/risks';
        const method = riskId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('riskModal'));
            modal.hide();
            await loadRisks(currentProjectId);
        } else {
            alert('Error saving risk');
        }
    } catch (error) {
        console.error('Error saving risk:', error);
        alert('Error saving risk');
    }
}

function editRisk(riskId) {
    openRiskModal(riskId);
}

async function deleteRisk(riskId) {
    if (!confirm('Are you sure you want to delete this risk?')) return;
    
    try {
        const response = await fetch(`/api/risks/${riskId}`, { method: 'DELETE' });
        if (response.ok) {
            await loadRisks(currentProjectId);
        }
    } catch (error) {
        console.error('Error deleting risk:', error);
    }
}

async function generateSummary() {
    if (!currentProjectId) return;
    
    const summaryDiv = document.getElementById('aiSummary');
    summaryDiv.innerHTML = '<div class="spinner-border" role="status"><span class="visually-hidden">Generating...</span></div>';
    
    try {
        const response = await fetch(`/api/ai/summarize/${currentProjectId}`, { method: 'POST' });
        const data = await response.json();
        
        summaryDiv.innerHTML = `<pre class="mb-0">${data.summary}</pre>`;
    } catch (error) {
        console.error('Error generating summary:', error);
        summaryDiv.innerHTML = '<p class="text-danger">Error generating summary</p>';
    }
}

function editProject(projectId) {
    openProjectModal(projectId);
    const modal = new bootstrap.Modal(document.getElementById('projectModal'));
    modal.show();
}

async function deleteProject(projectId) {
    if (!confirm('Are you sure you want to delete this project? This will also delete all associated milestones and risks.')) return;
    
    try {
        const response = await fetch(`/api/projects/${projectId}`, { method: 'DELETE' });
        if (response.ok) {
            loadProjects();
        } else {
            alert('Error deleting project');
        }
    } catch (error) {
        console.error('Error deleting project:', error);
        alert('Error deleting project');
    }
}


