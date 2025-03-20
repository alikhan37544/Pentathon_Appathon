// Tab functionality
function initTabs() {
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and panes
            document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked button
            button.classList.add('active');
            
            // Show corresponding tab pane
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
}

// File Upload Functionality
function initFileUpload() {
    const dropArea = document.getElementById('dropArea');
    const fileInput = document.getElementById('fileInput');
    const browseLink = document.getElementById('browseLink');
    const filesList = document.getElementById('filesList');
    const processButton = document.getElementById('processButton');
    const loader = document.getElementById('loader');
    const resultContainer = document.getElementById('resultContainer');
    const resultDiv = document.getElementById('result');
    
    // Click browse link to trigger file input
    if (browseLink) {
        browseLink.addEventListener('click', () => {
            fileInput.click();
        });
    }
    
    // Handle file selection from input
    if (fileInput) {
        fileInput.addEventListener('change', handleFiles);
    }
    
    // Handle drag and drop events
    if (dropArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });
        
        dropArea.addEventListener('drop', handleDrop, false);
    }
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight() {
        dropArea.classList.add('active');
    }
    
    function unhighlight() {
        dropArea.classList.remove('active');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles({ files });
    }
    
    function handleFiles(files) {
        files = files.files || files; // Support both input change event and drop files
        if (!files || files.length === 0) return;
        
        // Clear existing files
        filesList.innerHTML = '';
        
        Array.from(files).forEach(file => {
            // Check if file is an image
            if (!file.type.match('image.*')) {
                alert('Please upload image files only.');
                return;
            }
            
            // Check file size
            if (file.size > 90 * 1024 * 1024) { // 90MB in bytes
                alert('File size exceeds 90MB limit.');
                return;
            }
            
            // Add file to list
            addFileToList(file);
        });
    }
    
    function addFileToList(file) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        const extension = file.name.split('.').pop().toUpperCase();
        const fileSize = formatFileSize(file.size);
        
        fileItem.innerHTML = `
            <div class="file-icon">
                ${extension}
            </div>
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-size">${fileSize}</div>
                <div class="file-progress">
                    <div class="progress-bar" style="width: 0%"></div>
                </div>
            </div>
            <div class="file-status status-ready">Ready</div>
            <div class="file-actions">
                <button type="button" class="remove-file">×</button>
            </div>
        `;
        
        filesList.appendChild(fileItem);
        
        // Add remove functionality
        fileItem.querySelector('.remove-file').addEventListener('click', () => {
            fileItem.remove();
            if (filesList.children.length === 0) {
                fileInput.value = ''; // Reset the file input
            }
        });
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Process button click
    if (processButton) {
        processButton.addEventListener('click', () => {
            if (!filesList || filesList.children.length === 0) {
                alert('Please upload at least one image first.');
                return;
            }
            
            // Show loader
            if (loader) loader.style.display = 'block';
            if (resultContainer) resultContainer.classList.add('hidden');
            
            // Get the file from the file list
            const fileItem = filesList.children[0];
            const progressBar = fileItem.querySelector('.progress-bar');
            const statusElement = fileItem.querySelector('.file-status');
            
            // Update progress for visual feedback
            let progress = 0;
            statusElement.textContent = 'Processing...';
            statusElement.className = 'file-status status-processing';
            
            const progressInterval = setInterval(() => {
                progress += 5;
                if (progress > 90) clearInterval(progressInterval);
                progressBar.style.width = `${progress}%`;
            }, 200);
            
            // Create FormData and append the file
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            
            // Send OCR request
            fetch('/fancyocr', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                clearInterval(progressInterval);
                
                // Hide loader
                if (loader) loader.style.display = 'none';
                
                // Update progress to 100%
                progressBar.style.width = '100%';
                
                if (data.error) {
                    statusElement.textContent = 'Error';
                    statusElement.className = 'file-status status-error';
                    resultDiv.textContent = 'Error: ' + data.error;
                } else {
                    statusElement.textContent = 'Complete';
                    statusElement.className = 'file-status status-complete';
                    resultDiv.textContent = data.text;
                }
                
                // Show results
                if (resultContainer) resultContainer.classList.remove('hidden');
            })
            .catch(error => {
                clearInterval(progressInterval);
                if (loader) loader.style.display = 'none';
                progressBar.style.width = '100%';
                statusElement.textContent = 'Error';
                statusElement.className = 'file-status status-error';
                resultDiv.textContent = 'Error: ' + error.message;
                if (resultContainer) resultContainer.classList.remove('hidden');
            });
        });
    }
}

// Ollama Chat Functionality
function initChat() {
    const messageContainer = document.getElementById('messageContainer');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    
    if (!messageContainer || !messageInput || !sendButton) return;
    
    sendButton.addEventListener('click', sendMessage);
    
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    function sendMessage() {
        const message = messageInput.value.trim();
        if (message === '') return;
        
        // Add user message
        addChatMessage(message, 'user-message');
        messageInput.value = '';
        
        // Simulate Ollama response (would be replaced with actual API call)
        setTimeout(() => {
            const response = "This is a placeholder response. In a real implementation, this would connect to the Ollama API to get actual responses.";
            addChatMessage(response, 'bot-message');
        }, 1000);
    }
    
    function addChatMessage(text, className) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${className}`;
        messageElement.textContent = text;
        messageContainer.appendChild(messageElement);
        
        // Scroll to bottom
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }
}

// Initialize the page functionality when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tabs if they exist
    initTabs();
    
    // Initialize file upload functionality if elements exist
    initFileUpload();
    
    // Initialize chat functionality if elements exist
    initChat();
});