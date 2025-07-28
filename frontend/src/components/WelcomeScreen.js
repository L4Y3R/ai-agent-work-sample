import React from 'react';

const WelcomeScreen = () => {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center text-gray-500">
        <h2>Ask me anything about your air quality data!</h2>
        <div className="mt-4 text-sm">
          <p className="mb-1">Try asking:</p>
          <ul className="space-y-1">
            <li>"What's the average CO2 level in Room 1?"</li>
            <li>"Show me temperature data by room"</li>
            <li>"Which room has the highest humidity?"</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen;