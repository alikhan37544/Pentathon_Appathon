import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = ({ message = 'Loading...', progress = null }) => {
  return (
    <div className="loading-container">
      <div className="spinner-container">
        <div className="spinner"></div>
        
        {progress !== null && (
          <div className="progress-value">{Math.round(progress)}%</div>
        )}
      </div>
      
      {message && <p className="loading-message">{message}</p>}
      
      {progress !== null && (
        <div className="progress-bar-container">
          <div className="progress-bar" style={{ width: `${progress}%` }}></div>
        </div>
      )}
    </div>
  );
};

export default LoadingSpinner;