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

const triggerEventApi = axios.create({
  baseURL: API_URL + '/triggers/-/events',
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
      const response = await triggerApi.get(`/${triggerId}/`);
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
      console.error(`Error creating trigger ${trigger.slug}:`, error);
      throw error;
    }
  },

  async updateTrigger(trigger) {
    try {
      console.log('Update trigger data:', trigger);
      const response = await triggerApi.put(`/${trigger.slug}/`, trigger);
      return response.data;
    } catch (error) {
      console.error(
        // `Error updating trigger ${trigger.name} (Id: ${trigger.slug}):`,
        `Error updating trigger ${trigger.slug}:`,
        error,
      );
      throw error;
    }
  },

  async getTriggerEvents(trigger) {
    const triggerId = trigger?.slug || trigger;
    try {
      const response = await triggerApi.get(`/${triggerId}/events/`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching events for trigger ${triggerId}:`, error);
      throw error;
    }
  },

  async getTriggerEventById(eventId) {
    try {
      const response = await triggerEventApi.get(`/${eventId}/`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching trigger event with Id ${eventId}:`, error);
      throw error;
    }
  },

  async getPipelineExecutions(trigger) {
    const triggerId = trigger?.slug || trigger;
    try {
      const response = await triggerApi.get(`/${triggerId}/runs/`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching pipeline runs for trigger ${triggerId}:`, error);
      throw error;
    }
  },

  async deleteTrigger(trigger) {
    const triggerId = trigger?.slug || trigger;
    try {
      console.log('Delete trigger:', triggerId);
      // Note: In the backend, the trigger status is changed to "Deleted".
      // Otherwise all the associated events and runs are delected as well due to cascading.
      const response = await triggerApi.delete(`/${triggerId}/`);
      return response?.data;
    } catch (error) {
      console.error(`Error deleting trigger ${triggerId}:`, error);
      throw error;
    }
  },
};
