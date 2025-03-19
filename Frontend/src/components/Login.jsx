import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Login.css';

const Login = ({ onClose, onSuccess }) => {
  const [activeTab, setActiveTab] = useState('register');
  const [activeUserType, setActiveUserType] = useState('student');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    confirmPassword: '',
    rememberMe: false
  });
  const [errors, setErrors] = useState({});

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    const inputValue = type === 'checkbox' ? checked : value;
    
    setFormData(prevState => ({
      ...prevState,
      [name]: inputValue
    }));
    
    // Clear error for this field if it exists
    if (errors[name]) {
      setErrors(prevState => ({
        ...prevState,
        [name]: ''
      }));
    }
  };

  const validateLoginForm = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateRegisterForm = () => {
    const newErrors = {};
    
    if (!formData.name) {
      newErrors.name = 'Name is required';
    }
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (activeTab === 'login' && validateLoginForm()) {
      // In a real app, you would send this data to your backend
      console.log('Login form submitted:', formData);
      
      // Simulate successful login
      if (onSuccess) {
        onSuccess(activeUserType);
      }
      
      // Close the modal if provided
      if (onClose) {
        onClose();
      }
    } else if (activeTab === 'register' && validateRegisterForm()) {
      // In a real app, you would send this data to your backend
      console.log('Register form submitted:', formData);
      
      // Simulate successful registration and login
      if (onSuccess) {
        onSuccess(activeUserType);
      }
      
      // Close the modal if provided
      if (onClose) {
        onClose();
      }
    }
  };

  return (
    <div className="login-overlay" onClick={onClose}>
      <div className="login-container" onClick={(e) => e.stopPropagation()}>
        <div className="login-header">
          <div className="login-tabs">
            <button 
              className={`login-tab-btn ${activeTab === 'login' ? 'active' : ''}`}
              onClick={() => setActiveTab('login')}
            >
              Login
            </button>
            <button 
              className={`login-tab-btn ${activeTab === 'register' ? 'active' : ''}`}
              onClick={() => setActiveTab('register')}
            >
              Register
            </button>
          </div>
          {onClose && (
            <button className="close-btn" onClick={onClose}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          )}
        </div>
        
        <div className="login-content">
          <div className="user-type-selector">
            <button 
              className={`user-type-btn ${activeUserType === 'student' ? 'active' : ''}`}
              onClick={() => setActiveUserType('student')}
            >
              Student
            </button>
            <button 
              className={`user-type-btn ${activeUserType === 'teacher' ? 'active' : ''}`}
              onClick={() => setActiveUserType('teacher')}
            >
              Teacher
            </button>
          </div>
          
          <h2 className="login-title">
            {activeTab === 'login' 
              ? `${activeUserType === 'student' ? 'Student' : 'Teacher'} Login` 
              : `${activeUserType === 'student' ? 'Student' : 'Teacher'} Registration`}
          </h2>
          
          <form className="login-form" onSubmit={handleSubmit}>
            {activeTab === 'register' && (
              <div className="form-group">
                <label className="form-label" htmlFor="name">Full Name</label>
                <input 
                  type="text" 
                  id="name" 
                  name="name" 
                  className={`form-control ${errors.name ? 'has-error' : ''}`}
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="Enter your full name"
                />
                {errors.name && <div className="error-message">{errors.name}</div>}
              </div>
            )}
            
            <div className="form-group">
              <label className="form-label" htmlFor="email">Email</label>
              <input 
                type="email" 
                id="email" 
                name="email" 
                className={`form-control ${errors.email ? 'has-error' : ''}`}
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Enter your email"
              />
              {errors.email && <div className="error-message">{errors.email}</div>}
            </div>
            
            <div className="form-group">
              <label className="form-label" htmlFor="password">Password</label>
              <input 
                type="password" 
                id="password" 
                name="password" 
                className={`form-control ${errors.password ? 'has-error' : ''}`}
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Enter your password"
              />
              {errors.password && <div className="error-message">{errors.password}</div>}
            </div>
            
            {activeTab === 'register' && (
              <div className="form-group">
                <label className="form-label" htmlFor="confirmPassword">Confirm Password</label>
                <input 
                  type="password" 
                  id="confirmPassword" 
                  name="confirmPassword" 
                  className={`form-control ${errors.confirmPassword ? 'has-error' : ''}`}
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  placeholder="Confirm your password"
                />
                {errors.confirmPassword && <div className="error-message">{errors.confirmPassword}</div>}
              </div>
            )}
            
            {activeTab === 'login' && (
              <div className="form-options">
                <div className="remember-me">
                  <input 
                    type="checkbox" 
                    id="rememberMe" 
                    name="rememberMe"
                    checked={formData.rememberMe}
                    onChange={handleInputChange}
                  />
                  <label htmlFor="rememberMe">Remember me</label>
                </div>
                <Link to="/forgot-password" className="forgot-password">Forgot password?</Link>
              </div>
            )}
            
            <button type="submit" className="btn btn-primary login-btn">
              {activeTab === 'login' ? 'Login' : 'Create Account'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;