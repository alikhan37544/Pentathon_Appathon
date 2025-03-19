import React, { createContext, useState, useContext, useEffect } from 'react';
import { api } from '../services/api';

const ResultsContext = createContext();

export const useResults = () => useContext(ResultsContext);

export const ResultsProvider = ({ children }) => {
  const [loading, setLoading] = useState(false);
  const [evaluationStatus, setEvaluationStatus] = useState({
    running: false,
    complete: false,
    progress: 0,
    message: "",
    error: null
  });
  const [resultsExist, setResultsExist] = useState(false);

  // Check if results exist on initial load
  useEffect(() => {
    checkResultsExist();
  }, []);

  const checkResultsExist = async () => {
    try {
      const data = await api.checkResultsExist();
      setResultsExist(data.exists);
    } catch (error) {
      console.error('Error checking if results exist:', error);
    }
  };

  const startEvaluation = async () => {
    setLoading(true);
    try {
      await api.startEvaluation();
      // Start polling for status updates
      pollStatus();
    } catch (error) {
      setEvaluationStatus(prev => ({
        ...prev,
        error: 'Failed to start evaluation'
      }));
      setLoading(false);
    }
  };

  const pollStatus = async () => {
    try {
      const status = await api.checkStatus();
      setEvaluationStatus(status);
      
      // If evaluation is still running, poll again in 2 seconds
      if (status.running) {
        setTimeout(pollStatus, 2000);
      } else {
        setLoading(false);
        checkResultsExist();
      }
    } catch (error) {
      setEvaluationStatus(prev => ({
        ...prev,
        running: false,
        error: 'Error checking evaluation status'
      }));
      setLoading(false);
    }
  };

  const downloadResults = () => {
    window.location.href = api.getResultsDownloadUrl();
  };

  return (
    <ResultsContext.Provider value={{
      loading,
      evaluationStatus,
      resultsExist,
      startEvaluation,
      downloadResults,
      checkResultsExist
    }}>
      {children}
    </ResultsContext.Provider>
  );
};