import React, { useRef, useEffect, useMemo } from 'react';
import Message from './Message';
import WelcomeScreen from './WelcomeScreen';
import Loading from './Loading';

const ChatArea = ({ messages = [], loading = false }) => {
  const messagesEndRef = useRef(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (messages.length > 0) {
      scrollToBottom();
    }
  }, [messages.length]);

  const hasMessages = useMemo(() => messages.length > 0, [messages.length]);

  if (!hasMessages) {
    return (
      <div className="flex-1 overflow-y-auto px-6 py-4">
        <WelcomeScreen />
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-6 py-4">
      <div className="max-w-4xl mx-auto">
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
        {loading && <Loading />}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatArea;