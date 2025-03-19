import React from 'react';
import { useNavigate } from 'react-router-dom';
import Login from '../components/Login';
import './LoginPage.css';

const LoginPage = () => {
  const navigate = useNavigate();
  
  const handleSuccessfulLogin = () => {
    // Redirect to dashboard or home page after successful login
    navigate('/');
  };
  
  return (
    <div className="login-page">
      <Login onSuccess={handleSuccessfulLogin} />
    </div>
  );
};

export default LoginPage;