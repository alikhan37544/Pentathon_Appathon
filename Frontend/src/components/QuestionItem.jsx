import React from 'react';
import './QuestionItem.css';

const QuestionItem = ({ question, isSelected, onClick }) => {
  // Calculate score percentage for styling
  const scorePercentage = (question.score / question.maxScore) * 100;
  
  // Determine score color based on percentage
  const getScoreColor = () => {
    if (scorePercentage >= 80) return 'excellent';
    if (scorePercentage >= 70) return 'good';
    if (scorePercentage >= 60) return 'average';
    if (scorePercentage >= 50) return 'below-average';
    return 'poor';
  };
  
  return (
    <div 
      className={`question-item ${isSelected ? 'selected' : ''}`}
      onClick={() => onClick(question.id)}
    >
      <div className="question-number">Q{question.questionNumber}</div>
      
      <div className="question-content">
        <div className="question-text">
          {question.questionText.length > 50
            ? `${question.questionText.substring(0, 50)}...`
            : question.questionText}
        </div>
        
        <div className="question-progress">
          <div 
            className="progress-bar" 
            style={{ width: `${scorePercentage}%`, backgroundColor: getProgressColor(scorePercentage) }}
          ></div>
        </div>
      </div>
      
      <div className={`question-score ${getScoreColor()}`}>
        {question.score}/{question.maxScore}
      </div>
    </div>
  );
};

// Helper function to get progress bar color
const getProgressColor = (percentage) => {
  if (percentage >= 80) return '#2ec4b6'; // Teal - excellent
  if (percentage >= 70) return '#4361ee'; // Blue - good
  if (percentage >= 60) return '#ff9f1c'; // Orange - average
  if (percentage >= 50) return '#ff6b6b'; // Red - below average
  return '#e63946'; // Deep red - poor
};

export default QuestionItem;