import React, { useRef, useEffect } from 'react';
import Message from './Message';
import WelcomeScreen from './WelcomeScreen';
import Loading from './Loading';

const ChatArea = ({ messages, loading }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto px-6 py-4">
      {messages.length === 0 ? (
        <WelcomeScreen />
      ) : (
        <div className="max-w-4xl mx-auto">
          {messages.map((message) => (
            <Message key={message.id} message={message} />
          ))}
          {loading && <Loading/>}
          <div ref={messagesEndRef} />
        </div>
      )}
    </div>
  );
};

export default ChatArea;