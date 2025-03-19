import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

// Testimonial data for the slider
const testimonials = [
  {
    id: 1,
    text: "EduGrader has transformed how I learn from my assignments. The detailed feedback helped me understand my mistakes and improve my academic performance.",
    name: "Alex Johnson",
    role: "Computer Science Student"
  },
  {
    id: 2,
    text: "As a teacher, EduGrader has saved me countless hours while providing my students with more comprehensive feedback than I could manage manually.",
    name: "Dr. Sarah Williams",
    role: "Chemistry Professor"
  },
  {
    id: 3,
    text: "The AI-powered evaluation is incredibly accurate. It helped me improve my essay writing skills by identifying patterns in my mistakes.",
    name: "Michael Chen",
    role: "Literature Student"
  }
];

// Animated counter component
const AnimatedCounter = ({ end, duration = 2000, label, icon }) => {
  const [count, setCount] = useState(0);
  const countRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          let startTime = null;
          
          const animate = (timestamp) => {
            if (!startTime) startTime = timestamp;
            const progress = Math.min((timestamp - startTime) / duration, 1);
            setCount(Math.floor(progress * end));
            
            if (progress < 1) {
              window.requestAnimationFrame(animate);
            }
          };
          
          window.requestAnimationFrame(animate);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );
    
    if (countRef.current) {
      observer.observe(countRef.current);
    }
    
    return () => {
      if (countRef.current) {
        observer.unobserve(countRef.current);
      }
    };
  }, [end, duration]);

  return (
    <div className="stat-card" ref={countRef}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-content">
        <div className="stat-value">{count.toLocaleString()}+</div>
        <div className="stat-label">{label}</div>
      </div>
    </div>
  );
};

