import { useState } from 'react';
import { askQuestion } from '../api/agent';
import ChatHeader from '../components/ChatHeader';
import ChatInput from '../components/ChatInput';
import ChatArea from '../components/ChatArea';

const Home = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim() || loading) return;
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: query,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentQuery = query;
    setQuery('');
    setLoading(true);
    
    try {
      const data = await askQuestion(currentQuery);
      
      let aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        timestamp: new Date()
      };

      if (data.output && data.output.success) {
        if (data.output.type === 'text') {
          aiMessage.contentType = 'text';
          aiMessage.content = data.output.data;
        } else if (data.output.type === 'dataframe') {
          aiMessage.contentType = 'dataframe';
          aiMessage.tableData = {
            data: data.output.data,
            columns: data.output.columns
          };
        } else {
          aiMessage.contentType = 'other';
          aiMessage.content = JSON.stringify(data.output.data, null, 2);
        }
      } else {
        aiMessage.contentType = 'text';
        aiMessage.content = 'No response received.';
      }

      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      console.error('Error:', err);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        contentType: 'text',
        content: 'Something went wrong. Please try again.',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    }
    
    setLoading(false);
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
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