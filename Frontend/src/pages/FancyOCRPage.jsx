import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUploader from '../components/FileUploader';
import LoadingSpinner from '../components/LoadingSpinner';
import './FancyOCRPage.css';

const FancyOCRPage = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [result, setResult] = useState('');
  const [error, setError] = useState('');
  
  // Handle file change from FileUploader
  const handleFileChange = (file) => {
    setImageFile(file);
    setError('');
    
    // Create a preview URL for the image
    if (file) {
      const previewUrl = URL.createObjectURL(file);
      setImagePreview(previewUrl);
    } else {
      setImagePreview(null);
    }
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate file selection
    if (!imageFile) {
      setError('Please select an image to process');
      return;
    }
    
    // Start loading indicator
    setIsLoading(true);
    setProgress(0);
    setMessage('Preparing to analyze your image...');
    setResult('');
    
    try {
      // Create form data for API call
      const formData = new FormData();
      formData.append('image', imageFile);
      
      // Upload the image
      const uploadResponse = await fetch('/api/ocr/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json();
        throw new Error(errorData.message || 'Failed to upload image');
      }
      
      // Start polling for status
      const statusCheckInterval = setInterval(async () => {
        try {
          const statusResponse = await fetch('/api/ocr/status');
          
          if (!statusResponse.ok) {
            clearInterval(statusCheckInterval);
            throw new Error('Failed to check OCR status');
          }
          
          const statusData = await statusResponse.json();
          
          // Update progress
          setProgress(statusData.progress);
          setMessage(statusData.message);
          
          // Check if complete or error
          if (statusData.complete) {
            clearInterval(statusCheckInterval);
            setIsLoading(false);
            setResult(statusData.result);
          } else if (statusData.error) {
            clearInterval(statusCheckInterval);
            setIsLoading(false);
            setError(statusData.error);
          }
        } catch (err) {
          clearInterval(statusCheckInterval);
          setIsLoading(false);
          setError(`Error checking OCR status: ${err.message}`);
        }
      }, 1000); // Check every second
      
    } catch (err) {
      setIsLoading(false);
      setError(`Error: ${err.message}`);
    }
  };
  
  // Clean up preview URLs when component unmounts
  useEffect(() => {
    return () => {
      if (imagePreview) {
        URL.revokeObjectURL(imagePreview);
      }
    };
  }, [imagePreview]);
  
  const copyToClipboard = () => {
    navigator.clipboard.writeText(result).then(
      () => {
        // Show temporary success message
        const originalMessage = message;
        setMessage('Text copied to clipboard!');
        setTimeout(() => setMessage(originalMessage), 2000);
      },
      (err) => {
        console.error('Could not copy text: ', err);
      }
    );
  };
  
  return (
    <div className="fancy-ocr-container">
      <div className="ocr-header">
        <div className="ocr-header-content">
          <h1 className="ocr-title">FancyOCR</h1>
          <p className="ocr-subtitle">
            Extract text from images using advanced AI vision
          </p>
        </div>
      </div>
      
      <div className="ocr-content">
        {isLoading ? (
          <div className="loading-wrapper">
            <LoadingSpinner 
              message={message} 
              progress={progress} 
            />
            <p className="processing-message">
              Our AI is analyzing your image and extracting text. 
              This may take a moment depending on the complexity of the image.
            </p>
          </div>
        ) : (
          <div className="ocr-main-content">
            <div className="ocr-uploader-section">
              <form className="ocr-form" onSubmit={handleSubmit}>
                <div className="form-group">
                  <label className="form-label">Upload an Image</label>
                  <FileUploader
                    onFileChange={handleFileChange}
                    acceptedFileTypes="image/*"
                    error={error}
                  />
                </div>
                
                {imagePreview && (
                  <div className="image-preview-container">
                    <img 
                      src={imagePreview} 
                      alt="Preview" 
                      className="image-preview" 
                    />
                  </div>
                )}
                
                <div className="form-actions">
                  <button 
                    type="submit" 
                    className="btn btn-primary btn-lg submit-btn"
                    disabled={!imageFile || isLoading}
                  >
                    Extract Text
                  </button>
                </div>
              </form>
            </div>
            
            {result && (
              <div className="result-section">
                <div className="result-header">
                  <h3>Extracted Text</h3>
                  <button 
                    className="btn btn-secondary btn-sm copy-btn"
                    onClick={copyToClipboard}
                  >
                    Copy to Clipboard
                  </button>
                </div>
                <pre className="result-text">{result}</pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default FancyOCRPage;