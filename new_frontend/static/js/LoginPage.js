// Login page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Slow down the background video
    const bgVideo = document.querySelector('.video-background video');
    if (bgVideo) {
        // Set playback rate to 0.5 (half speed)
        bgVideo.playbackRate = 0.5;
        
        // Make sure video is playing
        bgVideo.play().catch(error => {
            console.log('Video autoplay was prevented:', error);
        });
    }

    // Handle form submission
    const studentLoginForm = document.getElementById('studentLoginForm');
    const teacherLoginForm = document.getElementById('teacherLoginForm');
    
    if (studentLoginForm) {
        studentLoginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            processLogin('student');
        });
    }
    
    if (teacherLoginForm) {
        teacherLoginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            processLogin('teacher');
        });
    }

    // Get login error parameter from URL if present
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('error') === 'invalid_login') {
        showLoginError();
    }
});

// Process login
function processLogin(userType) {
    const form = userType === 'student' ? 
        document.getElementById('studentLoginForm') : 
        document.getElementById('teacherLoginForm');
    
    const username = form.querySelector('[name="username"]').value;
    const password = form.querySelector('[name="password"]').value;
    
    // Simple validation
    if (!username || !password) {
        showLoginError('Please enter both username and password');
        return;
    }
    
    // In a real application, we would submit the form to the server
    // For demonstration, we'll simulate authentication with a timeout
    
    const loginBtn = form.querySelector('.btn-login');
    const originalBtnText = loginBtn.innerHTML;
    
    // Show loading state
    loginBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Logging in...';
    loginBtn.disabled = true;
    
    setTimeout(() => {
        // Simulate successful login for demo
        if ((userType === 'student' && username === 'student123') || 
            (userType === 'teacher' && username === 'teacher@example.com')) {
            // Redirect to main page
            window.location.href = '/dashboard';
        } else {
            // Show error
            loginBtn.innerHTML = originalBtnText;
            loginBtn.disabled = false;
            showLoginError();
        }
    }, 1500);
}

// Show login error message
function showLoginError(message) {
    const errorDiv = document.getElementById('loginError');
    if (errorDiv) {
        if (message) {
            errorDiv.textContent = message;
        }
        errorDiv.style.display = 'block';
        
        // Animate the error message
        errorDiv.style.animation = 'none';
        errorDiv.offsetHeight; // Trigger reflow
        errorDiv.style.animation = 'fadeIn 0.5s ease-out';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorDiv.style.opacity = '0';
            setTimeout(() => {
                errorDiv.style.display = 'none';
                errorDiv.style.opacity = '1';
            }, 500);
        }, 5000);
    }
}