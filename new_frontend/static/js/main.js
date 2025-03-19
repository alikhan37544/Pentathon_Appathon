// Helper function to show alerts
function showAlert(message, type = "success") {
  const alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;

  document.getElementById("alertContainer").appendChild(alertDiv);

  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    alertDiv.classList.remove("show");
    setTimeout(() => alertDiv.remove(), 150);
  }, 5000);
}

// Document Ready Function
document.addEventListener("DOMContentLoaded", function () {
  // Add animations on page load
  animateElements();
  
  // Setup drag and drop file upload
  setupDragAndDrop();
  
  // Document Functionality
  setupDocumentFunctionality();

  // Transcript Functionality
  setupTranscriptFunctionality();

  // Hide all loading indicators initially
  document.querySelectorAll(".loading").forEach((el) => {
    el.style.display = "none";
  });
  
  // Set active tab based on URL hash if present
  const hash = window.location.hash;
  if (hash === '#video-transcripts') {
    const transcriptTab = document.getElementById('transcript-tab');
    if (transcriptTab) {
      const tabInstance = new bootstrap.Tab(transcriptTab);
      tabInstance.show();
    }
  }
  
  // Update hash when tabs are changed
  const tabs = document.querySelectorAll('button[data-bs-toggle="tab"]');
  tabs.forEach(tab => {
    tab.addEventListener('shown.bs.tab', function (e) {
      if (e.target.id === 'transcript-tab') {
        window.location.hash = 'video-transcripts';
        // Re-trigger animations when tab changes
        setTimeout(animateElements, 50);
      } else {
        window.location.hash = 'document-database';
        // Re-trigger animations when tab changes
        setTimeout(animateElements, 50);
      }
      
      // Hide results when switching tabs
      document.getElementById('noResultsMessage').style.display = 'block';
      document.getElementById('noVideoResultsMessage').style.display = 'block';
      document.getElementById('queryDocumentsResults').style.display = 'none';
      document.getElementById('populateOutput').style.display = 'none';
      document.getElementById('videoInfo').style.display = 'none';
      document.getElementById('videoSegments').style.display = 'none';
      document.getElementById('transcriptResults').style.display = 'none';
    });
  });
});

// Function to re-run animations
function animateElements() {
  // Remove animation classes
  document.querySelectorAll('.slide-left, .slide-right, .fade-in').forEach(el => {
    el.style.animation = 'none';
    el.offsetHeight; // Trigger reflow
    el.style.animation = '';
  });
  
  // Re-add animation classes
  document.querySelectorAll('.slide-left').forEach((el, index) => {
    el.style.animationDelay = `${0.1 * index}s`;
  });
  
  document.querySelectorAll('.slide-right').forEach((el, index) => {
    el.style.animationDelay = `${0.1 * index}s`;
  });
}

