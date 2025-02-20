import { defineStore } from 'pinia';
import { authService } from '@/services/auth';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    details: null,
    username: null,
    firstname: null,
    lastname: null,
    isLoggedIn: false,
    isActive: false,
    isAdmin: false,
    isSuperuser: false,
    loading: false,
    error: null,
  }),

  actions: {
    async login() {
      await authService.login();
    },

    async logout() {
      await authService.logout();
      // The following is useless as we are navigating to the logout page
      // this.details = null
      // this.username = null
      // this.firstname = null
      // this.lastname = null
      // this.isLoggedIn = false
      // this.isAdmin = false
      // this.loading = false
      // this.error = null
    },

    async fetchUserDetails() {
      this.loading = true;
      this.error = null;
      try {
        const user = await authService.getUserDetails();
        this.details = user;
        this.username = user.username;
        this.firstname = user.first_name;
        this.lastname = user.last_name;
        this.isActive = user.is_active;
        this.isAdmin = user.is_admin;
        this.isSuperuser = user.is_superuser;
        this.isLoggedIn = true;
      } catch (error) {
        this.error = error.message;
        this.isLoggedIn = false;
      } finally {
        this.loading = false;
      }
    },
  },
});
