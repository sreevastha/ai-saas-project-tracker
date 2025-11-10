let projectsData = [];

// Load dashboard data
async function loadDashboard() {
    try {
        // Load KPIs
        const kpiResponse = await fetch('/api/kpis');
        const kpis = await kpiResponse.json();
        
        document.getElementById('onTrackPct').textContent = kpis.projects_on_track + '%';
        document.getElementById('avgDelay').textContent = kpis.avg_delay_percentage + '%';
        document.getElementById('highRiskCount').textContent = kpis.high_risk_count;
        document.getElementById('avgCompletion').textContent = kpis.avg_completion + '%';
        
        // Load projects
        const projectsResponse = await fetch('/api/projects');
        projectsData = await projectsResponse.json();
        
        // Update charts
        updateCharts();
        
        // Update projects table
        updateProjectsTable();
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function updateCharts() {
    // Status distribution chart
    const statusCounts = {};
    projectsData.forEach(p => {
        const status = p.status || 'NOT_STARTED';
        statusCounts[status] = (statusCounts[status] || 0) + 1;
    });
    
    const statusData = [{
        values: Object.values(statusCounts),
        labels: Object.keys(statusCounts).map(s => s.replace('_', ' ')),
        type: 'pie',
        marker: {
            colors: ['#6c757d', '#0d6efd', '#ffc107', '#198754', '#dc3545']
        }
    }];
    
    Plotly.newPlot('statusChart', statusData, {
        title: 'Project Status Distribution',
        height: 300
    });
    
    // Completion trends chart
    const completionData = [{
        x: projectsData.map(p => p.name),
        y: projectsData.map(p => p.completion_percentage || 0),
        type: 'bar',
        marker: {
            color: projectsData.map(p => {
                const comp = p.completion_percentage || 0;
                if (comp >= 80) return '#198754';
                if (comp >= 50) return '#ffc107';
                return '#dc3545';
            })
        }
    }];
    
    Plotly.newPlot('completionChart', completionData, {
        title: 'Project Completion Percentage',
        xaxis: { title: 'Projects' },
        yaxis: { title: 'Completion %' },
        height: 300
    });
}

function updateProjectsTable() {
    const tbody = document.getElementById('projectsTable');
    
    if (projectsData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No projects found. <a href="/projects">Add a project</a></td></tr>';
        return;
    }
    
    tbody.innerHTML = projectsData.slice(0, 10).map(project => {
        const deadline = new Date(project.deadline);
        const isOverdue = deadline < new Date() && project.status !== 'COMPLETED';
        const deadlineClass = isOverdue ? 'text-danger' : '';
        
        return `
            <tr>
                <td><strong>${project.name}</strong></td>
                <td>${project.owner}</td>
                <td><span class="status-badge status-${project.status.toLowerCase().replace(' ', '-')}">${project.status.replace('_', ' ')}</span></td>
                <td>
                    <div class="progress">
                        <div class="progress-bar" role="progressbar" style="width: ${project.completion_percentage}%">
                            ${project.completion_percentage}%
                        </div>
                    </div>
                </td>
                <td class="${deadlineClass}">${deadline.toLocaleDateString()}</td>
                <td>
                    <a href="/projects" class="btn btn-sm btn-outline-primary">View</a>
                </td>
            </tr>
        `;
    }).join('');
}

function exportToCSV() {
    window.location.href = '/api/export/csv';
}

// Auto-refresh every 30 seconds
setInterval(loadDashboard, 30000);

// Initial load
loadDashboard();


