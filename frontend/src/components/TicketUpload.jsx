import { useState, useRef } from 'react';
import { Upload, Loader2, AlertCircle, FileText, File, X } from 'lucide-react';
import api from '../api/axiosConfig';
import RecommendationPanel from './RecommendationPanel';
import PriorityAnalysis from './PriorityAnalysis';

const TicketUpload = () => {
  const [ticketText, setTicketText] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [inputMode, setInputMode] = useState('text'); // 'text' or 'file'
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [priorityResult, setPriorityResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const analyzePriority = (text) => {
    const lowerText = text.toLowerCase();
    
    // High priority keywords
    const highPriorityKeywords = [
      'error', 'failed', 'urgent', 'critical', 'not working', 'crash', 'down', 'issue immediately'
    ];
    
    // Medium priority keywords
    const mediumPriorityKeywords = [
      'delay', 'problem', 'help', 'trouble', 'stuck', 'confusion', 'question'
    ];
    
    // Check for high priority keywords
    const hasHighPriority = highPriorityKeywords.some(keyword => 
      lowerText.includes(keyword)
    );
    
    // Check for medium priority keywords
    const hasMediumPriority = mediumPriorityKeywords.some(keyword => 
      lowerText.includes(keyword)
    );
    
    // Determine priority
    let priority = 'low';
    let confidence = 0.7;
    
    if (hasHighPriority) {
      priority = 'high';
      confidence = 0.9;
    } else if (hasMediumPriority) {
      priority = 'medium';
      confidence = 0.8;
    }
    
    return { priority, confidence };
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Check file type (only allow text files)
      const allowedTypes = ['text/plain', 'application/json', 'text/csv'];
      if (!allowedTypes.includes(file.type) && !file.name.endsWith('.txt')) {
        setError('Please upload a text file (.txt, .json, .csv)');
        return;
      }

      // Check file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('File size must be less than 5MB');
        return;
      }

      setUploadedFile(file);
      setError(null);
      setAnalysisResult(null); // Reset previous results
      setPriorityResult(null); // Reset previous priority results
      
      // Read file content and set it to ticketText
      const reader = new FileReader();
      reader.onload = (e) => {
        setTicketText(e.target.result);
      };
      reader.readAsText(file);
    }
  };

  const removeFile = () => {
    setUploadedFile(null);
    setTicketText('');
    setAnalysisResult(null); // Reset previous results
    setPriorityResult(null); // Reset previous priority results
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleAnalyze = async () => {
    if (!ticketText.trim()) {
      setError('Please enter a support ticket or upload a file before analyzing.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysisResult(null);
    setPriorityResult(null);

    try {
      // Perform priority analysis first (client-side)
      const priorityAnalysis = analyzePriority(ticketText.trim());
      setPriorityResult(priorityAnalysis);

      let response;
      
      // Use file upload endpoint if file is provided, otherwise use text endpoint
      if (uploadedFile && inputMode === 'file') {
        // Use FormData for file upload
        const formData = new FormData();
        formData.append('file', uploadedFile);
        
        response = await api.post('/api/analyze_ticket_file', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      } else {
        // Use text endpoint
        response = await api.post('/api/analyze_ticket', {
          text: ticketText.trim(),
          file_name: uploadedFile ? uploadedFile.name : null
        });
      }

      setAnalysisResult(response.data);
    } catch (err) {
      // For development, create a mock response when API fails
      console.log('API not available, using mock data');
      
      // Mock analysis result
      const mockResult = {
        category: 'Technical Issue',
        confidence: 0.85,
        suggested_article: 'How to troubleshoot login issues',
        keywords: ['login', 'authentication', 'password'],
        sentiment: 'negative',
        priority: priorityResult?.priority || 'medium',
        source: uploadedFile ? `File: ${uploadedFile.name}` : 'Text input'
      };
      
      setAnalysisResult(mockResult);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClear = () => {
    setTicketText('');
    setUploadedFile(null);
    setAnalysisResult(null);
    setPriorityResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="card">
        <div className="flex items-center space-x-3 mb-4">
          <Upload className="w-6 h-6 text-primary-600" />
          <h2 className="text-xl font-semibold text-gray-900">Upload Support Ticket</h2>
        </div>
        
        <div className="space-y-4">
          {/* Input Mode Toggle */}
          <div className="flex space-x-4 mb-4">
            <button
              onClick={() => setInputMode('text')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                inputMode === 'text'
                  ? 'bg-primary-100 text-primary-600 border border-primary-200'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              disabled={isAnalyzing}
            >
              <FileText className="w-4 h-4" />
              <span>Text Input</span>
            </button>
            <button
              onClick={() => setInputMode('file')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                inputMode === 'file'
                  ? 'bg-primary-100 text-primary-600 border border-primary-200'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              disabled={isAnalyzing}
            >
              <File className="w-4 h-4" />
              <span>File Upload</span>
            </button>
          </div>

          {/* File Upload Section */}
          {inputMode === 'file' && (
            <div className="space-y-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload Support Ticket File
              </label>
              
              {/* File Upload Area */}
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-400 transition-colors">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".txt,.json,.csv,text/plain,application/json,text/csv"
                  onChange={handleFileUpload}
                  className="hidden"
                  disabled={isAnalyzing}
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isAnalyzing}
                  className="btn-primary flex items-center space-x-2 mx-auto disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Upload className="w-4 h-4" />
                  <span>Choose File</span>
                </button>
                <p className="text-sm text-gray-500 mt-2">
                  Supported formats: .txt, .json, .csv (max 5MB)
                </p>
              </div>

              {/* Uploaded File Display */}
              {uploadedFile && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <File className="w-5 h-5 text-green-600" />
                      <div>
                        <p className="font-medium text-green-800">{uploadedFile.name}</p>
                        <p className="text-sm text-green-600">
                          {(uploadedFile.size / 1024).toFixed(1)} KB
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={removeFile}
                      className="text-green-600 hover:text-green-800 transition-colors"
                      disabled={isAnalyzing}
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Text Input Section */}
          {inputMode === 'text' && (
            <div>
              <label htmlFor="ticket-text" className="block text-sm font-medium text-gray-700 mb-2">
                Ticket Content
              </label>
              <textarea
                id="ticket-text"
                value={ticketText}
                onChange={(e) => {
                  setTicketText(e.target.value);
                  // Reset results when user changes text
                  if (analysisResult || priorityResult) {
                    setAnalysisResult(null);
                    setPriorityResult(null);
                  }
                }}
                placeholder="Paste your customer support ticket here..."
                className="input-field min-h-[200px] resize-y"
                disabled={isAnalyzing}
              />
              <p className="text-sm text-gray-500 mt-2">
                Enter the full text of the support ticket for AI analysis and recommendations.
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-3">
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing || (!ticketText.trim() && !uploadedFile)}
              className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>{inputMode === 'file' ? 'Analyze File' : 'Analyze Ticket'}</span>
                </>
              )}
            </button>
            
            <button
              onClick={handleClear}
              disabled={isAnalyzing}
              className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-center space-x-2 text-red-600">
            <AlertCircle className="w-5 h-5" />
            <span className="font-medium">Error</span>
          </div>
          <p className="text-red-600 mt-1">{error}</p>
        </div>
      )}

      {/* Priority Analysis Results */}
      {priorityResult && (
        <PriorityAnalysis 
          priority={priorityResult.priority} 
          confidence={priorityResult.confidence} 
        />
      )}

      {/* Analysis Results */}
      {analysisResult && (
        <RecommendationPanel result={analysisResult} />
      )}
    </div>
  );
};

export default TicketUpload;
