// GmailCat PDA - Interactive JavaScript

class GmailCatApp {
    constructor() {
        this.processBtn = document.getElementById('processBtn');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.resultsPanel = document.getElementById('resultsPanel');
        this.resultsContent = document.getElementById('resultsContent');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.toastContainer = document.getElementById('toastContainer');
        
        this.init();
    }
    
    init() {
        this.processBtn.addEventListener('click', () => this.processEmails());
        this.updateStatus('Ready to process your emails', 'info');
    }
    
    async processEmails() {
        try {
            this.showLoading();
            this.processBtn.disabled = true;
            this.updateStatus('Processing emails...', 'warning');
            
            // Simulate loading steps
            await this.animateLoadingSteps();
            
            const response = await fetch('/run-agent/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({})
            });
            
            const data = await response.json();
            
            this.hideLoading();
            this.processBtn.disabled = false;
            
            if (data.status === 'success') {
                this.displayResults(data.data);
                this.updateStatus('Processing completed successfully!', 'success');
                this.showToast('Success!', 'Emails processed and calendar events created.', 'success');
            } else {
                this.updateStatus('Processing failed. Please try again.', 'error');
                this.showToast('Error', data.message || 'An unknown error occurred.', 'error');
            }
            
        } catch (error) {
            this.hideLoading();
            this.processBtn.disabled = false;
            this.updateStatus('Network error. Please check your connection.', 'error');
            this.showToast('Network Error', 'Failed to connect to the server.', 'error');
            console.error('Error:', error);
        }
    }
    
    async animateLoadingSteps() {
        const steps = ['step1', 'step2', 'step3', 'step4'];
        
        for (let i = 0; i < steps.length; i++) {
            await this.sleep(1000);
            
            // Mark current step as active
            const currentStep = document.getElementById(steps[i]);
            if (currentStep) {
                currentStep.classList.add('active');
                const icon = currentStep.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-spinner fa-spin';
                }
            }
            
            await this.sleep(1500);
            
            // Mark current step as completed
            if (currentStep) {
                currentStep.classList.remove('active');
                currentStep.classList.add('completed');
                const icon = currentStep.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-check-circle';
                }
            }
        }
    }
    
    displayResults(data) {
        this.resultsPanel.style.display = 'block';
        
        let html = '';
        
        if (data.status === 'complete') {
            html += `
                <div class="result-summary">
                    <div class="summary-stats">
                        <div class="stat-item">
                            <i class="fas fa-envelope"></i>
                            <div>
                                <div class="stat-number">5</div>
                                <div class="stat-label">Emails Scanned</div>
                            </div>
                        </div>
                        <div class="stat-item">
                            <i class="fas fa-calendar-plus"></i>
                            <div>
                                <div class="stat-number">${data.events_created || 0}</div>
                                <div class="stat-label">Events Created</div>
                            </div>
                        </div>
                        <div class="stat-item">
                            <i class="fas fa-clock"></i>
                            <div>
                                <div class="stat-number">${new Date().toLocaleTimeString()}</div>
                                <div class="stat-label">Completed At</div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            if (data.links && data.links.length > 0) {
                html += '<div class="events-list">';
                html += '<h3><i class="fas fa-calendar-check"></i> Created Events</h3>';
                
                data.links.forEach((link, index) => {
                    html += `
                        <div class="result-item">
                            <div class="result-title">
                                <i class="fas fa-calendar-alt"></i>
                                Calendar Event ${index + 1}
                            </div>
                            <div class="result-details">
                                Successfully created and added to your Google Calendar
                            </div>
                            <a href="${link}" class="result-link" target="_blank">
                                <i class="fas fa-external-link-alt"></i>
                                View in Google Calendar
                            </a>
                        </div>
                    `;
                });
                
                html += '</div>';
            } else if (data.message) {
                html += `
                    <div class="result-item">
                        <div class="result-title">
                            <i class="fas fa-info-circle"></i>
                            ${data.message}
                        </div>
                    </div>
                `;
            }
        }
        
        this.resultsContent.innerHTML = html;
        
        // Scroll to results
        this.resultsPanel.scrollIntoView({ behavior: 'smooth' });
    }
    
    updateStatus(message, type = 'info') {
        this.statusIndicator.className = `status-indicator ${type}`;
        
        let icon = 'fas fa-info-circle';
        if (type === 'success') icon = 'fas fa-check-circle';
        else if (type === 'error') icon = 'fas fa-exclamation-circle';
        else if (type === 'warning') icon = 'fas fa-clock';
        
        this.statusIndicator.innerHTML = `
            <i class="${icon}"></i>
            <span>${message}</span>
        `;
    }
    
    showLoading() {
        this.loadingOverlay.style.display = 'flex';
        
        // Reset all steps
        const steps = document.querySelectorAll('.step');
        steps.forEach(step => {
            step.classList.remove('active', 'completed');
            const icon = step.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-clock';
            }
        });
    }
    
    hideLoading() {
        this.loadingOverlay.style.display = 'none';
    }
    
    showToast(title, message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let icon = 'fas fa-check-circle';
        if (type === 'error') icon = 'fas fa-exclamation-circle';
        else if (type === 'warning') icon = 'fas fa-exclamation-triangle';
        
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="${icon}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
        `;
        
        this.toastContainer.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slideIn 0.3s ease reverse';
                setTimeout(() => {
                    if (toast.parentNode) {
                        this.toastContainer.removeChild(toast);
                    }
                }, 300);
            }
        }, 5000);
    }
    
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        // Fallback: try to get from meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.getAttribute('content') : '';
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Additional CSS for new elements
const additionalCSS = `
.result-summary {
    margin-bottom: 2rem;
}

.summary-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.stat-item {
    background: var(--bg-secondary);
    padding: 1.5rem;
    border-radius: var(--radius-lg);
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
}

.stat-item i {
    font-size: 2rem;
    color: var(--primary-color);
}

.stat-number {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
}

.stat-label {
    font-size: 0.875rem;
    color: var(--text-secondary);
    font-weight: 500;
}

.events-list h3 {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    color: var(--text-primary);
    font-size: 1.25rem;
}

.events-list h3 i {
    color: var(--success-color);
}

.result-item .result-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.result-item .result-title i {
    color: var(--primary-color);
}

@media (max-width: 768px) {
    .summary-stats {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .stat-item {
        flex-direction: row;
        text-align: left;
    }
}
`;

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add additional CSS
    const style = document.createElement('style');
    style.textContent = additionalCSS;
    document.head.appendChild(style);
    
    // Initialize the app
    new GmailCatApp();
    
    // Add some nice entrance animations
    const elements = document.querySelectorAll('.feature-card, .action-panel');
    elements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            el.style.transition = 'all 0.6s ease';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 100 * (index + 1));
    });
});
