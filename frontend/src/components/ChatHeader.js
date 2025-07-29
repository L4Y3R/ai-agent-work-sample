import ThemeToggle from "./ThemeToggle";

const ChatHeader = ({ messagesLength, onClearChat }) => {
  return (
    <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex justify-between items-center">
      <h1 className="text-2xl font-bold text-gray-800 dark:text-white">AI Agent Work Sample</h1>
      <div className="flex items-center gap-3">
        <ThemeToggle />
        {messagesLength > 0 && (
          <button
            onClick={onClearChat}
            className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 px-3 py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            Clear Chat
          </button>
        )}
      </div>
    </div>
  );
};

export default ChatHeader;