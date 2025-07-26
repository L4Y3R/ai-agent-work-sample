import React, { useState } from 'react';
import { askQuestion } from '../api/agent';

const Home = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [responseType, setResponseType] = useState('text');
  const [tableData, setTableData] = useState({ data: [], columns: [] });
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    console.log('API Base URL:', process.env.REACT_APP_API_BASE_URL);
    if (!query.trim()) return;
    
    setLoading(true);
    setResponse('');
    setResponseType('text');
    setTableData({ data: [], columns: [] });
    
    try {
      const data = await askQuestion(query);
      console.log('Received data:', data);
      
      if (data.output && data.output.success) {
        if (data.output.type === 'text') {
          setResponse(data.output.data);
          setResponseType('text');
        } else if (data.output.type === 'dataframe') {
          setTableData({
            data: data.output.data,
            columns: data.output.columns
          });
          setResponseType('dataframe');
        } else {
          setResponse(JSON.stringify(data.output.data, null, 2));
          setResponseType('other');
        }
      } else {
        setResponse('No response received.');
        setResponseType('text');
      }
    } catch (err) {
      console.error('Error:', err);
      setResponse('Something went wrong.');
      setResponseType('text');
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
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button
          onClick={handleSearch}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          disabled={loading}
        >
          {loading ? 'Thinking...' : 'Ask'}
        </button>
      </div>
      
      {(response || tableData.data.length > 0) && (
        <div className="bg-white rounded shadow p-4 border border-gray-200">
          <h2 className="font-semibold mb-2">Response:</h2>
          {responseType === 'text' ? (
            <p>{response}</p>
          ) : responseType === 'dataframe' ? (
            <div className="overflow-x-auto">
              <table className="min-w-full border-collapse border border-gray-300">
                <thead>
                  <tr className="bg-gray-50">
                    {tableData.columns.map((column, index) => (
                      <th 
                        key={index} 
                        className="border border-gray-300 px-4 py-2 text-left font-semibold text-gray-700"
                      >
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {tableData.data.map((row, rowIndex) => (
                    <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      {tableData.columns.map((column, colIndex) => (
                        <td 
                          key={colIndex} 
                          className="border border-gray-300 px-4 py-2 text-gray-900"
                        >
                          {row[column]}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <pre className="whitespace-pre-wrap text-sm bg-gray-100 p-3 rounded overflow-x-auto">
              {response}
            </pre>
          )}
        </div>
      )}
    </div>
  );
};

export default Home;