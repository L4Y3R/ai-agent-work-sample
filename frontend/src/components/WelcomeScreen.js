import React from 'react';

const WelcomeScreen = () => {
  const exampleQuestions = [
    "What's the average CO2 level in Room 1?",
    "Show me temperature data by room",
    "Which room has the highest humidity?"
  ];

  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center text-gray-500 dark:text-gray-400 max-w-md">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-6">
          Ask me anything about your data!
        </h2>
        
        <div className="text-sm">
          <p className="mb-3 text-gray-600 dark:text-gray-300">Try asking:</p>
          <ul className="space-y-2 text-left">
            {exampleQuestions.map((question, index) => (
              <li 
                key={index}
                className="px-3 py-2 text-gray-700 dark:text-gray-300"
              >
                "{question}"
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen;