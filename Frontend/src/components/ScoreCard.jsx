import React from 'react';
import CircularProgress from './CircularProgress';
import './ScoreCard.css';

const ScoreCard = ({ score, maxScore, subject, strengths = [], improvements = [] }) => {
  // Calculate score percentage
  const scorePercentage = (score / maxScore) * 100;
  
  // Determine score grade and message
  const getScoreGrade = () => {
    if (scorePercentage >= 90) return { grade: 'A', message: 'Excellent' };
    if (scorePercentage >= 80) return { grade: 'B', message: 'Very Good' };
    if (scorePercentage >= 70) return { grade: 'C', message: 'Good' };
    if (scorePercentage >= 60) return { grade: 'D', message: 'Satisfactory' };
    if (scorePercentage >= 50) return { grade: 'E', message: 'Pass' };
    return { grade: 'F', message: 'Needs Improvement' };
  };
  
  const { grade, message } = getScoreGrade();
  
  return (
    <div className="score-card">
      <div className="score-header">
        <h3 className="score-title">Overall Performance</h3>
        <div className="score-subject">{subject}</div>
      </div>
      
      <div className="score-visualization">
        <CircularProgress score={score} maxScore={maxScore} />
        
        <div className="score-details">
          <div className="score-grade">{grade}</div>
          <div className="score-message">{message}</div>
        </div>
      </div>
      
      <div className="score-analysis">
        <div className="score-strengths">
          <h4 className="score-section-title">Strengths</h4>
          <ul className="score-list">
            {strengths.map((strength, index) => (
              <li key={index} className="score-list-item strength">
                <span className="list-icon">✓</span>
                <span>{strength}</span>
              </li>
            ))}
            {strengths.length === 0 && (
              <li className="score-list-item empty">No specific strengths identified</li>
            )}
          </ul>
        </div>
        
        <div className="score-improvements">
          <h4 className="score-section-title">Areas for Improvement</h4>
          <ul className="score-list">
            {improvements.map((improvement, index) => (
              <li key={index} className="score-list-item improvement">
                <span className="list-icon">!</span>
                <span>{improvement}</span>
              </li>
            ))}
            {improvements.length === 0 && (
              <li className="score-list-item empty">No specific improvements identified</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ScoreCard;