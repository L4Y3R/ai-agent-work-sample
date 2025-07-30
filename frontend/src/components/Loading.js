import React from 'react';

const Loading = ({ message = 'Analyzing data...' }) => {
  return (
    <div className="flex justify-start mb-4" role="status" aria-live="polite">
      <div className="bg-gray-100 dark:bg-gray-700 rounded-lg px-4 py-2">
        <div className="flex items-center space-x-2">
          <div 
            className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"
            aria-hidden="true"
          />
          <span className="text-sm text-gray-600 dark:text-white">
            {message}
          </span>
        </div>
      </div>
    </div>
  );
};

export default Loading;