import React from 'react';
import { Link } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import { useResults } from '../contexts/ResultsContext';
import './EvaluationPage.css';

const EvaluationPage = () => {
  const { 
    loading, 
    evaluationStatus, 
    resultsExist, 
    startEvaluation, 
    downloadResults 
  } = useResults();

  return (
    <div className="evaluation-page">
      <div className="evaluation-container">
        <div className="evaluation-card">
          <div className="evaluation-header gradient-bg">
            <h1 className="evaluation-title">ANSWER SHEET EVALUATION</h1>
            <p className="evaluation-subtitle">Start the automated evaluation of student answer sheets</p>
          </div>

          <div className="evaluation-content">
            {loading || evaluationStatus.running ? (
              <div className="loading-wrapper">
                <LoadingSpinner 
                  message={evaluationStatus.message || "Processing answer sheets..."} 
                  progress={evaluationStatus.progress} 
                />
                <p className="processing-message">
                  Our system is evaluating all student answers. This may take several minutes depending on the number of students and questions.
                </p>
              </div>
            ) : (
              <>
                <div className="evaluation-info">
                  <div className="info-card">
                    <div className="info-icon">
                      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M13 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V9L13 2Z" 
                          stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M13 2V9H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                    <div className="info-text">
                      <h3>How It Works</h3>
                      <p>The system will evaluate all student answer files against the provided answer keys using AI. Results will be available for download when complete.</p>
                    </div>
                  </div>
                </div>

                {evaluationStatus.error && (
                  <div className="error-message">
                    Error: {evaluationStatus.error}
                  </div>
                )}

                {evaluationStatus.complete && (
                  <div className="success-message">
                    Evaluation completed successfully!
                  </div>
                )}

                <div className="evaluation-actions">
                  <button 
                    onClick={startEvaluation}
                    disabled={loading || evaluationStatus.running}
                    className="btn btn-primary btn-lg"
                  >
                    Start Evaluation
                  </button>

                  {resultsExist && (
                    <div className="results-actions">
                      <button onClick={downloadResults} className="btn btn-secondary">
                        Download Results
                      </button>
                      <Link to="/results-view" className="btn btn-secondary">
                        View Results
                      </Link>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EvaluationPage;