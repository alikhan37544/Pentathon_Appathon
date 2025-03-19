import React, { useState, useRef } from 'react';
import './FileUploader.css';

const FileUploader = ({ onFileChange, acceptedFileTypes = '.pdf,.doc,.docx', error }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState('');
  const fileInputRef = useRef(null);
  
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileName(file.name);
      onFileChange(file);
    }
  };
  
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };
  
  const handleDragLeave = () => {
    setIsDragging(false);
  };
  
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files[0];
    if (file) {
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
      if (acceptedFileTypes.includes(fileExtension)) {
        setFileName(file.name);
        onFileChange(file);
      } else {
        alert(`Please upload files with these formats: ${acceptedFileTypes}`);
      }
    }
  };
  
  const handleClick = () => {
    fileInputRef.current.click();
  };
  
  return (
    <div className="file-uploader-container">
      <div 
        className={`file-uploader ${isDragging ? 'dragging' : ''} ${error ? 'has-error' : ''} ${fileName ? 'has-file' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input 
          type="file" 
          ref={fileInputRef}
          onChange={handleFileChange}
          accept={acceptedFileTypes}
          className="file-input"
        />
        
        <div className="file-uploader-content">
          <div className="file-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M13 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V9L13 2Z" 
                stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M13 2V9H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M12 18V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M9 15L12 18L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          
          {fileName ? (
            <div className="file-info">
              <div className="file-name">{fileName}</div>
              <p className="file-hint">Click or drag to replace</p>
            </div>
          ) : (
            <div className="file-info">
              <p className="file-instruction">Drag and drop your answer sheet here</p>
              <p className="file-hint">or click to browse files</p>
              <p className="file-formats">Supported formats: PDF, DOC, DOCX</p>
            </div>
          )}
        </div>
      </div>
      
      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

export default FileUploader;