import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import { useResults } from '../contexts/ResultsContext';
import { api } from '../services/api';
import './ResultsViewPage.css';

const ResultsViewPage = () => {
  const [resultsHtml, setResultsHtml] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { downloadResults } = useResults();

  useEffect(() => {
    const fetchResults = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // First check if results exist
        const resultsExistResponse = await api.checkResultsExist();
        
        if (!resultsExistResponse.exists) {
          throw new Error('No evaluation results available yet. Please run an evaluation first.');
        }
        
        const html = await api.viewResults();
        
        if (!html || html.trim() === '') {
          throw new Error('No results data received from server');
        }
        
        setResultsHtml(html);
        setLoading(false);
      } catch (err) {
        console.error('Failed to load results:', err);
        setError(`${err.message || 'Unknown error occurred while fetching results'}`);
        setLoading(false);
      }
    };

    fetchResults();
  }, []);

  return (
    <div className="results-view-page">
      <div className="results-container">
        <div className="results-header">
          <h1 className="page-title">Evaluation Results</h1>
          <div className="results-actions">
            <Link to="/evaluation" className="btn btn-secondary">
              Back to Evaluation
            </Link>
            <button onClick={downloadResults} className="btn btn-primary">
              Download Results
            </button>
          </div>
        </div>

        {loading ? (
          <LoadingSpinner message="Loading results..." />
        ) : error ? (
          <div className="error-container">
            <div className="error-message">
              <h3>Error Loading Results</h3>
              <p>{error}</p>
              <p>This might be because:</p>
              <ul>
                <li>No evaluation has been run yet</li>
                <li>The results file isn't properly generated</li>
                <li>There was a network issue connecting to the server</li>
              </ul>
              <div className="error-actions">
                <Link to="/evaluation" className="btn btn-primary">
                  Go to Evaluation
                </Link>
                <button onClick={() => window.location.reload()} className="btn btn-secondary">
                  Retry
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div 
            className="results-content"
            dangerouslySetInnerHTML={{ __html: resultsHtml }}
          />
        )}
      </div>
    </div>
  );
};

export default ResultsViewPage;