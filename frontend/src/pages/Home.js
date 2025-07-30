import React, { useState } from 'react';
import { askQuestion } from '../api/agent';
import ChatHeader from '../components/ChatHeader';
import ChatInput from '../components/ChatInput';
import ChatArea from '../components/ChatArea';

const createMessage = (id, type, content, options = {}) => ({
  id,
  type,
  content,
  timestamp: new Date(),
  ...options,
});

const createAiMessage = (data) => {
  const baseMessage = {
    id: Date.now() + 1,
    type: 'ai',
    timestamp: new Date(),
  };

 if (!data.output.success) {
    const errorContent = data.output.data || 'An error occurred.';
    return {
      ...baseMessage,
      contentType: 'text',
      content: errorContent,
      ...(data.output.data ? {} : { isError: true }),
    };
  }

  const { type, data: outputData, columns } = data.output;

  switch (type) {
    case 'text':
      return {
        ...baseMessage,
        contentType: 'text',
        content: outputData,
      };
    case 'dataframe':
      return {
        ...baseMessage,
        contentType: 'dataframe',
        tableData: {
          data: outputData,
          columns,
        },
      };
    default:
      return {
        ...baseMessage,
        contentType: 'other',
        content: JSON.stringify(outputData, null, 2),
      };
  }
};

const Home = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim() || loading) return;

    const userMessage = createMessage(Date.now(), 'user', query);
    setMessages(prev => [...prev, userMessage]);

    const currentQuery = query;
    setQuery('');
    setLoading(true);

    try {
      const data = await askQuestion(currentQuery);
      const aiMessage = createAiMessage(data);
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = createMessage(
        Date.now() + 1,
        'ai',
        'Something went wrong. Please try again.',
        { contentType: 'text', isError: true }
      );
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="flex flex-col h-screen transition-colors duration-300 bg-gray-50 dark:bg-gray-900">
      <ChatHeader
        messagesLength={messages.length}
        onClearChat={clearChat}
      />
      <ChatArea
        messages={messages}
        loading={loading}
      />
      <ChatInput
        query={query}
        setQuery={setQuery}
        onSend={handleSearch}
        loading={loading}
      />
    </div>
  );
};

export default Home;