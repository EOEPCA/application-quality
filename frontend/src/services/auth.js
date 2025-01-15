import axios from 'axios'

const OIDC_URL = '/oidc'
const API_TIMEOUT = 5000

const authApi = axios.create({
    baseURL: OIDC_URL,
    timeout: API_TIMEOUT,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  })

  export const authService = {
    async login() {
        window.location.href = OIDC_URL + '/authenticate/';
    },

    async getUserDetails() {
      try {
        const response = await authApi.get('/user-details/')
        return response.data
      } catch (error) {
        console.error('Error during user info request:', error)
        throw error
      }
    },

    async logout() {
      window.location.href = OIDC_URL + '/logout/';
    }
}
