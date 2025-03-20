import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

const HomePage = () => {
  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero-section gradient-bg">
        <div className="container">
          <div className="hero-content">
            <h1 className="hero-title">
              Automated Answer Sheet Evaluation System
            </h1>
            <p className="hero-description">
              Get instant, AI-powered feedback on your academic answers. Upload your answer scripts and receive detailed evaluation, scores, and improvement suggestions within minutes.
            </p>
            <Link to="/upload" className="hero-btn btn btn-primary btn-lg">
              Upload Answer Sheet
            </Link>
          </div>
          
          <div className="hero-image">
            <img 
              src="/api/placeholder/500/400" 
              alt="Answer sheet evaluation illustration" 
              className="illustration"
            />
          </div>
        </div>
      </section>
      
      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="container">
          <h2 className="section-title">How It Works</h2>
          
          <div className="steps-container">
            <div className="step-card">
              <div className="step-number">1</div>
              <div className="step-icon">
                <svg width="50" height="50" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M13 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V9L13 2Z" 
                    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M13 2V9H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h3 className="step-title">Upload Answer Script</h3>
              <p className="step-description">
                Upload your answer script in PDF, DOC, or DOCX format. Select your subject, year, and semester.
              </p>
            </div>
            
            <div className="step-card">
              <div className="step-number">2</div>
              <div className="step-icon">
                <svg width="50" height="50" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" 
                    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M12 16V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M12 8H12.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h3 className="step-title">AI Evaluation</h3>
              <p className="step-description">
                Our advanced language model analyzes your answers, comparing them with ideal responses based on academic standards.
              </p>
            </div>
            
            <div className="step-card">
              <div className="step-number">3</div>
              <div className="step-icon">
                <svg width="50" height="50" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M22 11.08V12C21.9988 14.1564 21.3005 16.2547 20.0093 17.9818C18.7182 19.709 16.9033 20.9725 14.8354 21.5839C12.7674 22.1953 10.5573 22.1219 8.53447 21.3746C6.51168 20.6273 4.78465 19.2461 3.61096 17.4371C2.43727 15.628 1.87979 13.4881 2.02168 11.3363C2.16356 9.18455 2.99721 7.13631 4.39828 5.49706C5.79935 3.85781 7.69279 2.71537 9.79619 2.24013C11.8996 1.7649 14.1003 1.98232 16.07 2.85999" 
                    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M22 4L12 14.01L9 11.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h3 className="step-title">Get Detailed Feedback</h3>
              <p className="step-description">
                Receive comprehensive evaluation with scores, strengths, areas for improvement, and specific feedback for each answer.
              </p>
            </div>
          </div>
        </div>
      </section>
      
      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <h2 className="section-title">Features</h2>
          
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 3V21H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M20 8L12 16L8 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h3 className="feature-title">Objective Evaluation</h3>
              <p className="feature-description">
                Consistent and unbiased assessment of answers based on academic criteria.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 8V12L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" 
                    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h3 className="feature-title">Instant Results</h3>
              <p className="feature-description">
                Get evaluation results within minutes, no more waiting for days.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M9 11L12 14L22 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M21 12V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H16" 
                    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <h3 className="feature-title">Detailed Feedback</h3>
              <p className="feature-description">
                Receive specific comments, suggestions, and improvement tips for each answer.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M8 3V6M16 3V6M3 9H21M5 3H19C20.1046 3 21 3.89543 21 5V19C21 20.1046 20.1046 21 19 21H5C3.89543 21 3 20.1046 3 19V5C3 3.89543 3.89543 3 5 3Z" 
                    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <rect x="9" y="13" width="2" height="2" fill="currentColor"/>
                  <rect x="13" y="13" width="2" height="2" fill="currentColor"/>
                  <rect x="9" y="17" width="2" height="2" fill="currentColor"/>
                  <rect x="13" y="17" width="2" height="2" fill="currentColor"/>
                </svg>
              </div>
              <h3 className="feature-title">Progress Tracking</h3>
              <p className="feature-description">
                Monitor your academic progress over time through multiple evaluations.
              </p>
            </div>
          </div>
        </div>
      </section>
      
      {/* CTA Section */}
      <section className="cta-section gradient-bg">
        <div className="container">
          <div className="cta-content">
            <h2 className="section-title">Ready to Get Started?</h2>
            <p className="cta-text">
              Upload your answer sheet and get instant, AI-powered evaluation and feedback.
            </p>
            <div className="cta-buttons">
              <Link to="/upload" className="cta-btn btn btn-primary btn-lg">
                Upload Answer Sheet
              </Link>
              <Link to="/evaluation" className="cta-btn btn btn-secondary btn-lg">
                Evaluate Answer Sheets
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;