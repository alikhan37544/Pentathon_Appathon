import React, { createContext, useState, useContext } from 'react';

// Create the evaluation context
const EvaluationContext = createContext();

// Custom hook to use the evaluation context
export const useEvaluation = () => useContext(EvaluationContext);

// Provider component for the evaluation context
export const EvaluationProvider = ({ children }) => {
  // State for evaluation data
  const [evaluationData, setEvaluationData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedQuestionId, setSelectedQuestionId] = useState(null);
  
  // Mock function to simulate submitting an answer sheet for evaluation
  const submitAnswerSheet = async (formData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // In a real application, this would make an API call to your backend
      // For demo purposes, we'll simulate a network delay and return mock data
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock evaluation ID (in a real app, this would come from your API)
      const evaluationId = 'eval-' + Date.now();
      
      // Return the evaluation ID
      return evaluationId;
    } catch (err) {
      setError('Failed to submit answer sheet. Please try again.');
      return null;
    } finally {
      setIsLoading(false);
    }
  };
  
  // Mock function to simulate fetching evaluation results
  const fetchEvaluationResults = async (evaluationId) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // In a real application, this would make an API call to your backend
      // For demo purposes, we'll simulate a network delay and return mock data
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock evaluation data
      const mockEvaluationData = {
        id: evaluationId,
        studentName: 'John Doe',
        studentId: 'S12345',
        subject: 'Computer Science',
        year: '3rd Year',
        semester: '5th Semester',
        submissionDate: new Date().toISOString(),
        overallScore: 85,
        maxScore: 100,
        questions: [
          {
            id: 1,
            questionNumber: 1,
            questionText: 'Explain the concept of Object-Oriented Programming and its main principles.',
            studentAnswer: 'Object-Oriented Programming (OOP) is a programming paradigm based on the concept of objects, which can contain data and code. The four main principles of OOP are Encapsulation, Inheritance, Polymorphism, and Abstraction.',
            score: 9,
            maxScore: 10,
            feedback: 'Great explanation of OOP concepts. You covered all four main principles. To improve, consider providing specific examples of each principle in action.',
            strengths: ['Correctly identified all four principles', 'Clear definition of OOP'],
            improvements: ['Could provide specific examples', 'More details on how these principles interact']
          },
          {
            id: 2,
            questionNumber: 2,
            questionText: 'Describe the working of TCP/IP protocol stack with the help of its layered architecture.',
            studentAnswer: 'TCP/IP protocol stack consists of four layers: Application Layer, Transport Layer, Internet Layer, and Network Interface Layer. Each layer has specific protocols and functions, and data is encapsulated as it moves down the stack and decapsulated as it moves up.',
            score: 8,
            maxScore: 10,
            feedback: 'Good overview of the TCP/IP layers. You correctly identified all four layers. To improve, elaborate on the specific protocols at each layer and explain the encapsulation process in more detail.',
            strengths: ['Identified all four layers correctly', 'Mentioned encapsulation concept'],
            improvements: ['Could list specific protocols for each layer', 'More details on the encapsulation process']
          },
          {
            id: 3,
            questionNumber: 3,
            questionText: 'Explain the concept of dynamic programming with a suitable example.',
            studentAnswer: 'Dynamic programming is an algorithmic technique where complex problems are broken down into simpler subproblems. It stores the results of subproblems to avoid redundant calculations. The Fibonacci sequence is a classic example of dynamic programming application.',
            score: 7,
            maxScore: 10,
            feedback: 'Decent explanation of dynamic programming. You captured the essence of storing subproblem results. To improve, provide a more detailed example showing both recursive and dynamic programming approaches to the same problem, highlighting the efficiency gain.',
            strengths: ['Correct basic definition', 'Mentioned an appropriate example (Fibonacci)'],
            improvements: ['Could show code examples of both approaches', 'Explain memoization vs tabulation', 'Analyze time complexity improvement']
          },
          {
            id: 4,
            questionNumber: 4,
            questionText: 'Compare and contrast between various sorting algorithms in terms of time complexity and space efficiency.',
            studentAnswer: 'Sorting algorithms can be compared based on time complexity and space efficiency. Quick Sort has an average time complexity of O(n log n) but worst case O(n²). Merge Sort has a consistent O(n log n) time complexity but requires O(n) extra space. Bubble Sort and Insertion Sort have O(n²) time complexity but only O(1) extra space requirement.',
            score: 10,
            maxScore: 10,
            feedback: 'Excellent comparison of sorting algorithms. You correctly analyzed both time and space complexities for multiple algorithms and highlighted the trade-offs between them.',
            strengths: ['Comprehensive coverage of multiple algorithms', 'Correct analysis of both time and space complexity', 'Clear comparisons between algorithms'],
            improvements: []
          },
          {
            id: 5,
            questionNumber: 5,
            questionText: 'Discuss the implications of Artificial Intelligence in modern healthcare systems.',
            studentAnswer: 'AI in healthcare has numerous implications, including improved diagnostic accuracy, personalized treatment plans, and efficient hospital management. AI can analyze medical images, predict disease outbreaks, and assist in drug discovery. However, challenges include data privacy concerns, regulatory issues, and the need for human oversight.',
            score: 8,
            maxScore: 10,
            feedback: 'Good overview of AI applications in healthcare. You covered both benefits and challenges. To improve, include specific case studies or examples of successful AI implementations in healthcare settings and discuss ethical considerations in more detail.',
            strengths: ['Balanced perspective covering benefits and challenges', 'Mentioned diverse applications of AI in healthcare'],
            improvements: ['Could include specific real-world examples', 'More discussion on ethical implications', 'Address the human-AI collaboration aspect']
          }
        ]
      };
      
      setEvaluationData(mockEvaluationData);
      setSelectedQuestionId(mockEvaluationData.questions[0].id);
      return mockEvaluationData;
    } catch (error) {
      setError('Failed to load evaluation results. Please try again.');
      return null;
    } finally {
      setIsLoading(false);
    }
  };
  
  // Context value
  const value = {
    evaluationData,
    isLoading,
    error,
    selectedQuestionId,
    setSelectedQuestionId,
    submitAnswerSheet,
    fetchEvaluationResults
  };
  
  return (
    <EvaluationContext.Provider value={value}>
      {children}
    </EvaluationContext.Provider>
  );
};