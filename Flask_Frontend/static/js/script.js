/**
 * Auto Checker Evaluation System
 * Main JavaScript functionality for the evaluation interface
 */
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const elements = {
        startBtn: document.getElementById('startBtn'),
        controlArea: document.getElementById('controlArea'),
        progressArea: document.getElementById('progressArea'),
        progressBar: document.getElementById('progressBar'),
        statusMessage: document.getElementById('statusMessage'),
        errorMessage: document.getElementById('errorMessage'),
        errorText: document.getElementById('errorText'),
        resultsArea: document.getElementById('resultsArea'),
        // New elements for existing results check
        existingResultsArea: document.getElementById('existingResultsArea'),
        checkingResultsSpinner: document.getElementById('checkingResultsSpinner'),
        checkingResultsMessage: document.getElementById('checkingResultsMessage'),
        existingResultsFound: document.getElementById('existingResultsFound')
    };
    
    // Configuration
    const config = {
        statusCheckInterval: 2000, // Check status every 2 seconds
        animationDuration: 500,    // Duration for smooth progress transitions
        maxRetries: 3              // Maximum number of retries for failed requests
    };
    
    // State management
    const state = {
        intervalId: null,
        currentProgress: 0,
        retryCount: 0,
        isEvaluating: false,
        hasExistingResults: false
    };
    
    /**
     * Initialize application
     */
    function init() {
        initEventListeners();
        checkForExistingResults();
        console.log('Auto Checker UI initialized successfully');
    }
    
    /**
     * Check if there are existing evaluation results
     */
    function checkForExistingResults() {
        fetch('/check_results_exist', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            elements.checkingResultsSpinner.classList.add('hidden');
            
            if (data.exists) {
                state.hasExistingResults = true;
                elements.existingResultsFound.classList.remove('hidden');
                elements.checkingResultsMessage.textContent = 'Previous evaluation results are available.';
            } else {
                elements.checkingResultsMessage.textContent = 'No previous results found. Start a new evaluation below.';
                setTimeout(() => {
                    elements.existingResultsArea.classList.add('fade-out');
                    setTimeout(() => {
                        elements.existingResultsArea.classList.add('hidden');
                    }, 500);
                }, 1500);
            }
        })
        .catch(error => {
            elements.checkingResultsSpinner.classList.add('hidden');
            elements.checkingResultsMessage.textContent = 'Could not check for existing results.';
            console.error('Error checking for results:', error);
        });
    }
    
    /**
     * Initialize event listeners
     */
    function initEventListeners() {
        elements.startBtn.addEventListener('click', handleStartEvaluation);
        
        // Add keyboard support
        document.addEventListener('keydown', function(event) {
            // Allow pressing Enter or Space to start evaluation when button is focused
            if ((event.key === 'Enter' || event.key === ' ') && 
                document.activeElement === elements.startBtn) {
                handleStartEvaluation();
            }
        });
    }
    
    /**
     * Handle the start evaluation button click
     */
    function handleStartEvaluation() {
        if (state.isEvaluating) return;
        
        state.isEvaluating = true;
        state.retryCount = 0;
        
        // Update UI
        elements.startBtn.disabled = true;
        elements.startBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        elements.progressArea.classList.remove('hidden');
        elements.errorMessage.classList.add('hidden');
        elements.resultsArea.classList.add('hidden');
        elements.existingResultsArea.classList.add('hidden'); // Hide existing results area
        
        // Reset progress
        updateProgressBar(0);
        elements.statusMessage.textContent = 'Initializing evaluation...';
        
        // Send request to start evaluation
        fetch('/start_evaluation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'started') {
                elements.statusMessage.textContent = 'Evaluation started...';
                startStatusChecking();
            } else {
                showError(data.message || 'Failed to start evaluation');
                resetEvaluationState();
            }
        })
        .catch(error => {
            showError('Error: ' + error.message);
            resetEvaluationState();
        });
    }
    
    /**
     * Start periodic status checking
     */
    function startStatusChecking() {
        // Clear any existing interval
        stopStatusChecking();
        
        // Check status periodically
        state.intervalId = setInterval(checkStatus, config.statusCheckInterval);
        
        // Check immediately
        checkStatus();
    }
    
    /**
     * Check the current evaluation status
     */
    function checkStatus() {
        fetch('/status')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server responded with status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Reset retry counter on successful response
                state.retryCount = 0;
                
                // Update progress bar with smooth animation
                if (typeof data.progress === 'number') {
                    animateProgressTo(data.progress);
                }
                
                // Update status message
                if (data.message) {
                    elements.statusMessage.textContent = data.message;
                }
                
                // Check for errors
                if (data.error) {
                    showError(data.error);
                    resetEvaluationState();
                    return;
                }
                
                // Check if complete
                if (data.complete) {
                    animateProgressTo(100);
                    elements.statusMessage.textContent = 'Evaluation completed successfully!';
                    elements.resultsArea.classList.remove('hidden');
                    
                    // Add a small animation to the success area
                    const successIcon = elements.resultsArea.querySelector('.success-icon');
                    if (successIcon) {
                        successIcon.classList.add('animate__animated', 'animate__bounceIn');
                    }
                    
                    // Update state to show we have results
                    state.hasExistingResults = true;
                    
                    resetEvaluationState();
                    return;
                }
                
                // If not running and not complete, something went wrong
                if (!data.running && !data.complete && !data.error) {
                    showError('Evaluation process stopped unexpectedly');
                    resetEvaluationState();
                }
            })
            .catch(error => {
                state.retryCount++;
                
                if (state.retryCount <= config.maxRetries) {
                    console.warn(`Status check failed (attempt ${state.retryCount}/${config.maxRetries}): ${error.message}`);
                    elements.statusMessage.textContent = `Connection issue, retrying (${state.retryCount}/${config.maxRetries})...`;
                } else {
                    showError('Failed to check status: ' + error.message);
                    resetEvaluationState();
                }
            });
    }
    
    /**
     * Animate the progress bar to the target value
     * @param {number} targetProgress - The target progress value (0-100)
     */
    function animateProgressTo(targetProgress) {
        // Ensure values are within bounds
        targetProgress = Math.min(Math.max(targetProgress, 0), 100);
        const currentProgress = state.currentProgress;
        
        // Don't animate if no change or if jumping to 100%
        if (currentProgress === targetProgress || targetProgress === 100) {
            updateProgressBar(targetProgress);
            state.currentProgress = targetProgress;
            return;
        }
        
        // Calculate increment for smooth animation
        const startTime = performance.now();
        
        function animate(currentTime) {
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / config.animationDuration, 1);
            const currentValue = currentProgress + progress * (targetProgress - currentProgress);
            
            updateProgressBar(currentValue);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                state.currentProgress = targetProgress;
            }
        }
        
        requestAnimationFrame(animate);
    }
    
    /**
     * Update the progress bar display
     * @param {number} progress - The progress value (0-100)
     */
    function updateProgressBar(progress) {
        // If progress is not a number, use indeterminate progress
        if (isNaN(progress)) {
            elements.progressBar.style.width = '100%';
            elements.progressBar.textContent = 'Processing...';
            elements.progressBar.classList.add('progress-bar-animated');
        } else {
            const value = Math.min(Math.max(Math.round(progress), 0), 100);
            elements.progressBar.style.width = value + '%';
            elements.progressBar.textContent = value + '%';
            elements.progressBar.setAttribute('aria-valuenow', value);
            
            // Add color classes based on progress
            elements.progressBar.classList.remove('bg-danger', 'bg-warning', 'bg-info', 'bg-success');
            
            if (value < 25) {
                elements.progressBar.classList.add('bg-danger');
            } else if (value < 50) {
                elements.progressBar.classList.add('bg-warning');
            } else if (value < 75) {
                elements.progressBar.classList.add('bg-info');
            } else {
                elements.progressBar.classList.add('bg-success');
            }
        }
    }
    
    /**
     * Display an error message
     * @param {string} message - The error message to display
     */
    function showError(message) {
        elements.errorText.textContent = message;
        elements.errorMessage.classList.remove('hidden');
    }
    
    /**
     * Stop the status checking interval
     */
    function stopStatusChecking() {
        if (state.intervalId) {
            clearInterval(state.intervalId);
            state.intervalId = null;
        }
    }
    
    /**
     * Reset the evaluation state
     */
    function resetEvaluationState() {
        stopStatusChecking();
        state.isEvaluating = false;
        elements.startBtn.disabled = false;
        elements.startBtn.innerHTML = '<i class="fas fa-play-circle me-2"></i>Start New Evaluation';
        
        // Show existing results area if we have results now
        if (state.hasExistingResults) {
            elements.existingResultsArea.classList.remove('hidden');
            elements.checkingResultsSpinner.classList.add('hidden');
            elements.checkingResultsMessage.textContent = 'Previous evaluation results are available.';
            elements.existingResultsFound.classList.remove('hidden');
        }
    }
    
    // Initialize the application
    init();
});