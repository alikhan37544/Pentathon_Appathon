const API_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : window.location.hostname === 'localhost' 
    ? 'http://localhost:5000'
    : `http://${window.location.hostname}:5000`;  // Use the same hostname as frontend

const viewResults = async () => {
  try {
    // Use correct endpoint matching your Flask route (/results)
    const response = await fetch(`${API_URL}/results`, {
      method: 'GET',
      headers: {
        'Accept': 'text/html',
      },
      mode: 'cors',
      credentials: 'omit'
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

// Add a new method to get all student results
const getStudentResults = async () => {
  try {
    const response = await fetch(`${API_URL}/api/students_results`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to fetch student results');
    }
    
    return await response.json();
  } catch (error) {
    console.error('API error in getStudentResults:', error);
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
  viewResults,

  // Get student results
  getStudentResults
};