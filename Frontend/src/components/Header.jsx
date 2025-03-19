import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <div className="container header-container">
        <Link to="/" className="header-logo">
          <h1>EduGrader</h1>
        </Link>
        <nav className="header-nav">
          <Link to="/upload" className="nav-link">Upload Answer Sheet</Link>
          <Link to="/evaluation" className="nav-link">Evaluate Answers</Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;