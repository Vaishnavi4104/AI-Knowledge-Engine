import { motion } from 'framer-motion';
import { AlertTriangle, AlertCircle, CheckCircle } from 'lucide-react';

const PriorityAnalysis = ({ priority, confidence = 0.85 }) => {
  const getPriorityConfig = (priority) => {
    switch (priority.toLowerCase()) {
      case 'high':
        return {
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          textColor: 'text-red-800',
          titleColor: 'text-red-900',
          icon: <AlertTriangle className="w-6 h-6 text-red-600" />,
          badgeColor: 'bg-red-100 text-red-800',
          emoji: '🔴'
        };
      case 'medium':
        return {
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          textColor: 'text-yellow-800',
          titleColor: 'text-yellow-900',
          icon: <AlertCircle className="w-6 h-6 text-yellow-600" />,
          badgeColor: 'bg-yellow-100 text-yellow-800',
          emoji: '🟡'
        };
      case 'low':
        return {
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          textColor: 'text-green-800',
          titleColor: 'text-green-900',
          icon: <CheckCircle className="w-6 h-6 text-green-600" />,
          badgeColor: 'bg-green-100 text-green-800',
          emoji: '🟢'
        };
      default:
        return {
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          textColor: 'text-gray-800',
          titleColor: 'text-gray-900',
          icon: <AlertCircle className="w-6 h-6 text-gray-600" />,
          badgeColor: 'bg-gray-100 text-gray-800',
          emoji: '⚪'
        };
    }
  };

  const config = getPriorityConfig(priority);
  const confidencePercentage = Math.round(confidence * 100);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ 
        duration: 0.5,
        ease: "easeOut",
        type: "spring",
        stiffness: 100
      }}
      className={`${config.bgColor} ${config.borderColor} border rounded-xl p-4 shadow-md`}
    >
      <div className="flex items-center space-x-3">
        <div className="flex-shrink-0">
          {config.icon}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-2xl">{config.emoji}</span>
            <h3 className={`text-lg font-semibold ${config.titleColor}`}>
              Priority Analysis
            </h3>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium ${config.badgeColor}`}>
              {priority.toUpperCase()} Priority
            </span>
            <span className={`text-sm ${config.textColor}`}>
              {confidencePercentage}% confidence
            </span>
          </div>
        </div>
      </div>

      {/* Priority Description */}
      <div className={`mt-3 ${config.textColor}`}>
        <p className="text-sm">
          {priority.toLowerCase() === 'high' && 
            'This ticket requires immediate attention due to critical keywords detected.'}
          {priority.toLowerCase() === 'medium' && 
            'This ticket indicates a moderate issue that should be addressed soon.'}
          {priority.toLowerCase() === 'low' && 
            'This ticket appears to be a routine inquiry or minor issue.'}
        </p>
      </div>

      {/* Confidence Bar */}
      <div className="mt-3">
        <div className="flex items-center justify-between text-xs mb-1">
          <span className={`${config.textColor}`}>Confidence</span>
          <span className={`${config.textColor}`}>{confidencePercentage}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-1.5">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${confidencePercentage}%` }}
            transition={{ duration: 1, delay: 0.3, ease: "easeOut" }}
            className={`h-1.5 rounded-full ${
              priority.toLowerCase() === 'high' ? 'bg-red-500' :
              priority.toLowerCase() === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
            }`}
          />
        </div>
      </div>
    </motion.div>
  );
};

export default PriorityAnalysis;
