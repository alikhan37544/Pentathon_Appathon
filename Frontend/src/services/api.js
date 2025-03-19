const API_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://127.0.0.1:5000';

export const api = {
  // Start the evaluation process
  startEvaluation: async () => {
    try {
      const response = await fetch(`${API_URL}/start_evaluation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'omit'  // Use 'omit' to not include credentials
      });
      return await response.json();
    } catch (error) {
      console.error('Error starting evaluation:', error);
      throw error;
    }
  },

  // Check evaluation status
  checkStatus: async () => {
    try {
      const response = await fetch(`${API_URL}/status`);
      return await response.json();
    } catch (error) {
      console.error('Error checking status:', error);
      throw error;
    }
  },

  // Check if results exist
  checkResultsExist: async () => {
    try {
      const response = await fetch(`${API_URL}/check_results_exist`);
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
      const response = await fetch(`${API_URL}/results`);
      return await response.text();
    } catch (error) {
      console.error('Error viewing results:', error);
      throw error;
    }
  }
};