// Testimonial slider component
const TestimonialSlider = () => {
  const [current, setCurrent] = useState(0);
  
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrent((prev) => (prev + 1) % testimonials.length);
    }, 5000);
    
    return () => clearInterval(timer);
  }, []);
  
  return (
    <div className="testimonial-slider">
      <div className="testimonial-container">
        {testimonials.map((testimonial, index) => (
          <div 
            key={testimonial.id} 
            className={`testimonial-slide ${index === current ? 'active' : ''}`}
            style={{ transform: `translateX(${(index - current) * 100}%)` }}
          >
            <div className="testimonial-content">
              <p className="testimonial-text">"{testimonial.text}"</p>
              <div className="testimonial-author">
                <p className="author-name">{testimonial.name}</p>
                <p className="author-role">{testimonial.role}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="testimonial-dots">
        {testimonials.map((_, index) => (
          <button 
            key={index} 
            className={`dot ${index === current ? 'active' : ''}`}
            onClick={() => setCurrent(index)}
          />
        ))}
      </div>
    </div>
  );
};

const HomePage = () => {
  // Observe elements for scroll animation
  useEffect(() => {
    const observerOptions = {
      root: null,
      rootMargin: '0px',
      threshold: 0.1,
    };
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
          observer.unobserve(entry.target);
        }
      });
    }, observerOptions);
    
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    animatedElements.forEach(el => observer.observe(el));
    
    return () => {
      animatedElements.forEach(el => observer.unobserve(el));
    };
  }, []);

  return (
    <div className="home-page">
      {/* Hero Section with Background Image */}
      <section className="hero-section">
        <div className="container">
          <div className="hero-content animate-on-scroll">
            <h1 className="hero-title">
              Automated Answer Sheet Evaluation System
            </h1>
            <p className="hero-description">
              Get instant, AI-powered feedback on your academic answers. Upload your answer scripts and receive detailed evaluation, scores, and improvement suggestions within minutes.
            </p>
            <div className="hero-buttons">
              <Link to="/upload" className="hero-btn btn btn-primary">
                Upload Answer Sheet
              </Link>
              <Link to="/login" className="hero-btn btn btn-secondary">
                Login to Account
              </Link>
            </div>
          </div>
          <div className="hero-image animate-on-scroll">
            <img 
              src="/Chart.png" 
              alt="AI-Enhanced Learning Models" 
              className="chart-illustration"
            />
          </div>
        </div>
        
        <div className="hero-wave">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320" preserveAspectRatio="none">
            <path fill="#f8fafc" fillOpacity="1" d="M0,224L48,213.3C96,203,192,181,288,181.3C384,181,480,203,576,202.7C672,203,768,181,864,181.3C960,181,1056,203,1152,202.7C1248,203,1344,181,1392,170.7L1440,160L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path>
          </svg>
        </div>
      </section>
      
      {/* Stats Section */}
      <section className="stats-section">
        <div className="container">
          <div className="stats-grid animate-on-scroll">
            <AnimatedCounter 
              end={15000} 
              label="Students Helped" 
              icon={
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="9" cy="7" r="4"></circle>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
              }
            />
            <AnimatedCounter 
              end={200000} 
              label="Answers Evaluated" 
              icon={
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="9 11 12 14 22 4"></polyline>
                  <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                </svg>
              }
            />
            <AnimatedCounter 
              end={98} 
              label="Accuracy %" 
              icon={
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14 9 11"></polyline>
                </svg>
              }
            />
            <AnimatedCounter 
              end={120} 
              label="Educational Institutions" 
              icon={
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M2 22h20M18 2H6l-4 4v10h20V6l-4-4z"></path>
                  <path d="M12 15V9"></path>
                  <path d="M8 9h8"></path>
                </svg>
              }
            />
          </div>
        </div>
      </section>
      
      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="container">
          <h2 className="section-title animate-on-scroll">How It Works</h2>
          
          <div className="steps-container">
            <div className="step-card animate-on-scroll">
              <div className="step-number">1</div>
              <div className="step-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="#7231e3" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="12" y1="18" x2="12" y2="12"></line>
                  <line x1="9" y1="15" x2="15" y2="15"></line>
                </svg>
              </div>
              <h3 className="step-title">Upload Answer Script</h3>
              <p className="step-description">
                Upload your answer script in PDF, DOC, or DOCX format. Select your subject, year, and semester.
              </p>
            </div>
            
            <div className="step-card animate-on-scroll" style={{ animationDelay: '0.2s' }}>
              <div className="step-number">2</div>
              <div className="step-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="#7231e3" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="16" x2="12" y2="12"></line>
                  <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
              </div>
              <h3 className="step-title">AI Evaluation</h3>
              <p className="step-description">
                Our advanced language model analyzes your answers, comparing them with ideal responses based on academic standards.
              </p>
            </div>
            
            <div className="step-card animate-on-scroll" style={{ animationDelay: '0.4s' }}>
              <div className="step-number">3</div>
              <div className="step-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="#7231e3" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
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
      
      {/* Testimonials Section */}
      <section className="testimonials-section">
        <div className="container">
          <h2 className="section-title animate-on-scroll">What Our Users Say</h2>
          <div className="animate-on-scroll">
            <TestimonialSlider />
          </div>
        </div>
      </section>
      
      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <h2 className="section-title animate-on-scroll">Features</h2>
          
          <div className="features-grid">
            <div className="feature-card animate-on-scroll">
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
            
            <div className="feature-card animate-on-scroll" style={{ animationDelay: '0.2s' }}>
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
            
            <div className="feature-card animate-on-scroll" style={{ animationDelay: '0.4s' }}>
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
            
            <div className="feature-card animate-on-scroll" style={{ animationDelay: '0.6s' }}>
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
      <section className="cta-section">
        <div className="container">
          <div className="cta-content animate-on-scroll">
            <h2 className="cta-title">Ready to Improve Your Academic Performance?</h2>
            <p className="cta-description">
              Upload your answer sheet now and get detailed AI-powered feedback to enhance your learning experience.
            </p>
            <div className="cta-buttons">
              <Link to="/upload" className="cta-btn btn btn-primary">
                Start Evaluation
              </Link>
              <Link to="/login" className="cta-btn btn btn-secondary">
                Create Account
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;