function setupDragAndDrop() {
  const dropArea = document.getElementById('dropArea');
  const fileInput = document.getElementById('file');
  const uploadList = document.getElementById('uploadList');
  
  if (!dropArea || !fileInput) return;
  
  // Click on drop area to open file browser
  dropArea.addEventListener('click', () => {
    fileInput.click();
  });
  
  // File input change event
  fileInput.addEventListener('change', (e) => {
    if (fileInput.files.length > 0) {
      updateUploadPreview(fileInput.files);
    }
  });
  
  // Prevent default drag behaviors
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });
  
  // Highlight drop area when item is dragged over it
  ['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false);
  });
  
  // Remove highlight when item is dragged out or dropped
  ['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false);
  });
  
  // Handle dropped files
  dropArea.addEventListener('drop', handleDrop, false);
  
  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }
  
  function highlight() {
    dropArea.classList.add('drag-over');
  }
  
  function unhighlight() {
    dropArea.classList.remove('drag-over');
  }
  
  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
      fileInput.files = files;
      updateUploadPreview(files);
    }
  }
  
  function updateUploadPreview(files) {
    // Hide the drop area
    dropArea.style.display = 'none';
    
    // Show the upload list
    uploadList.style.display = 'block';
    uploadList.innerHTML = '';
    
    // Create a file item for each file
    Array.from(files).forEach((file, index) => {
      const fileExt = file.name.split('.').pop().toLowerCase();
      const fileItem = document.createElement('div');
      fileItem.className = 'upload-item slide-right';
      fileItem.style.animationDelay = `${0.1 * index}s`;
      
      // Randomly generate a progress value between 30-90% for visual effect
      const progressValue = Math.floor(Math.random() * 60) + 30;
      
      fileItem.innerHTML = `
        <div class="upload-item-icon">
          <i class="bi bi-file-earmark-${getIconType(fileExt)}"></i>
        </div>
        <div class="upload-item-details">
          <div class="upload-item-name">${file.name}</div>
          <div class="upload-item-status">Uploading...</div>
          <div class="upload-item-progress">
            <div class="upload-item-progress-bar" style="width: ${progressValue}%"></div>
          </div>
        </div>
        <div class="upload-item-actions">
          <div class="upload-item-percentage">${progressValue}%</div>
          <div class="upload-item-close" data-index="${index}">
            <i class="bi bi-x"></i>
          </div>
        </div>
      `;
      
      uploadList.appendChild(fileItem);
      
      // Simulate progress animation
      animateProgress(fileItem.querySelector('.upload-item-progress-bar'), progressValue, 100);
    });
    
    // Add click event to close buttons
    document.querySelectorAll('.upload-item-close').forEach(closeBtn => {
      closeBtn.addEventListener('click', (e) => {
        const index = parseInt(e.currentTarget.getAttribute('data-index'));
        // We can't directly remove files from the FileList, so we'd need to recreate it
        // For now, just removing the visual element
        const item = e.currentTarget.closest('.upload-item');
        
        // Add exit animation
        item.style.animation = 'slideOutRight 0.3s forwards';
        
        setTimeout(() => {
          item.remove();
          
          // If all files are removed, show the drop area again
          if (uploadList.children.length === 0) {
            uploadList.style.display = 'none';
            dropArea.style.display = 'block';
          }
        }, 300);
      });
    });
  }
  
  function getIconType(extension) {
    const iconMap = {
      'pdf': 'pdf',
      'doc': 'word',
      'docx': 'word',
      'xls': 'excel',
      'xlsx': 'excel',
      'ppt': 'powerpoint',
      'pptx': 'powerpoint',
      'txt': 'text',
      'csv': 'text',
      'json': 'code',
      'xml': 'code'
    };
    
    return iconMap[extension] || 'text';
  }
  
  function animateProgress(progressBar, startValue, endValue) {
    const duration = 1500; // Animation duration in ms
    const startTime = performance.now();
    
    function updateProgress(currentTime) {
      const elapsedTime = currentTime - startTime;
      const progress = Math.min(elapsedTime / duration, 1);
      const currentValue = startValue + (endValue - startValue) * progress;
      
      progressBar.style.width = `${currentValue}%`;
      progressBar.parentElement.parentElement.querySelector('.upload-item-percentage').textContent = `${Math.round(currentValue)}%`;
      
      if (progress < 1) {
        requestAnimationFrame(updateProgress);
      } else {
        // When progress reaches 100%, update status
        progressBar.parentElement.parentElement.querySelector('.upload-item-status').textContent = 'Ready to submit';
        progressBar.parentElement.parentElement.querySelector('.upload-item-status').classList.add('success');
      }
    }
    
    requestAnimationFrame(updateProgress);
  }
  
  // Handle form submission
  const uploadForm = document.getElementById('uploadForm');
  if (uploadForm) {
    uploadForm.addEventListener('submit', function(e) {
      // We don't prevent default here to allow the form to submit normally
      // But we could add loading indicators or other visual feedback
      
      // Reset the UI after form is submitted
      setTimeout(() => {
        uploadList.style.display = 'none';
        dropArea.style.display = 'block';
      }, 500);
    });
  }
}

