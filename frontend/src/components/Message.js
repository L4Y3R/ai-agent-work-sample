const Message = ({ message }) => {
  if (message.type === 'user') {
    return (
      <div className="flex justify-end mb-6">
        <div className="bg-blue-600 dark:bg-blue-500 text-white rounded-lg px-5 py-3 max-w-md lg:max-w-2xl xl:max-w-3xl">
          <p className="text-base leading-relaxed">{message.content}</p>
        </div>
      </div>
    );
  } else {
    return (
      <div className="flex justify-start mb-6">
        <div className={`rounded-lg px-5 py-4 max-w-2xl lg:max-w-4xl xl:max-w-5xl ${
          message.isError 
            ? 'bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700' 
            : 'bg-gray-100 dark:bg-gray-700'
        }`}>
          {message.contentType === 'text' ? (
            <p className="text-base text-gray-800 dark:text-gray-200 leading-relaxed">{message.content}</p>
          ) : message.contentType === 'dataframe' ? (
            <div>
              <p className="text-gray-600 dark:text-gray-300 mb-3 font-medium text-base">Answer:</p>
              <div className="overflow-x-auto">
                <table className="min-w-full border-collapse border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 rounded-md">
                  <thead>
                    <tr className="bg-gray-50 dark:bg-gray-700">
                      {message.tableData.columns.map((column, index) => (
                        <th 
                          key={index} 
                          className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-left font-semibold text-gray-700 dark:text-gray-300 text-sm"
                        >
                          {column}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {message.tableData.data.map((row, rowIndex) => (
                      <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-700'}>
                        {message.tableData.columns.map((column, colIndex) => (
                          <td 
                            key={colIndex} 
                            className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-900 dark:text-gray-200 text-sm"
                          >
                            {row[column]}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <pre className="whitespace-pre-wrap text-sm bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200 p-3 rounded overflow-x-auto">
              {message.content}
            </pre>
          )}
        </div>
      </div>
    );
  }
};

export default Message;