import React, { useEffect, useState } from 'react';
import './CircularProgress.css';

const CircularProgress = ({ 
  score, 
  maxScore, 
  size = 80, 
  strokeWidth = 8, 
  showPercentage = true 
}) => {
  const [progress, setProgress] = useState(0);
  
  // Calculate the percentage
  const percentage = (score / maxScore) * 100;
  
  // Calculate radius and stroke measurements
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (progress / 100) * circumference;
  
  // Determine the color based on the score percentage
  const getColor = () => {
    if (percentage >= 80) return '#2ec4b6'; // Teal - excellent
    if (percentage >= 70) return '#4361ee'; // Blue - good
    if (percentage >= 60) return '#ff9f1c'; // Orange - average
    if (percentage >= 50) return '#ff6b6b'; // Red - below average
    return '#e63946'; // Deep red - poor
  };
  
  // Animate the progress when the component mounts or when the score changes
  useEffect(() => {
    const timer = setTimeout(() => {
      setProgress(percentage);
    }, 100);
    
    return () => clearTimeout(timer);
  }, [percentage]);
  
  return (
    <div className="circular-progress" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Background circle */}
        <circle
          className="circular-progress-bg"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
        />
        
        {/* Progress circle */}
        <circle
          className="circular-progress-bar"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          style={{
            strokeDasharray: circumference,
            strokeDashoffset: strokeDashoffset,
            stroke: getColor()
          }}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      
      {/* Score text */}
      {showPercentage && (
        <div className="circular-progress-text">
          <span className="percentage">{Math.round(percentage)}%</span>
        </div>
      )}
    </div>
  );
};

export default CircularProgress;