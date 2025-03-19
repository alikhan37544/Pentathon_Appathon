import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import UploadPage from './pages/UploadPage';
import ResultsPage from './pages/ResultsPage';
import LoginPage from './pages/LoginPage';
import { EvaluationProvider } from './contexts/EvaluationContext';

function App() {
  return (
    <EvaluationProvider>
      <Router>
        <div className="app">
          <Header />
          <main className="app-content">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/results/:evaluationId" element={<ResultsPage />} />
              <Route path="/login" element={<LoginPage />} />
            </Routes>
          </main>
        </div>
      </Router>
    </EvaluationProvider>
  );
}

export default App;