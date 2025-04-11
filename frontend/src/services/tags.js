import axios from 'axios';

const API_URL = '/api';
const API_TIMEOUT = 5000;

const tagApi = axios.create({
  baseURL: API_URL + '/tags',
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

export const tagService = {
  async getTags() {
    try {
      const response = await tagApi.get('/');
      return response.data;
    } catch (error) {
      console.error('Error fetching tags definitions:', error);
      throw error;
    }
  },

  async getTagById(tagId) {
    try {
      const response = await tagApi.get(`/${tagId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching definition of tag ${tagId}:`, error);
      throw error;
    }
  },
};
