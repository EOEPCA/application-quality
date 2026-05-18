import axios from 'axios';

const API_URL = '/api';
const API_TIMEOUT = 5000;

const triggerTypeApi = axios.create({
  baseURL: API_URL + '/triggertypes',
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

const triggerApi = axios.create({
  baseURL: API_URL + '/triggers',
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

export const triggerService = {

  async getTriggerTypes() {
    try {
      const response = await triggerTypeApi.get('/');
      return response.data;
    } catch (error) {
      console.error('Error fetching trigger types:', error);
      throw error;
    }
  },

  async getTriggers() {
    try {
      const response = await triggerApi.get('/');
      return response.data;
    } catch (error) {
      console.error('Error fetching triggers:', error);
      throw error;
    }
  },

  async getTriggerById(triggerId) {
    try {
      const response = await triggerApi.get(`/${triggerId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching trigger ${triggerId}:`, error);
      throw error;
    }
  },

  async createTrigger(trigger) {
    try {
      console.log('Create trigger data:', trigger);
      const response = await triggerApi.post(`/`, trigger);
      return response.data;
    } catch (error) {
      console.error(`Error creating trigger ${trigger.name}:`, error);
      throw error;
    }
  },

  async updateTrigger(trigger) {
    try {
      console.log('Update trigger data:', trigger);
      const response = await triggerApi.put(`/${trigger.id}/`, trigger);
      return response.data;
    } catch (error) {
      console.error(
        `Error updating trigger ${trigger.name} (Id: ${trigger.id}):`,
        error,
      );
      throw error;
    }
  },

  async deleteTrigger(trigger) {
    // TODO: Change the trigger status to "Deleted"
  },
};
