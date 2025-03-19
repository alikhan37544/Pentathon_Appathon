const API_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : window.location.hostname === 'localhost' 
    ? 'http://localhost:5000'
    : `http://${window.location.hostname}:5000`;  // Use the same hostname as frontend

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
  viewResults: async () => {
    try {
      const response = await fetch(`${API_URL}/results`, {
        mode: 'cors',
        credentials: 'omit'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.text();
    } catch (error) {
      console.error('Error viewing results:', error);
      throw error;
    }
  }
};