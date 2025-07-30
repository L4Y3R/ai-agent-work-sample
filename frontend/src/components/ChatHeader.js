import React from 'react';
import ThemeToggle from './ThemeToggle';

const ChatHeader = ({ messagesLength = 0, onClearChat }) => {
  const handleClearChat = () => {
    if (window.confirm('Are you sure you want to clear all messages?')) {
      onClearChat();
    }
  };

  return (
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex justify-between items-center">
      <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
        AI Agent Work Sample
      </h1>
      
      <div className="flex items-center gap-3">
        <ThemeToggle />
        {messagesLength > 0 && (
          <button
            onClick={handleClearChat}
            className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 px-3 py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            aria-label="Clear chat messages"
          >
            Clear Chat
          </button>
        )}
      </div>
    </header>
  );
};

export default ChatHeader;