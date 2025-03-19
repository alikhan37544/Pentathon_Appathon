import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FormSelect from '../components/FormSelect';
import FileUploader from '../components/FileUploader';
import LoadingSpinner from '../components/LoadingSpinner';
import { useEvaluation } from '../contexts/EvaluationContext';
import './UploadPage.css';

const UploadPage = () => {
  const navigate = useNavigate();
  const { submitAnswerSheet, isLoading } = useEvaluation();
  
  // Form state
  const [formData, setFormData] = useState({
    subject: '',
    year: '',
    semester: '',
    file: null
  });
  
  // Form validation errors
  const [errors, setErrors] = useState({});
  
  // Progress state for simulating LLM processing
  const [progress, setProgress] = useState(0);
  
  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
    
    // Clear error for this field if it exists
    if (errors[name]) {
      setErrors(prevState => ({
        ...prevState,
        [name]: ''
      }));
    }
  };
  
  // Handle file selection
  const handleFileChange = (file) => {
    setFormData(prevState => ({
      ...prevState,
      file
    }));
    
    // Clear error for file if it exists
    if (errors.file) {
      setErrors(prevState => ({
        ...prevState,
        file: ''
      }));
    }
  };
  
  // Validate form before submission
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.subject) {
      newErrors.subject = 'Please select a subject';
    }
    
    if (!formData.year) {
      newErrors.year = 'Please select your year';
    }
    
    if (!formData.semester) {
      newErrors.semester = 'Please select your semester';
    }
    
    if (!formData.file) {
      newErrors.file = 'Please upload your answer script';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    // Start progress simulation
    let progressValue = 0;
    const progressInterval = setInterval(() => {
      progressValue += 5;
      if (progressValue >= 95) {
        clearInterval(progressInterval);
        progressValue = 95;
      }
      setProgress(progressValue);
    }, 300);
    
    // Create form data for API call
    const apiFormData = new FormData();
    apiFormData.append('subject', formData.subject);
    apiFormData.append('year', formData.year);
    apiFormData.append('semester', formData.semester);
    apiFormData.append('file', formData.file);
    
    // Submit the form
    const evaluationId = await submitAnswerSheet(apiFormData);
    
    // Clean up and navigate
    clearInterval(progressInterval);
    setProgress(100);
    
    if (evaluationId) {
      setTimeout(() => {
        navigate(`/results/${evaluationId}`);
      }, 500);
    }
  };
  
  // Subject options
  const subjects = [
    'Mathematics',
    'Physics',
    'Chemistry',
    'Biology',
    'Computer Science',
    'English Literature',
    'History',
    'Geography',
    'Economics',
    'Psychology'
  ];
  
  // Year options
  const years = ['1st Year', '2nd Year', '3rd Year', '4th Year'];
  
  // Semester options
  const semesters = [
    '1st Semester',
    '2nd Semester',
    '3rd Semester',
    '4th Semester',
    '5th Semester',
    '6th Semester',
    '7th Semester',
    '8th Semester'
  ];
  
  return (
    <div className="upload-page">
      <div className="upload-container">
        <div className="upload-card">
          <div className="upload-header gradient-bg">
            <h1 className="upload-title">ANSWER SHEET EVALUATION</h1>
            <p className="upload-subtitle">
              Upload your answer script and get instant AI-powered feedback
            </p>
          </div>
          
          <div className="upload-content">
            {isLoading ? (
              <div className="loading-wrapper">
                <LoadingSpinner 
                  message="Processing your answer sheet..." 
                  progress={progress} 
                />
                <p className="processing-message">
                  Our AI is analyzing your answers, comparing them to ideal responses, 
                  and providing detailed feedback. This may take a moment.
                </p>
              </div>
            ) : (
              <form className="upload-form" onSubmit={handleSubmit}>
                <FormSelect
                  label="Select Subject"
                  name="subject"
                  value={formData.subject}
                  onChange={handleInputChange}
                  options={subjects}
                  placeholder="-- Select Subject --"
                  error={errors.subject}
                />
                
                <FormSelect
                  label="College Year"
                  name="year"
                  value={formData.year}
                  onChange={handleInputChange}
                  options={years}
                  placeholder="-- Select Year --"
                  error={errors.year}
                />
                
                <FormSelect
                  label="Current Semester"
                  name="semester"
                  value={formData.semester}
                  onChange={handleInputChange}
                  options={semesters}
                  placeholder="-- Select Semester --"
                  error={errors.semester}
                />
                
                <div className="form-group">
                  <label className="form-label">Upload Answer Script</label>
                  <FileUploader
                    onFileChange={handleFileChange}
                    acceptedFileTypes=".pdf,.doc,.docx"
                    error={errors.file}
                  />
                </div>
                
                <div className="form-actions">
                  <button type="submit" className="btn btn-primary btn-lg submit-btn">
                    Submit for Evaluation
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;