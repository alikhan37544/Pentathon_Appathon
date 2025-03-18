// This file contains JavaScript code for client-side functionality, such as form handling and AJAX requests.

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const queryForm = document.getElementById('query-form');

    if (uploadForm) {
        uploadForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(uploadForm);
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                uploadForm.reset();
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }

    if (queryForm) {
        queryForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const queryText = document.getElementById('query-text').value;
            fetch(`/query?text=${encodeURIComponent(queryText)}`)
            .then(response => response.json())
            .then(data => {
                const resultsContainer = document.getElementById('results');
                resultsContainer.innerHTML = '';
                data.results.forEach(result => {
                    const resultItem = document.createElement('div');
                    resultItem.textContent = result;
                    resultsContainer.appendChild(resultItem);
                });
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});