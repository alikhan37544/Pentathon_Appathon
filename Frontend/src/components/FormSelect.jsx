import React from 'react';
import './FormSelect.css';

const FormSelect = ({ 
  label, 
  name, 
  value, 
  onChange, 
  options, 
  placeholder = 'Select an option', 
  error 
}) => {
  return (
    <div className="form-select-container">
      {label && <label className="form-label" htmlFor={name}>{label}</label>}
      
      <div className={`select-wrapper ${error ? 'has-error' : ''}`}>
        <select
          id={name}
          name={name}
          value={value}
          onChange={onChange}
          className="form-select"
        >
          <option value="" disabled>{placeholder}</option>
          {options.map((option, index) => (
            <option key={index} value={option.value || option}>
              {option.label || option}
            </option>
          ))}
        </select>
        
        <svg className="select-arrow" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
          <path fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 9l6 6 6-6"/>
        </svg>
      </div>
      
      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

export default FormSelect;