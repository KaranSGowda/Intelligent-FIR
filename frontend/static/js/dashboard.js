/**
 * Dashboard functionality for FIR management
 */
document.addEventListener('DOMContentLoaded', function() {
    // Handle case assignment modal
    const assignCaseModal = document.getElementById('assignCaseModal');
    if (assignCaseModal) {
        assignCaseModal.addEventListener('show.bs.modal', function(event) {
            // Button that triggered the modal
            const button = event.relatedTarget;
            
            // Extract info from data attributes
            const firId = button.getAttribute('data-fir-id');
            const firNumber = button.getAttribute('data-fir-number');
            
            // Update modal content
            const modalTitle = this.querySelector('.modal-title');
            const firIdInput = this.querySelector('#assignFirId');
            
            modalTitle.textContent = `Assign Case: ${firNumber}`;
            firIdInput.value = firId;
            
            // Fetch officers list if not already loaded
            const officerSelect = this.querySelector('#officerSelect');
            if (officerSelect && officerSelect.options.length <= 1) {
                fetchOfficers(officerSelect);
            }
        });
    }
    
    // Handle status update dropdowns
    const statusDropdowns = document.querySelectorAll('.status-dropdown');
    statusDropdowns.forEach(dropdown => {
        dropdown.addEventListener('change', function() {
            const firId = this.getAttribute('data-fir-id');
            const formId = `updateStatusForm_${firId}`;
            const form = document.getElementById(formId);
            if (form) {
                form.submit();
            }
        });
    });
    
    // Charts for admin dashboard
    const statusChart = document.getElementById('statusChart');
    if (statusChart) {
        renderStatusChart(statusChart);
    }
    
    const urgencyChart = document.getElementById('urgencyChart');
    if (urgencyChart) {
        renderUrgencyChart(urgencyChart);
    }
    
    // Filter functionality for cases table
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.querySelectorAll('select').forEach(select => {
            select.addEventListener('change', function() {
                filterForm.submit();
            });
        });
    }
    
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const table = document.getElementById('casesTable');
            
            if (!table) return;
            
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }
    
    // Fetch officers for assignment dropdown
    async function fetchOfficers(selectElement) {
        try {
            const response = await fetch('/admin/get_officers');
            if (!response.ok) {
                throw new Error('Failed to fetch officers');
            }
            
            const officers = await response.json();
            
            // Clear existing options except the first one
            while (selectElement.options.length > 1) {
                selectElement.remove(1);
            }
            
            // Add officer options
            officers.forEach(officer => {
                const option = document.createElement('option');
                option.value = officer.id;
                option.textContent = officer.name;
                selectElement.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching officers:', error);
            const option = document.createElement('option');
            option.disabled = true;
            option.textContent = 'Error loading officers';
            selectElement.appendChild(option);
        }
    }
    
    // Render status distribution chart
    function renderStatusChart(canvas) {
        // Get data from data attributes
        const draftCount = parseInt(canvas.getAttribute('data-draft') || 0);
        const filedCount = parseInt(canvas.getAttribute('data-filed') || 0);
        const investigatingCount = parseInt(canvas.getAttribute('data-investigating') || 0);
        const closedCount = parseInt(canvas.getAttribute('data-closed') || 0);
        
        new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: ['Draft', 'Filed', 'Under Investigation', 'Closed'],
                datasets: [{
                    data: [draftCount, filedCount, investigatingCount, closedCount],
                    backgroundColor: ['#6c757d', '#17a2b8', '#ffc107', '#28a745']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    // Render urgency distribution chart
    function renderUrgencyChart(canvas) {
        // Get data from data attributes
        const lowCount = parseInt(canvas.getAttribute('data-low') || 0);
        const normalCount = parseInt(canvas.getAttribute('data-normal') || 0);
        const highCount = parseInt(canvas.getAttribute('data-high') || 0);
        const criticalCount = parseInt(canvas.getAttribute('data-critical') || 0);
        
        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: ['Low', 'Normal', 'High', 'Critical'],
                datasets: [{
                    label: 'Cases by Urgency',
                    data: [lowCount, normalCount, highCount, criticalCount],
                    backgroundColor: ['#28a745', '#17a2b8', '#ffc107', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
});
