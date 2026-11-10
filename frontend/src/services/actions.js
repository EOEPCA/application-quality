import axios from 'axios';

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

const API_URL = '/api';
const API_TIMEOUT = 5000;

const actionsApi = axios.create({
  baseURL: API_URL + '/actions',
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
  withCredentials: true, // Important for CSRF to work with cookies
});

export const actionsService = {
  async setGitHubQualityCheckStatus({ repoUrl, refType, ref, status }) {
    try {
      console.log(`Set Quality Check status in GitHub: ${repoUrl} / ${refType} ${ref} = ${status}`);
      const response = await actionsApi.post('/github-quality-check-status',
        {
          'repoUrl': repoUrl,
          'refType': refType,
          'ref': ref,
          'status': status,
        }
      );
      return response.data;
    } catch (error) {
      console.error('Failed to set GitHub Quality Check status:', error);
      throw error;
    }
  },
};
