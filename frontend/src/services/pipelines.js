import axios from 'axios';

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

const API_URL = '/api';
const API_TIMEOUT = 5000;

const pipelineApi = axios.create({
  baseURL: API_URL + '/pipelines',
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
  withCredentials: true, // Important for CSRF to work with cookies
});

export const pipelineService = {
  async getPipelines() {
    try {
      const response = await pipelineApi.get('/');
      return response.data;
    } catch (error) {
      if (error.response?.data?.detail) {
        console.error(
          'Error fetching pipelines:',
          error,
          error.response.data.detail,
        );
      } else {
        console.error('Error fetching pipelines:', error);
      }
      throw error;
    }
  },

  async getPipelineById(pipelineId) {
    try {
      const response = await pipelineApi.get(`/${pipelineId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching pipeline ${pipelineId}:`, error);
      throw error;
    }
  },

  async createPipeline(pipeline) {
    try {
      console.log('Create pipeline data:', pipeline);
      const response = await pipelineApi.post(`/`, pipeline);
      return response.data;
    } catch (error) {
      console.error(`Error creating pipeline ${pipeline.slug}:`, error);
      throw error;
    }
  },

  async updatePipeline(pipeline) {
    try {
      console.log('Update pipeline data:', pipeline);
      const response = await pipelineApi.put(`/${pipeline.slug}`, pipeline);
      return response.data;
    } catch (error) {
      console.error(`Error updating pipeline ${pipeline.slug}:`, error);
      throw error;
    }
  },

  async executePipeline(pipelineId, inputs) {
    try {
      console.log('Executing pipeline ', pipelineId, 'with inputs:', inputs);
      const response = await pipelineApi.post(`/${pipelineId}/runs/`, inputs);
      return response.data;
    } catch (error) {
      console.error('Error creating execution:', error);
      throw new Error(
        error.response?.data?.message || 'Failed to create execution',
      );
    }
  },

  async getPipelineExecutions(pipelineId) {
    try {
      if (pipelineId === undefined) {
        pipelineId = '_'; // Meaning "all pipelines"
      }
      const response = await pipelineApi.get(`/${pipelineId}/runs/`);
      return response.data;
    } catch (error) {
      console.error(
        `Error fetching executions of pipeline ${pipelineId}:`,
        error,
      );
      throw error;
    }
  },

  async getPipelineExecutionById(pipelineId, runId) {
    try {
      const response = await pipelineApi.get(`/${pipelineId}/runs/${runId}`);
      return response.data;
    } catch (error) {
      console.error(
        `Error fetching pipeline execution ${pipelineId} ${runId}:`,
        error,
      );
      throw error;
    }
  },

  async getPipelineExecutionReports(pipelineId, runId) {
    try {
      const response = await pipelineApi.get(
        `/${pipelineId}/runs/${runId}/jobreports/`,
      );
      return response.data;
    } catch (error) {
      console.error(
        `Error fetching pipeline execution reports for ${pipelineId} ${runId}:`,
        error,
      );
      throw error;
    }
  },

  async deletePipeline(pipelineId) {
    try {
      console.log('Delete pipeline:', pipelineId);
      const response = await pipelineApi.delete(pipelineId);
      return response.data;
    } catch (error) {
      console.error(`Error deleting pipeline ${pipelineId}:`, error);
      throw error;
    }
  },
};
