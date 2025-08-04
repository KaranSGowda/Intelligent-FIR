/**
 * Login form functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Login script loaded');
    const loginForm = document.querySelector('form[action*="login"]');
    
    if (loginForm) {
        console.log('Login form found:', loginForm);
        
        // Add event listener to the form submission
        loginForm.addEventListener('submit', function(e) {
            console.log('Form submitted');
            // We'll let the form submit normally without preventing default
            // This ensures the server-side redirect works properly
            
            // Show loading indicator
            const loadingOverlay = document.getElementById('loadingOverlay');
            if (loadingOverlay) {
                loadingOverlay.style.display = 'flex';
                loadingOverlay.style.opacity = '1';
            }
            
            // Get form data for validation only
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            
            // Basic validation
            if (!username || !password) {
                e.preventDefault(); // Only prevent default if validation fails
                showAlert('Please enter both username and password', 'danger');
                return false;
            }
            
            // Let the form submit normally
            return true;
        });
    } else {
        console.warn('Login form not found');
    }
    
    // Function to show alert messages
    function showAlert(message, type) {
        // Check if an alert container already exists
        let alertContainer = document.querySelector('.login-alert-container');
        
        // If not, create one
        if (!alertContainer) {
            alertContainer = document.createElement('div');
            alertContainer.className = 'login-alert-container';
            const cardBody = document.querySelector('.card-body');
            cardBody.insertBefore(alertContainer, cardBody.firstChild);
        }
        
        // Create the alert
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Add the alert to the container
        alertContainer.innerHTML = '';
        alertContainer.appendChild(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    }
});