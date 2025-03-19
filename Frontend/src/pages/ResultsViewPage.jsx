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
        const html = await api.viewResults();
        setResultsHtml(html);
        setLoading(false);
      } catch (err) {
        setError('Failed to load results');
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
          <div className="error-message">{error}</div>
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