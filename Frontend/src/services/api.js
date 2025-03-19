const API_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : window.location.hostname === 'localhost' 
    ? 'http://localhost:5000'
    : `http://${window.location.hostname}:5000`;  // Use the same hostname as frontend

const viewResults = async () => {
  try {
    // Use fetch directly with the correct URL and appropriate headers
    const response = await fetch('/api/results', {
      method: 'GET',
      headers: {
        'Accept': 'text/html,application/json',
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    // Handle the response as text since we're expecting HTML
    const htmlContent = await response.text();
    return htmlContent;
  } catch (error) {
    console.error("Error fetching results:", error);
    throw error;
  }
};

export const api = {
  // Start the evaluation process
  startEvaluation: async () => {
    try {
      console.log(`Sending request to ${API_URL}/start_evaluation`);
      const response = await fetch(`${API_URL}/start_evaluation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors',
        credentials: 'omit'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error starting evaluation:', error);
      throw error;
    }
  },

  // Check evaluation status
  checkStatus: async () => {
    try {
      const response = await fetch(`${API_URL}/status`, {
        mode: 'cors',
        credentials: 'omit'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error checking status:', error);
      throw error;
    }
  },

  // Check if results exist
  checkResultsExist: async () => {
    try {
      const response = await fetch(`${API_URL}/check_results_exist`, {
        mode: 'cors',
        credentials: 'omit'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error checking if results exist:', error);
      throw error;
    }
  },

  // Get the download URL for results
  getResultsDownloadUrl: () => {
    return `${API_URL}/download_results`;
  },

  // View results
  viewResults
};