import React, { useState } from 'react';
import { askQuestion } from '../api/agent';

const Home = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
  if (!query.trim()) return;
  setLoading(true);
  setResponse('');
  try {
    const data = await askQuestion(query);
    console.log('Received data:', data);
    
    if (data.output && data.output.success && data.output.data) {
      setResponse(data.output.data);
    } else {
      setResponse('No response received.');
    }
  } catch (err) {
    console.error('Error:', err);
    setResponse('Something went wrong.');
  }
  setLoading(false);
};

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Air Quality AI Assistant</h1>

      <div className="flex gap-2 mb-4">
        <input
          type="text"
          className="border border-gray-300 rounded px-4 py-2 flex-grow"
          placeholder="Ask a question about the air quality data..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          onClick={handleSearch}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {loading ? 'Thinking...' : 'Ask'}
        </button>
      </div>

      {response && (
        <div className="bg-white rounded shadow p-4 border border-gray-200">
          <h2 className="font-semibold mb-2">Response:</h2>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
};

export default Home;
