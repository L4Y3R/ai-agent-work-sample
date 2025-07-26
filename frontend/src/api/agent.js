import axios from 'axios';

const API = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL,
});

export const askQuestion = async (query) => {
  try {
    const res = await API.post('/query', { query });
    return res.data;
  } catch (error) {
    console.error('Error asking question:', error);
    throw error;
  }
};
