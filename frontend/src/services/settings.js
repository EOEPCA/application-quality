import axios from 'axios';

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

const API_URL = '/api';
const API_TIMEOUT = 5000;

const settingsApi = axios.create({
  baseURL: API_URL + '/settings',
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
  withCredentials: true, // Important for CSRF to work with cookies
});

export const settingsService = {
  async getSettings() {
    try {
      const response = await settingsApi.get('/');
      return response.data;
    } catch (error) {
      console.error('Error during application settings request:', error);
      throw error;
    }
  },
};
