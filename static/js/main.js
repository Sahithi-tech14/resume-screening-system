/**
 * Main JavaScript File for AI-Powered Resume Screening System
 *
 * This file contains client-side functionality for:
 * - Form validation
 * - Dynamic content updates
 * - Chart configurations
 * - User interactions
 *
 * INTERVIEW PREPARATION:
 *
 * Q: Why use client-side validation alongside server-side?
 * A: Client-side validation provides immediate feedback to users
 *    without server round-trips. Server-side validation is required
 *    for security since JavaScript can be bypassed.
 *
 * Q: What is async/await?
 * A: It's modern JavaScript syntax for handling asynchronous operations.
 *    Makes code look synchronous while handling promises.
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Resume Screening System initialized');

    // Initialize tooltips
    initializeTooltips();

    // Initialize form validation
    initializeFormValidation();

    // Initialize alerts auto-dismiss
    initializeAlerts();
});


/**
 * Initialize Bootstrap tooltips
 * Tooltips provide helpful hints on hover
 */
function initializeTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
}


/**
 * Initialize form validation
 * Provides real-time feedback for form inputs
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        // Add validation on input
        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                validateInput(this);
            });

            // Also validate on blur
            input.addEventListener('blur', function() {
                validateInput(this);
            });
        });

        // Form submission validation
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();

                // Highlight invalid fields
                inputs.forEach(input => {
                    validateInput(input);
                });
            }
        });
    });
}


/**
 * Validate a single input field
 * Uses HTML5 validation API
 *
 * @param {HTMLInputElement} input - The input element to validate
 */
function validateInput(input) {
    const formGroup = input.closest('.mb-3') || input.closest('.mb-4');
    if (!formGroup) return;

    // Check validity
    if (input.validity.valid) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');

        // Update feedback
        let feedback = formGroup.querySelector('.valid-feedback');
        if (!feedback && input.type !== 'checkbox') {
            feedback = document.createElement('div');
            feedback.className = 'valid-feedback';
            feedback.textContent = 'Looks good!';
            formGroup.appendChild(feedback);
        }
    } else if (input.value) {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');

        // Update feedback
        let feedback = formGroup.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';

            // Custom error messages
            if (input.validity.valueMissing) {
                feedback.textContent = 'This field is required.';
            } else if (input.validity.typeMismatch) {
                feedback.textContent = 'Please enter a valid value.';
            } else if (input.validity.tooShort) {
                feedback.textContent = `Minimum ${input.minLength} characters required.`;
            } else if (input.validity.patternMismatch) {
                feedback.textContent = 'Please match the requested format.';
            }

            formGroup.appendChild(feedback);
        }
    } else {
        input.classList.remove('is-valid', 'is-invalid');
    }
}


/**
 * Initialize alert auto-dismiss
 * Automatically closes success alerts after 5 seconds
 */
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert-success, .alert-info');

    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}


/**
 * Format file size to human-readable format
 *
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}


/**
 * Show loading spinner
 * Used during API calls or file uploads
 *
 * @param {HTMLElement} element - Element to show spinner in
 */
function showLoading(element) {
    const originalContent = element.innerHTML;
    element.dataset.originalContent = originalContent;
    element.disabled = true;
    element.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status"></span>
        Loading...
    `;
}


/**
 * Hide loading spinner and restore original content
 *
 * @param {HTMLElement} element - Element to restore
 */
function hideLoading(element) {
    if (element.dataset.originalContent) {
        element.innerHTML = element.dataset.originalContent;
        element.disabled = false;
    }
}


/**
 * Show toast notification
 *
 * @param {string} message - Message to display
 * @param {string} type - Type of toast (success, error, warning, info)
 */
function showToast(message, type = 'info') {
    // Create toast container if not exists
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }

    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type}" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', toastHtml);

    // Show toast
    const toastEl = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastEl, { autohide: true, delay: 4000 });
    toast.show();

    // Remove toast after hidden
    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}


/**
 * Debounce function
 * Limits how often a function can be called
 *
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}


/**
 * Charts configuration
 * These settings customize Chart.js appearance
 */
const ChartConfig = {
    // Default colors for charts
    colors: {
        primary: 'rgba(13, 110, 253, 0.8)',
        success: 'rgba(25, 135, 84, 0.8)',
        warning: 'rgba(255, 193, 7, 0.8)',
        danger: 'rgba(220, 53, 69, 0.8)',
        info: 'rgba(13, 202, 240, 0.8)',
        gray: 'rgba(108, 117, 125, 0.8)'
    },

    // Default chart options
    getDefaults: function() {
        return {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        };
    }
};


/**
 * Create a bar chart
 *
 * @param {string} canvasId - ID of the canvas element
 * @param {Object} data - Chart data
 * @returns {Chart} The created chart
 */
function createBarChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            ...ChartConfig.getDefaults(),
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}


/**
 * Create a doughnut chart
 *
 * @param {string} canvasId - ID of the canvas element
 * @param {Object} data - Chart data
 * @returns {Chart} The created chart
 */
function createDoughnutChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            ...ChartConfig.getDefaults(),
            cutout: '70%'
        }
    });
}


/**
 * Update progress bars with animation
 *
 * @param {string} selector - Selector for progress bars
 * @param {number} percent - Percentage to fill
 */
function updateProgressBar(selector, percent) {
    const progressBar = document.querySelector(selector);
    if (progressBar) {
        var width = 0;
        const id = setInterval(frame, 20);

        function frame() {
            if (width >= percent) {
                clearInterval(id);
            } else {
                width++;
                progressBar.style.width = width + '%';
                progressBar.setAttribute('aria-valuenow', width);
            }
        }
    }
}


// Export functions for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatFileSize,
        showLoading,
        hideLoading,
        showToast,
        debounce,
        createBarChart,
        createDoughnutChart,
        updateProgressBar
    };
}
