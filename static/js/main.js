// Main JavaScript for Factory ERP

// Global variables
let currentUser = null;
let userRole = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    checkAuthStatus();
    
    // Initialize forms
    initializeForms();
    
    // Initialize charts if on dashboard
    if (document.getElementById('productionChart')) {
        initializeCharts();
    }
});

function checkAuthStatus() {
    // Check for stored auth token
    const token = localStorage.getItem('authToken');
    if (token) {
        // Verify token and set user info
        // This would normally make an API call to verify the token
        currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
        userRole = localStorage.getItem('userRole') || 'staff';
    }
}

function initializeForms() {
    // Production form
    const productionForm = document.getElementById('productionForm');
    if (productionForm) {
        productionForm.addEventListener('submit', handleProductionSubmit);
        
        // Auto-calculate fields
        const actualInput = document.getElementById('actual');
        const targetInput = document.getElementById('target');
        const inputMaterialInput = document.getElementById('input_material');
        const outputMaterialInput = document.getElementById('output_material');
        
        if (actualInput && targetInput) {
            actualInput.addEventListener('input', calculateOvertime);
        }
        
        if (inputMaterialInput && outputMaterialInput) {
            inputMaterialInput.addEventListener('input', calculateWastage);
            outputMaterialInput.addEventListener('input', calculateWastage);
        }
    }
    
    // Attendance form
    const attendanceForm = document.getElementById('attendanceForm');
    if (attendanceForm) {
        attendanceForm.addEventListener('submit', handleAttendanceSubmit);
    }
    
    // Downtime form
    const downtimeForm = document.getElementById('downtimeForm');
    if (downtimeForm) {
        downtimeForm.addEventListener('submit', handleDowntimeSubmit);
    }
    
    // Requisition form
    const requisitionForm = document.getElementById('requisitionForm');
    if (requisitionForm) {
        requisitionForm.addEventListener('submit', handleRequisitionSubmit);
    }
}

function calculateOvertime() {
    const actual = parseInt(document.getElementById('actual').value) || 0;
    const target = parseInt(document.getElementById('target').value) || 0;
    
    if (actual > target && target > 0) {
        const overtimeHours = ((actual - target) / (target / 8)).toFixed(2);
        document.getElementById('overtime_hours').value = overtimeHours;
    } else {
        document.getElementById('overtime_hours').value = '0.00';
    }
}

function calculateWastage() {
    const inputMaterial = parseFloat(document.getElementById('input_material').value) || 0;
    const outputMaterial = parseFloat(document.getElementById('output_material').value) || 0;
    
    const wastage = (inputMaterial - outputMaterial).toFixed(2);
    document.getElementById('wastage').value = wastage;
}

function handleProductionSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    
    // Validate material flow
    if (parseFloat(data.output_material) > parseFloat(data.input_material)) {
        alert('Output material cannot exceed input material!');
        return;
    }
    
    // Submit to API
    fetch('/api/production', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Production data saved successfully!');
            event.target.reset();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while saving data.');
    });
}

function handleAttendanceSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const selectedWorkers = formData.getAll('workers');
    
    if (selectedWorkers.length === 0) {
        alert('Please select at least one worker.');
        return;
    }
    
    const data = {
        workers: selectedWorkers,
        date: formData.get('date')
    };
    
    fetch('/api/attendance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Attendance saved successfully!');
            event.target.reset();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while saving attendance.');
    });
}

function handleDowntimeSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    
    fetch('/api/downtime', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Downtime recorded successfully!');
            event.target.reset();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while recording downtime.');
    });
}

function handleRequisitionSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    
    fetch('/api/requisition', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Requisition submitted successfully!');
            event.target.reset();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while submitting requisition.');
    });
}

function initializeCharts() {
    // Production Chart
    const productionCtx = document.getElementById('productionChart');
    if (productionCtx) {
        fetch('/api/reports/production')
            .then(response => response.json())
            .then(data => {
                new Chart(productionCtx, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Target',
                            data: data.targets,
                            backgroundColor: 'rgba(54, 162, 235, 0.5)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        }, {
                            label: 'Actual',
                            data: data.actuals,
                            backgroundColor: data.actuals.map((actual, index) => 
                                actual < data.targets[index] ? 'rgba(255, 99, 132, 0.5)' : 'rgba(75, 192, 192, 0.5)'
                            ),
                            borderColor: data.actuals.map((actual, index) => 
                                actual < data.targets[index] ? 'rgba(255, 99, 132, 1)' : 'rgba(75, 192, 192, 1)'
                            ),
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            })
            .catch(error => console.error('Error loading production chart:', error));
    }
}

// Utility functions
function formatDate(date) {
    return new Date(date).toLocaleDateString();
}

function formatTime(time) {
    return new Date(time).toLocaleTimeString();
}

function showWorkerHistory(workerId) {
    fetch(`/api/worker_history/${workerId}`)
        .then(response => response.json())
        .then(data => {
            // Create modal or popup to show worker history
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Worker Production History</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Item</th>
                                        <th>Target</th>
                                        <th>Actual</th>
                                        <th>Efficiency</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${data.history.map(record => `
                                        <tr>
                                            <td>${formatDate(record.date)}</td>
                                            <td>${record.item_name}</td>
                                            <td>${record.target}</td>
                                            <td>${record.actual}</td>
                                            <td>${((record.actual / record.target) * 100).toFixed(1)}%</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            new bootstrap.Modal(modal).show();
        })
        .catch(error => console.error('Error loading worker history:', error));
}

function approveRequisition(requisitionId, action) {
    const remarks = prompt(`Enter remarks for ${action}:`);
    
    fetch(`/api/requisition/${requisitionId}/${action}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({ remarks: remarks })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Requisition ${action}d successfully!`);
            location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred.');
    });
}

