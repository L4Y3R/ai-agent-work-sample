import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL,
  timeout: 20000,
});

export const askQuestion = async (query) => {
  if (!query?.trim()) {
    throw new Error('Query is required');
  }

  try {
    const response = await apiClient.post('/query', { query });
    return response.data;
  } catch (error) {
    const message = error.response?.data?.message || 'Failed to process question';
    console.error('API Error:', message);
    throw new Error(message);
  }
};