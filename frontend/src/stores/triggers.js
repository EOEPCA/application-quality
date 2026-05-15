import { defineStore } from 'pinia';
import { triggerService } from '@/services/triggers';

export const useTriggerStore = defineStore('trigger', {
  state: () => ({
    triggerTypes: [],
    triggers: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetchTriggers() {
      this.loading = true;
      this.error = null;
      try {
        this.triggerTypes = await triggerService.getTriggerTypes();
        this.triggers = await triggerService.getTriggers();
      } catch (error) {
        const msg_prefix = 'Error fetching triggers: ';
        if (error.response?.data?.detail) {
          console.error(msg_prefix, error, error.response.data.detail);
          this.error = msg_prefix + error.response.data.detail;
        } else {
          console.error(msg_prefix, error);
          this.error = msg_prefix + error.message;
        }
      } finally {
        this.loading = false;
      }
    },

    async fetchTriggerById(id) {
      this.loading = true;
      this.error = null;
      try {
        const trigger = await triggerService.getTriggerById(id);
        const index = this.triggers.findIndex((p) => p.slug === id);
        if (index !== -1) {
          this.triggers[index] = trigger;
        } else {
          this.triggers.push(trigger);
        }
      } catch (error) {
        const msg_prefix = 'Error fetching trigger: ';
        if (error.response?.data?.detail) {
          console.error(msg_prefix, error, error.response.data.detail);
          this.error = msg_prefix + error.response.data.detail;
        } else {
          console.error(msg_prefix, error);
          this.error = msg_prefix + error.message;
        }
      } finally {
        this.loading = false;
      }
    },

    // async getTriggerById(id) {
    getTriggerById(id) {
      var index = this.triggers.findIndex((p) => p.slug === id);
      if (index == -1) {
        // console.log("Trigger not found in store => Fetching it", id)
        // await this.fetchTriggerById(id)
        this.fetchTriggerById(id);
      }
      index = this.triggers.findIndex((p) => p.slug === id);
      if (index !== -1) {
        return this.triggers[index];
      }
      return null;
    },

    getTriggerName(id) {
      const trigger = this.getTriggerById(id);
      return trigger ? trigger.name : null;
    },

    getTriggerUserParams(id) {
      const trigger = this.getTriggerById(id);
      return trigger ? trigger.user_params : null;
    },

    hasTriggerUserParams(id) {
      const trigger = this.getTriggerById(id);
      return trigger ? Object.keys(trigger.user_params).length !== 0 : false;
    },
  },
});
