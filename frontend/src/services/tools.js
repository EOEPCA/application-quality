import axios from 'axios';

const API_URL = '/api';
const API_TIMEOUT = 5000;

const toolApi = axios.create({
  baseURL: API_URL + '/tools',
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

export const toolService = {
  async getTools() {
    try {
      const response = await toolApi.get('/');
      return response.data;
    } catch (error) {
      console.error('Error fetching analysis tools:', error);
      throw error;
    }
  },

  async getToolById(toolId) {
    try {
      const response = await toolApi.get(`/${toolId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching analysis tool ${toolId}:`, error);
      throw error;
    }
  },
};