function setupDocumentFunctionality() {
  // Populate database button
  const populateBtn = document.getElementById("populateBtn");
  if (populateBtn) {
    populateBtn.addEventListener("click", function () {
      const loadingDiv = document.getElementById("populateLoading");
      const outputDiv = document.getElementById("populateOutput");
      const noResultsMessage = document.getElementById("noResultsMessage");

      loadingDiv.style.display = "block";
      outputDiv.style.display = "none";
      noResultsMessage.style.display = "none";

      fetch("/populate_database", {
        method: "POST",
      })
        .then((response) => response.json())
        .then((data) => {
          loadingDiv.style.display = "none";
          outputDiv.style.display = "block";

          if (data.success) {
            showAlert("Database populated successfully", "success");
            outputDiv.innerHTML =
              '<div class="text-success fw-bold">Database populated successfully!</div>';
            if (data.output) {
              outputDiv.innerHTML += "<hr><pre>" + data.output + "</pre>";
            }
          } else {
            showAlert("Error populating database", "danger");
            outputDiv.innerHTML =
              '<div class="text-danger fw-bold">Error populating database:</div>';
            if (data.error) {
              outputDiv.innerHTML +=
                '<hr><pre class="text-danger">' + data.error + "</pre>";
            }
          }
        })
        .catch((error) => {
          loadingDiv.style.display = "none";
          outputDiv.style.display = "block";
          outputDiv.innerHTML =
            '<div class="text-danger fw-bold">Error: ' + error.message + "</div>";
          showAlert("Error: " + error.message, "danger");
        });
    });
  }

  // Query documents form
  const queryDocumentsForm = document.getElementById("queryDocumentsForm");
  if (queryDocumentsForm) {
    queryDocumentsForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const query = document.getElementById("documentQuery").value.trim();
      if (!query) {
        showAlert("Query cannot be empty", "warning");
        return;
      }

      const loadingDiv = document.getElementById("queryDocumentsLoading");
      const resultsDiv = document.getElementById("queryDocumentsResults");
      const noResultsMessage = document.getElementById("noResultsMessage");
      const populateOutputDiv = document.getElementById("populateOutput");

      loadingDiv.style.display = "block";
      resultsDiv.style.display = "none";
      noResultsMessage.style.display = "none";
      populateOutputDiv.style.display = "none";

      const formData = new FormData();
      formData.append("query", query);

      fetch("/query_documents", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          loadingDiv.style.display = "none";
          resultsDiv.style.display = "block";

          if (data.success) {
            showAlert("Query executed successfully", "success");
            resultsDiv.innerHTML =
              '<h6 class="mb-3">Results for: <span class="fw-bold" style="color: #0a5f52;">' +
              data.query +
              "</span></h6><hr>";

            // Format the results
            resultsDiv.innerHTML += "<div>" + data.results + "</div>";
            
            // Add slide-in animation to the results
            resultsDiv.classList.add('slide-right');
            setTimeout(() => {
              resultsDiv.classList.remove('slide-right');
            }, 1000);
          } else {
            showAlert("Error executing query", "danger");
            resultsDiv.innerHTML =
              '<h6 class="mb-3">Error for query: <span class="fw-bold text-danger">' +
              data.query +
              "</span></h6><hr>";
            resultsDiv.innerHTML +=
              '<pre class="text-danger">' + data.error + "</pre>";
          }
        })
        .catch((error) => {
          loadingDiv.style.display = "none";
          resultsDiv.style.display = "block";
          resultsDiv.innerHTML =
            '<div class="text-danger fw-bold">Error: ' + error.message + "</div>";
          showAlert("Error: " + error.message, "danger");
        });
    });
  }
}

