import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Login from './Login';
import './Header.css';

const Header = () => {
  const [showLogin, setShowLogin] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userType, setUserType] = useState(null); // 'student' or 'teacher'
  
  const handleLoginClick = () => {
    setShowLogin(true);
  };
  
  const handleCloseLogin = () => {
    setShowLogin(false);
  };
  
  const handleSuccessfulLogin = (type) => {
    setIsLoggedIn(true);
    setUserType(type);
    setShowLogin(false);
  };
  
  const handleLogout = () => {
    setIsLoggedIn(false);
    setUserType(null);
  };
  
  return (
    <header className="header">
      <div className="container header-container">
        <Link to="/" className="header-logo">
          <h1>EduGrader</h1>
        </Link>
        <nav className="header-nav">
          <Link to="/upload" className="nav-link">Upload Answer Sheet</Link>
          
          {isLoggedIn ? (
            <div className="user-menu">
              <span className="user-type">{userType === 'student' ? 'Student' : 'Teacher'}</span>
              <button className="auth-btn logout-btn" onClick={handleLogout}>
                Logout
              </button>
            </div>
          ) : (
            <button className="auth-btn login-btn" onClick={handleLoginClick}>
              Login
            </button>
          )}
        </nav>
      </div>
      
      {showLogin && (
        <Login 
          onClose={handleCloseLogin} 
          onSuccess={handleSuccessfulLogin}
        />
      )}
    </header>
  );
};

export default Header;