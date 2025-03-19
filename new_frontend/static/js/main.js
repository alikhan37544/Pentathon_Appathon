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
  // Document Functionality
  setupDocumentFunctionality();

  // Transcript Functionality
  setupTranscriptFunctionality();

  // Hide all loading indicators initially
  document.querySelectorAll(".loading").forEach((el) => {
    el.style.display = "none";
  });
});

function setupDocumentFunctionality() {
  // Populate database button
  const populateBtn = document.getElementById("populateBtn");
  if (populateBtn) {
    populateBtn.addEventListener("click", function () {
      const loadingDiv = document.getElementById("populateLoading");
      const outputDiv = document.getElementById("populateOutput");

      loadingDiv.style.display = "block";
      outputDiv.style.display = "none";

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
              '<div class="text-success">Database populated successfully!</div>';
            if (data.output) {
              outputDiv.innerHTML += "<hr><pre>" + data.output + "</pre>";
            }
          } else {
            showAlert("Error populating database", "danger");
            outputDiv.innerHTML =
              '<div class="text-danger">Error populating database:</div>';
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
            '<div class="text-danger">Error: ' + error.message + "</div>";
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

      loadingDiv.style.display = "block";
      resultsDiv.style.display = "none";

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
              '<h6>Results for: <span class="text-primary">' +
              data.query +
              "</span></h6><hr>";

            // Format the results
            resultsDiv.innerHTML += "<div>" + data.results + "</div>";
          } else {
            showAlert("Error executing query", "danger");
            resultsDiv.innerHTML =
              '<h6>Error for query: <span class="text-danger">' +
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
            '<div class="text-danger">Error: ' + error.message + "</div>";
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

      loadingDiv.style.display = "block";
      videoInfoDiv.style.display = "none";
      videoSegmentsDiv.style.display = "none";

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

            // Display video segments
            const segmentsList = document.getElementById("segmentsList");
            segmentsList.innerHTML = "";

            data.segments.forEach((segment, index) => {
              const segmentDiv = document.createElement("div");
              segmentDiv.className = "list-group-item";

              segmentDiv.innerHTML = `
                            <div class="segment-item">
                                <div class="segment-text">${segment.title}</div>
                                <div class="segment-time">${segment.start_time} - ${segment.end_time}</div>
                            </div>
                        `;

              // Add click handler to jump to that part of video on YouTube
              segmentDiv.addEventListener("click", function () {
                // Extract seconds from start_time format (00:00:00)
                const timeParts = segment.start_time.split(":");
                const seconds =
                  parseInt(timeParts[0]) * 3600 +
                  parseInt(timeParts[1]) * 60 +
                  parseInt(timeParts[2]);
                const videoUrl = data.video_info.url + seconds;
                window.open(videoUrl, "_blank");
              });

              segmentsList.appendChild(segmentDiv);
            });

            videoSegmentsDiv.style.display = "block";
          } else {
            showAlert(data.error || "Error processing video", "danger");
          }
        })
        .catch((error) => {
          loadingDiv.style.display = "none";
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

      loadingDiv.style.display = "block";
      resultsDiv.style.display = "none";

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
              data.results.forEach((result) => {
                const resultDiv = document.createElement("div");
                resultDiv.className = "transcript-result";

                // Format timestamp
                const startTime = result.metadata.start_time || 0;
                const timestamp = formatTime(
                  typeof startTime === "string"
                    ? parseFloat(startTime)
                    : startTime
                );

                resultDiv.innerHTML = `
                                <div class="transcript-result-header">
                                    <div class="transcript-result-title">${
                                      result.metadata.title || "Unknown Video"
                                    }</div>
                                    <div class="transcript-result-timestamp">${timestamp}</div>
                                </div>
                                <div class="transcript-result-content">
                                    ${result.content}
                                </div>
                                <div class="transcript-result-relevance">
                                    <small>Relevance: ${(
                                      1 - result.relevance
                                    ).toFixed(2)}</small>
                                </div>
                                <a href="${result.metadata.url}" 
                                   target="_blank" class="btn btn-sm btn-outline-danger mt-2">
                                   <i class="bi bi-play-btn me-1"></i>Watch this segment
                                </a>
                            `;

                resultsList.appendChild(resultDiv);
              });
            } else {
              resultsList.innerHTML =
                '<div class="alert alert-info">No results found for this query.</div>';
            }
          } else {
            showAlert(data.error || "Error searching transcripts", "danger");
            resultsList.innerHTML =
              '<div class="alert alert-danger">Error: ' +
              (data.error || "Unknown error") +
              "</div>";
          }
        })
        .catch((error) => {
          loadingDiv.style.display = "none";
          resultsDiv.style.display = "block";
          resultsList.innerHTML =
            '<div class="alert alert-danger">Error: ' +
            error.message +
            "</div>";
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
