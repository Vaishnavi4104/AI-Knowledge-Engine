import { CheckCircle, Tag, TrendingUp, AlertTriangle, Clock } from 'lucide-react';

const RecommendationPanel = ({ result }) => {
  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600 bg-green-50';
      case 'negative': return 'text-red-600 bg-red-50';
      case 'neutral': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const formatConfidence = (confidence) => {
    return `${Math.round(confidence * 100)}%`;
  };

  return (
    <div className="card">
      <div className="flex items-center space-x-3 mb-6">
        <CheckCircle className="w-6 h-6 text-green-600" />
        <h3 className="text-xl font-semibold text-gray-900">Analysis Results</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Category & Confidence */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category
            </label>
            <div className="flex items-center space-x-2">
              <Tag className="w-4 h-4 text-primary-600" />
              <span className="text-lg font-semibold text-gray-900">
                {result.category}
              </span>
            </div>
            <div className="mt-2 flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600">
                Confidence: {formatConfidence(result.confidence)}
              </span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sentiment
            </label>
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getSentimentColor(result.sentiment?.toLowerCase() || 'neutral')}`}>
              {result.sentiment?.charAt(0).toUpperCase() + result.sentiment?.slice(1).toLowerCase() || 'Neutral'}
            </span>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Priority
            </label>
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(result.priority?.toLowerCase() || 'low')}`}>
              <AlertTriangle className="w-3 h-3 mr-1" />
              {result.priority?.charAt(0).toUpperCase() + result.priority?.slice(1).toLowerCase() || 'Low'}
            </span>
          </div>
        </div>

        {/* Suggested Article & Keywords */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Recommended Articles
            </label>
            <div className="space-y-2">
              {(result.suggested_articles || (result.suggested_article ? [result.suggested_article] : [])).map((article, index) => (
                <div key={index} className="bg-primary-50 border border-primary-200 rounded-lg p-4">
                  <h4 className="font-medium text-primary-900">
                    {article}
                  </h4>
                  <p className="text-sm text-primary-700 mt-1">
                    This article should help resolve the customer's issue.
                  </p>
                </div>
              ))}
            </div>
          </div>

          {(result.detected_keywords || result.keywords) && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Key Topics
              </label>
              <div className="flex flex-wrap gap-2">
                {(result.detected_keywords || result.keywords || []).map((keyword, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 rounded-md text-sm"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-6 pt-6 border-t border-gray-200 flex space-x-3">
        <button className="btn-primary flex items-center space-x-2">
          <CheckCircle className="w-4 h-4" />
          <span>View Article</span>
        </button>
        <button className="btn-secondary flex items-center space-x-2">
          <Clock className="w-4 h-4" />
          <span>Track Response</span>
        </button>
      </div>
    </div>
  );
};

export default RecommendationPanel;
