import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import { useResults } from '../contexts/ResultsContext';
import { api } from '../services/api';
import './ResultsViewPage.css';
import CircularProgress from '../components/CircularProgress';
import { Bar, Radar } from 'react-chartjs-2';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  Title, 
  Tooltip, 
  Legend,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale, 
  LinearScale, 
  BarElement, 
  Title, 
  Tooltip, 
  Legend,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  {
    id: 'customAnimation',
    beforeInit: function(chart) {
      chart.options.animation = {
        duration: 1000,
        easing: 'easeOutBounce'
      };
    }
  }
);

const ResultsViewPage = () => {
  const [students, setStudents] = useState([]);
  const [currentStudentIndex, setCurrentStudentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { downloadResults } = useResults();
  const [openQuestions, setOpenQuestions] = useState({});

  const toggleQuestion = (questionId) => {
    setOpenQuestions(prev => ({
      ...prev,
      [questionId]: !prev[questionId]
    }));
  };

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
        
        // Now fetch the JSON data
        const data = await api.getStudentResults();
        
        if (!data || !data.students || data.students.length === 0) {
          throw new Error('No student results data received from server');
        }
        
        console.log('Loaded student data:', data.students);
        
        // Ensure each student has the required properties
        const validatedStudents = data.students.map((student, index) => ({
          ...student,
          id: student.id || `student-${index}`,
          questionNumber: student.questionNumber || index + 1,
          // Ensure other required properties have defaults if missing
        }));
        
        setStudents(validatedStudents);
        setCurrentStudentIndex(0);
        setLoading(false);
      } catch (err) {
        console.error('Failed to load results:', err);
        setError(`${err.message || 'Unknown error occurred while fetching results'}`);
        setLoading(false);
      }
    };

    fetchResults();
  }, []);

  const nextStudent = () => {
    if (currentStudentIndex < students.length - 1) {
      setCurrentStudentIndex(currentStudentIndex + 1);
    }
  };

  const prevStudent = () => {
    if (currentStudentIndex > 0) {
      setCurrentStudentIndex(currentStudentIndex - 1);
    }
  };

  const currentStudent = students[currentStudentIndex];

  // Generate chart data for the current student if available
  const generateBarChartData = () => {
    if (!currentStudent) return null;
    
    return {
      labels: currentStudent.questions.map(q => `Q${q.questionNumber}`),
      datasets: [
        {
          label: 'Score',
          data: currentStudent.questions.map(q => q.score),
          backgroundColor: 'rgba(67, 97, 238, 0.7)',
          borderColor: 'rgba(67, 97, 238, 1)',
          borderWidth: 1,
          barThickness: 'flex',
          maxBarThickness: 40
        },
        {
          label: 'Maximum',
          data: currentStudent.questions.map(q => q.maxScore),
          backgroundColor: 'rgba(220, 220, 220, 0.7)',
          borderColor: 'rgba(220, 220, 220, 1)',
          borderWidth: 1,
          barThickness: 'flex',
          maxBarThickness: 40
        }
      ]
    };
  };

  const generateRadarChartData = () => {
    if (!currentStudent) return null;
    
    // Calculate percentage scores for radar chart
    const percentScores = currentStudent.questions.map(q => 
      (q.score / q.maxScore) * 100
    );
    
    return {
      labels: currentStudent.questions.map(q => `Q${q.questionNumber}`),
      datasets: [
        {
          label: 'Score %',
          data: percentScores,
          backgroundColor: 'rgba(67, 97, 238, 0.2)',
          borderColor: 'rgba(67, 97, 238, 1)',
          borderWidth: 2,
          pointBackgroundColor: 'rgba(67, 97, 238, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(67, 97, 238, 1)',
          pointRadius: 4,
          pointHoverRadius: 6
        }
      ]
    };
  };

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
          <div className="student-results-wrapper">
            {/* Student Navigation Header */}
            <div className="student-navigation">
              <button 
                className="nav-arrow prev"
                onClick={prevStudent}
                disabled={currentStudentIndex === 0}
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M15 19L8 12L15 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
              
              <div className="student-indicator">
                <span className="student-name">{currentStudent?.studentName}</span>
                <span className="student-counter">
                  {currentStudentIndex + 1} of {students.length}
                </span>
              </div>
              
              <button 
                className="nav-arrow next"
                onClick={nextStudent}
                disabled={currentStudentIndex === students.length - 1}
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M9 5L16 12L9 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            </div>
            
            {currentStudent && (
              <div className="student-result-card">
                {/* Student Header Information */}
                <div className="result-card-header">
                  <div className="student-details">
                    <h2 className="student-name-header">{currentStudent.studentName}</h2>
                    <div className="student-info-row">
                      <span className="info-label">{currentStudent.subject}</span>
                      <span className="info-separator">•</span>
                      <span className="info-label">{currentStudent.year}</span>
                      <span className="info-separator">•</span>
                      <span className="info-label">{currentStudent.semester}</span>
                    </div>
                  </div>
                  
                  <div className="student-score">
                    <CircularProgress 
                      score={currentStudent.overallScore} 
                      maxScore={currentStudent.maxScore} 
                      size={80}
                      strokeWidth={8}
                      showPercentage={true}
                    />
                    <div className="score-text">
                      <div className="score-value">{currentStudent.overallScore}/{currentStudent.maxScore}</div>
                      <div className="score-label">Overall Score</div>
                    </div>
                  </div>
                </div>
                
                {/* Charts Section */}
                <div className="result-charts-section">
                  <h3 className="section-title">Performance Analysis</h3>
                  
                  <div className="charts-grid">
                    <div className="chart-container">
                      <h4 className="chart-title">Score by Question</h4>
                      {generateBarChartData() && (
                        <Bar 
                          data={generateBarChartData()} 
                          options={{
                            responsive: true,
                            scales: {
                              y: {
                                beginAtZero: true,
                                suggestedMax: Math.max(...currentStudent.questions.map(q => q.maxScore)) + 2
                              }
                            },
                            plugins: {
                              legend: {
                                position: 'top'
                              }
                            }
                          }}
                        />
                      )}
                    </div>
                    
                    <div className="chart-container">
                      <h4 className="chart-title">Score Distribution</h4>
                      {generateRadarChartData() && (
                        <Radar 
                          data={generateRadarChartData()}
                          options={{
                            responsive: true,
                            scales: {
                              r: {
                                beginAtZero: true,
                                min: 0,
                                max: 100,
                                ticks: {
                                  stepSize: 20
                                }
                              }
                            },
                            plugins: {
                              legend: {
                                position: 'top'
                              }
                            }
                          }}
                        />
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Questions Section */}
                <div className="result-questions-section">
                  <h3 className="section-title">Questions & Feedback</h3>
                  
                  <div className="questions-accordion">
                    {currentStudent.questions.map((question, index) => (
                      <div className="accordion-item" key={question.id || index}>
                        <details open={openQuestions[question.id || index]}>
                          <summary 
                            className="accordion-header" 
                            onClick={(e) => {
                              e.preventDefault();
                              toggleQuestion(question.id || index);
                            }}
                          >
                            <div className="question-info">
                              <span className="question-number">Question {question.questionNumber}</span>
                              <span className="question-score">
                                {question.score}/{question.maxScore}
                              </span>
                            </div>
                            <div className="question-preview">
                              {question.questionText.length > 60 
                                ? `${question.questionText.substring(0, 60)}...` 
                                : question.questionText}
                            </div>
                          </summary>
                          
                          <div className="accordion-body">
                            <div className="question-full">
                              <h4>Question:</h4>
                              <p>{question.questionText}</p>
                            </div>
                            
                            <div className="student-answer">
                              <h4>Student's Answer:</h4>
                              <p>{question.studentAnswer}</p>
                            </div>
                            
                            <div className="feedback-container">
                              <h4>Feedback:</h4>
                              <p className="feedback-text">{question.feedback}</p>
                              
                              <div className="feedback-columns">
                                <div className="strength-column">
                                  <h5>Strengths</h5>
                                  <ul className="strength-list">
                                    {question.strengths.map((strength, idx) => (
                                      <li key={idx} className="strength-item">{strength}</li>
                                    ))}
                                  </ul>
                                </div>
                                
                                <div className="improvement-column">
                                  <h5>Areas for Improvement</h5>
                                  <ul className="improvement-list">
                                    {question.improvements.map((improvement, idx) => (
                                      <li key={idx} className="improvement-item">{improvement}</li>
                                    ))}
                                  </ul>
                                </div>
                              </div>
                            </div>
                          </div>
                        </details>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Overall Feedback */}
                <div className="overall-feedback-section">
                  <h3 className="section-title">Overall Assessment</h3>
                  <p className="feedback-paragraph">
                    {currentStudent.overallFeedback || 
                     `${currentStudent.studentName} demonstrates a good understanding of the subject material. 
                      The overall performance is ${Math.round((currentStudent.overallScore / currentStudent.maxScore) * 100)}%, 
                      which shows solid comprehension with some areas for improvement. 
                      Focus on addressing the specific feedback for each question to improve future performance.`}
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsViewPage;