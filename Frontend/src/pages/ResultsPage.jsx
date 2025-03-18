import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useEvaluation } from '../contexts/EvaluationContext';
import LoadingSpinner from '../components/LoadingSpinner';
import CircularProgress from '../components/CircularProgress';
import './ResultsPage.css';

const ResultsPage = () => {
  const { evaluationId } = useParams();
  const { 
    evaluationData, 
    isLoading, 
    error,
    selectedQuestionId,
    setSelectedQuestionId,
    fetchEvaluationResults 
  } = useEvaluation();
  
  const [activeTab, setActiveTab] = useState('questions');
  const [activeFeedbackTab, setActiveFeedbackTab] = useState('feedback');
  
  // Fetch evaluation results when component mounts
  useEffect(() => {
    if (!evaluationData || evaluationData.id !== evaluationId) {
      fetchEvaluationResults(evaluationId);
    }
  }, [evaluationId, evaluationData, fetchEvaluationResults]);
  
  // Get the selected question
  const selectedQuestion = evaluationData?.questions.find(
    q => q.id === selectedQuestionId
  );
  
  // Get current date for display
  const currentDate = new Date().toLocaleDateString('en-US', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });
  
  if (isLoading) {
    return (
      <div className="results-dashboard loading-state">
        <LoadingSpinner message="Loading evaluation results..." />
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="results-dashboard error-state">
        <div className="error-container">
          <h2>Error Loading Results</h2>
          <p>{error}</p>
          <Link to="/upload" className="btn btn-primary">Try Again</Link>
        </div>
      </div>
    );
  }
  
  if (!evaluationData) {
    return (
      <div className="results-dashboard loading-state">
        <LoadingSpinner message="Preparing your evaluation..." />
      </div>
    );
  }
  
  // Calculate average score
  const averageScore = Math.round(evaluationData.questions.reduce((sum, q) => sum + (q.score / q.maxScore) * 100, 0) / evaluationData.questions.length);
  const totalScore = evaluationData.overallScore;
  
  return (
    <div className="results-dashboard">
      <div className="dashboard-sidebar">
        <div className="sidebar-header">
          <h2>Evaluation</h2>
        </div>
        
        <nav className="sidebar-nav">
          <Link to="/" className="nav-item">
            <span className="nav-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="3" y="3" width="7" height="9" rx="2" stroke="currentColor" strokeWidth="2"/>
                <rect x="14" y="3" width="7" height="5" rx="2" stroke="currentColor" strokeWidth="2"/>
                <rect x="14" y="12" width="7" height="9" rx="2" stroke="currentColor" strokeWidth="2"/>
                <rect x="3" y="16" width="7" height="5" rx="2" stroke="currentColor" strokeWidth="2"/>
              </svg>
            </span>
            <span>Home</span>
          </Link>
          
          <Link to="/upload" className="nav-item">
            <span className="nav-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </span>
            <span>Upload New</span>
          </Link>
          
          <div className="nav-item active">
            <span className="nav-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 5H7C5.89543 5 5 5.89543 5 7V19C5 20.1046 5.89543 21 7 21H17C18.1046 21 19 20.1046 19 19V7C19 5.89543 18.1046 5 17 5H15M9 5C9 6.10457 9.89543 7 11 7H13C14.1046 7 15 6.10457 15 5M9 5C9 3.89543 9.89543 3 11 3H13C14.1046 3 15 3.89543 15 5" 
                  stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M9 12H15M9 16H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </span>
            <span>Results</span>
          </div>
        </nav>
      </div>
      
      <div className="dashboard-main">
        <div className="dashboard-header">
          <div className="header-title">
            <h1>Evaluation Results</h1>
            <p className="header-subtitle">{currentDate} • {evaluationData.subject}</p>
          </div>
          
          <div className="header-actions">
            <button className="btn btn-primary">Download Report</button>
          </div>
        </div>
        
        <div className="dashboard-content">
          {/* Performance Overview */}
          <section className="content-card">
            <h2 className="card-title">Performance Overview</h2>
            
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon questions-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 5H7C5.89543 5 5 5.89543 5 7V19C5 20.1046 5.89543 21 7 21H17C18.1046 21 19 20.1046 19 19V7C19 5.89543 18.1046 5 17 5H15M9 5C9 6.10457 9.89543 7 11 7H13C14.1046 7 15 6.10457 15 5M9 5C9 3.89543 9.89543 3 11 3H13C14.1046 3 15 3.89543 15 5" 
                      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <div className="stat-content">
                  <div className="stat-value">{evaluationData.questions.length}</div>
                  <div className="stat-label">Questions</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon score-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22 11.08V12C21.9988 14.1564 21.3005 16.2547 20.0093 17.9818C18.7182 19.709 16.9033 20.9725 14.8354 21.5839C12.7674 22.1953 10.5573 22.1219 8.53447 21.3746C6.51168 20.6273 4.78465 19.2461 3.61096 17.4371C2.43727 15.628 1.87979 13.4881 2.02168 11.3363C2.16356 9.18455 2.99721 7.13631 4.39828 5.49706C5.79935 3.85781 7.69279 2.71537 9.79619 2.24013C11.8996 1.7649 14.1003 1.98232 16.07 2.85999" 
                      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M22 4L12 14.01L9 11.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <div className="stat-content">
                  <div className="stat-value">{averageScore}%</div>
                  <div className="stat-label">Average Score</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-icon total-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" 
                      stroke="currentColor" strokeWidth="2"/>
                    <path d="M15 9L9 15M9 9L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                </div>
                <div className="stat-content">
                  <div className="stat-value">{totalScore}</div>
                  <div className="stat-label">Total Score</div>
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-progress">
                  <CircularProgress 
                    score={evaluationData.overallScore} 
                    maxScore={evaluationData.maxScore} 
                    size={80}
                    strokeWidth={8}
                    showPercentage={true}
                  />
                </div>
                <div className="stat-content">
                  <div className="stat-value">{evaluationData.overallScore}/{evaluationData.maxScore}</div>
                  <div className="stat-label">Overall Grade</div>
                </div>
              </div>
            </div>
          </section>
          
          {/* Questions & Feedback Section */}
          <section className="content-card">
            <div className="qf-header">
              <h2 className="card-title">Questions & Feedback</h2>
              
              <div className="tab-buttons">
                <button 
                  className={`tab-btn ${activeTab === 'questions' ? 'active' : ''}`}
                  onClick={() => setActiveTab('questions')}
                >
                  Questions
                </button>
                <button 
                  className={`tab-btn ${activeTab === 'summary' ? 'active' : ''}`}
                  onClick={() => setActiveTab('summary')}
                >
                  Summary
                </button>
              </div>
            </div>
            
            {activeTab === 'questions' && (
              <div className="questions-container">
                <div className="questions-sidebar">
                  <h3 className="sidebar-title">Questions</h3>
                  <div className="questions-list">
                    {evaluationData.questions.map((question, index) => {
                      // Calculate score percentage for progress bar
                      const scorePercent = (question.score / question.maxScore) * 100;
                      
                      return (
                        <div 
                          key={question.id} 
                          className={`question-item ${question.id === selectedQuestionId ? 'selected' : ''}`}
                          onClick={() => setSelectedQuestionId(question.id)}
                        >
                          <div className="question-item-header">
                            <span className="question-label">Q{index + 1}</span>
                            <span className="question-preview">
                              {question.questionText.length > 30 
                                ? `${question.questionText.substring(0, 30)}...` 
                                : question.questionText}
                            </span>
                          </div>
                          
                          <div className="question-progress-bar">
                            <div 
                              className="progress-fill"
                              style={{ width: `${scorePercent}%` }}
                            ></div>
                          </div>
                          
                          <div className="question-score-badge">
                            {question.score}/{question.maxScore}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
                
                <div className="question-detail-view">
                  {selectedQuestion ? (
                    <>
                      <div className="question-header">
                        <h3 className="question-title">Question {evaluationData.questions.findIndex(q => q.id === selectedQuestionId) + 1}</h3>
                        <div className="question-score-display">
                          {selectedQuestion.score} <span className="score-delimiter">/</span> {selectedQuestion.maxScore}
                        </div>
                      </div>
                      
                      <div className="question-full-text">
                        {selectedQuestion.questionText}
                      </div>
                      
                      <div className="question-tabs">
                        <button 
                          className={`detail-tab-btn ${activeFeedbackTab === 'feedback' ? 'active' : ''}`}
                          onClick={() => setActiveFeedbackTab('feedback')}
                        >
                          Feedback
                        </button>
                        <button 
                          className={`detail-tab-btn ${activeFeedbackTab === 'answer' ? 'active' : ''}`}
                          onClick={() => setActiveFeedbackTab('answer')}
                        >
                          Your Answer
                        </button>
                      </div>
                      
                      <div className="tab-content">
                        {activeFeedbackTab === 'feedback' && (
                          <div className="feedback-content">
                            <p className="feedback-text">{selectedQuestion.feedback}</p>
                            
                            <div className="feedback-sections">
                              <div className="feedback-column">
                                <h4 className="feedback-subtitle">Strengths</h4>
                                <ul className="feedback-list">
                                  {selectedQuestion.strengths.map((strength, idx) => (
                                    <li key={idx} className="feedback-item good">
                                      {strength}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                              
                              <div className="feedback-column">
                                <h4 className="feedback-subtitle">Areas for Improvement</h4>
                                <ul className="feedback-list">
                                  {selectedQuestion.improvements.map((improvement, idx) => (
                                    <li key={idx} className="feedback-item needs-work">
                                      {improvement}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          </div>
                        )}
                        
                        {activeFeedbackTab === 'answer' && (
                          <div className="answer-content">
                            <p className="student-answer">{selectedQuestion.studentAnswer}</p>
                          </div>
                        )}
                      </div>
                    </>
                  ) : (
                    <div className="no-question-selected">
                      <p>Select a question to view feedback</p>
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {activeTab === 'summary' && (
              <div className="summary-content">
                <div className="summary-chart">
                  <h3>Performance by Question</h3>
                  <div className="bar-chart">
                    {evaluationData.questions.map((question, index) => {
                      const scorePercent = (question.score / question.maxScore) * 100;
                      return (
                        <div className="chart-item" key={index}>
                          <div className="chart-label">Q{index + 1}</div>
                          <div className="chart-bar-container">
                            <div 
                              className="chart-bar" 
                              style={{ width: `${scorePercent}%` }}
                            ></div>
                          </div>
                          <div className="chart-value">{question.score}/{question.maxScore}</div>
                        </div>
                      );
                    })}
                  </div>
                </div>
                
                <div className="overall-feedback">
                  <h3>Overall Feedback</h3>
                  <p>Good job on most questions. Your explanations were clear and well-structured. 
                  To improve further, focus on providing more specific examples in your answers and 
                  ensure you're addressing all parts of multi-part questions.</p>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;