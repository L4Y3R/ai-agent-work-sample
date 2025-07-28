
const ChatHeader = ({ messagesLength, onClearChat }) => {
  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
      <h1 className="text-2xl font-bold text-gray-800">AI Agent Work Sample</h1>
      {messagesLength > 0 && (
        <button
          onClick={onClearChat}
          className="text-sm text-gray-500 hover:text-gray-700 px-3 py-1 rounded hover:bg-gray-100"
        >
          Clear Chat
        </button>
      )}
    </div>
  );
};

export default ChatHeader;