function setupTranscriptFunctionality() {
  // Process video form
  const processVideoForm = document.getElementById("processVideoForm");
  if (processVideoForm) {
    processVideoForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const videoId = document.getElementById("videoId").value.trim();
      if (!videoId) {
        showAlert("Video ID cannot be empty", "warning");
        return;
      }

      const loadingDiv = document.getElementById("processVideoLoading");
      const videoInfoDiv = document.getElementById("videoInfo");
      const videoSegmentsDiv = document.getElementById("videoSegments");
      const noVideoResultsMessage = document.getElementById("noVideoResultsMessage");
      const transcriptResultsDiv = document.getElementById("transcriptResults");

      loadingDiv.style.display = "block";
      videoInfoDiv.style.display = "none";
      videoSegmentsDiv.style.display = "none";
      noVideoResultsMessage.style.display = "none";
      transcriptResultsDiv.style.display = "none";

      const formData = new FormData();
      formData.append("videoId", videoId);

      fetch("/process_video", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          loadingDiv.style.display = "none";

          if (data.success) {
            showAlert("Video processed successfully", "success");

            // Display video information
            document.getElementById("videoThumbnail").src =
              data.video_info.thumbnail;
            document.getElementById("videoTitle").textContent =
              data.video_info.title;
            document.getElementById("videoChannel").textContent =
              "Channel: " + data.video_info.channel;
            document.getElementById("videoLink").href = data.video_info.url;
            videoInfoDiv.style.display = "block";
            videoInfoDiv.classList.add('slide-right');
            
            setTimeout(() => {
              videoInfoDiv.classList.remove('slide-right');
            }, 1000);

            // Display video segments
            const segmentsList = document.getElementById("segmentsList");
            segmentsList.innerHTML = "";

            data.segments.forEach((segment, index) => {
              const segmentDiv = document.createElement("div");
              segmentDiv.className = "segment-item";
              segmentDiv.style.animationDelay = `${0.05 * index}s`;
              segmentDiv.classList.add('slide-right');

              segmentDiv.innerHTML = `
                <div class="segment-text">${segment.title}</div>
                <div class="segment-time">${segment.start_time} - ${segment.end_time}</div>
              `;

              // Add click handler to jump to that part of video on YouTube
              segmentDiv.addEventListener("click", function () {
                // Extract seconds from start_time format (00:00:00)
                const timeParts = segment.start_time.split(":");
                const seconds =
                  parseInt(timeParts[0]) * 3600 +
                  parseInt(timeParts[1]) * 60 +
                  parseInt(timeParts[2]);
                const videoUrl = `${data.video_info.url}&t=${seconds}`;
                window.open(videoUrl, "_blank");
              });

              segmentsList.appendChild(segmentDiv);
              
              // Remove animation class after animation completes
              setTimeout(() => {
                segmentDiv.classList.remove('slide-right');
              }, 1000 + (100 * index));
            });

            videoSegmentsDiv.style.display = "block";
            noVideoResultsMessage.style.display = "none";
          } else {
            showAlert(data.error || "Error processing video", "danger");
            noVideoResultsMessage.style.display = "block";
            noVideoResultsMessage.innerHTML = `
              <div class="empty-state">
                <i class="bi bi-exclamation-triangle empty-state-icon" style="color: #e74c3c;"></i>
                <p>${data.error || "Error processing video"}</p>
              </div>
            `;
          }
        })
        .catch((error) => {
          loadingDiv.style.display = "none";
          noVideoResultsMessage.style.display = "block";
          noVideoResultsMessage.innerHTML = `
            <div class="empty-state">
              <i class="bi bi-exclamation-triangle empty-state-icon" style="color: #e74c3c;"></i>
              <p>Error: ${error.message}</p>
            </div>
          `;
          showAlert("Error: " + error.message, "danger");
        });
    });
  }

  // Query transcripts form
  const queryTranscriptsForm = document.getElementById("queryTranscriptsForm");
  if (queryTranscriptsForm) {
    queryTranscriptsForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const query = document.getElementById("transcriptQuery").value.trim();
      if (!query) {
        showAlert("Query cannot be empty", "warning");
        return;
      }

      const loadingDiv = document.getElementById("queryTranscriptsLoading");
      const resultsDiv = document.getElementById("transcriptResults");
      const resultsList = document.getElementById("transcriptResultsList");
      const videoInfoDiv = document.getElementById("videoInfo");
      const videoSegmentsDiv = document.getElementById("videoSegments");
      const noVideoResultsMessage = document.getElementById("noVideoResultsMessage");

      loadingDiv.style.display = "block";
      resultsDiv.style.display = "none";
      videoInfoDiv.style.display = "none";
      videoSegmentsDiv.style.display = "none";
      noVideoResultsMessage.style.display = "none";

      const formData = new FormData();
      formData.append("query", query);

      fetch("/query_transcripts", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          loadingDiv.style.display = "none";
          resultsDiv.style.display = "block";

          if (data.success) {
            showAlert("Transcript search completed", "success");

            // Clear previous results
            resultsList.innerHTML = "";

            // Display results
            if (data.results && data.results.length > 0) {
              resultsList.innerHTML = `
                <div class="mb-3 pb-2 border-bottom slide-right">
                  <h6 class="text-secondary">Found ${data.results.length} results for: <span class="fw-bold" style="color: #0a5f52;">${data.query}</span></h6>
                </div>
              `;
              
              data.results.forEach((result, index) => {
                const resultDiv = document.createElement("div");
                resultDiv.className = "search-result slide-right";
                resultDiv.style.animationDelay = `${0.1 * index}s`;

                // Format timestamp
                const startTime = result.metadata.start_time || 0;
                const timestamp = formatTime(
                  typeof startTime === "string"
                    ? parseFloat(startTime)
                    : startTime
                );

                resultDiv.innerHTML = `
                  <div class="search-result-header">
                    <div class="search-result-title">${
                      result.metadata.title || "Unknown Video"
                    }</div>
                    <div class="search-result-source">${timestamp}</div>
                  </div>
                  <div class="search-result-content">
                    ${result.content}
                  </div>
                  <div class="d-flex justify-content-between align-items-center mt-3">
                    <div class="small text-muted">
                      Relevance: ${(1 - result.relevance).toFixed(2)}
                    </div>
                    <a href="${result.metadata.url || '#'}" 
                       target="_blank" class="btn btn-primary btn-sm">
                       <i class="bi bi-play-btn"></i> Watch
                    </a>
                  </div>
                `;

                resultsList.appendChild(resultDiv);
                
                // Remove animation class after animation completes
                setTimeout(() => {
                  resultDiv.classList.remove('slide-right');
                }, 1000 + (100 * index));
              });
            } else {
              resultsList.innerHTML = `
                <div class="empty-state slide-right">
                  <i class="bi bi-search empty-state-icon"></i>
                  <p>No results found for this query</p>
                </div>
              `;
            }
          } else {
            showAlert(data.error || "Error searching transcripts", "danger");
            resultsList.innerHTML = `
              <div class="empty-state slide-right">
                <i class="bi bi-exclamation-triangle empty-state-icon" style="color: #e74c3c;"></i>
                <p>Error: ${data.error || "Unknown error"}</p>
              </div>
            `;
          }
        })
        .catch((error) => {
          loadingDiv.style.display = "none";
          resultsDiv.style.display = "block";
          resultsList.innerHTML = `
            <div class="empty-state slide-right">
              <i class="bi bi-exclamation-triangle empty-state-icon" style="color: #e74c3c;"></i>
              <p>Error: ${error.message}</p>
            </div>
          `;
          showAlert("Error: " + error.message, "danger");
        });
    });
  }
}

// Helper function to format seconds into MM:SS format
function formatTime(seconds) {
  if (!seconds && seconds !== 0) return "00:00";

  seconds = Math.floor(seconds);
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  return (
    String(minutes).padStart(2, "0") +
    ":" +
    String(remainingSeconds).padStart(2, "0")
  );
}

// Add a keyframe animation for the slide out effect
document.addEventListener('DOMContentLoaded', function() {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideOutRight {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(100%);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(style);
});