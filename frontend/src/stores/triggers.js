import { defineStore } from 'pinia';
import { triggerService } from '@/services/triggers';
import { usePipelineStore } from '@/stores/pipelines';

export const useTriggerStore = defineStore('trigger', {
  state: () => ({
    triggerTypes: [],
    triggers: [],
    triggerEvents: [],
    loadingTriggers: false,
    loadingExecutions: true,
    selectedTriggerId: null,
    listError: null,  // Use to display errors in the main page
    error: null,  // Used to display errors in the creation/editing panel
  }),

  actions: {
    async fetchTriggers() {
      this.loadingTriggers = true;
      this.listError = null;
      try {
        this.triggerTypes = await triggerService.getTriggerTypes();
        this.triggers = await triggerService.getTriggers();
      } catch (error) {
        const msg_prefix = 'Error fetching triggers: ';
        if (error.response?.data?.detail) {
          console.error(msg_prefix, error, error.response.data.detail);
          this.listError = msg_prefix + error.response.data.detail;
        } else {
          console.error(msg_prefix, error);
          this.listError = msg_prefix + error.message;
        }
      } finally {
        this.loadingTriggers = false;
      }
    },

    async fetchTriggerById(id) {
      this.loadingTriggers = true;
      this.listError = null;
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
          this.listError = msg_prefix + error.response.data.detail;
        } else {
          console.error(msg_prefix, error);
          this.listError = msg_prefix + error.message;
        }
      } finally {
        this.loadingTriggers = false;
      }
    },

    getTriggerById(id) {
      // console.debug('Triggers in store:', this.triggers);
      if (id == null || id == undefined) id = this.selectedTriggerId;
      if (id == null || id == undefined) {
        console.warn('Bad request: no trigger Id provided');
        return null;
      }
      var index = this.triggers.findIndex((p) => p.slug === id);
      if (index == -1) {
        // console.log("Trigger not found in store => Fetching it", id)
        this.fetchTriggerById(id);
      }
      index = this.triggers.findIndex((p) => p.slug === id);
      if (index !== -1) {
        return this.triggers[index];
      }
      return null;
    },

    async fetchTriggerEventById(id) {
      this.loadingTriggers = true;
      this.listError = null;
      try {
        const trigger_event = await triggerService.getTriggerEventById(id);
        const index = this.triggerEvents.findIndex((p) => p.id === id);
        if (index !== -1) {
          this.triggerEvents[index] = trigger_event;
        } else {
          this.triggerEvents.push(trigger_event);
        }
      } catch (error) {
        const msg_prefix = 'Error fetching trigger event: ';
        if (error.response?.data?.detail) {
          console.error(msg_prefix, error, error.response.data.detail);
          this.listError = msg_prefix + error.response.data.detail;
        } else {
          console.error(msg_prefix, error);
          this.listError = msg_prefix + error.message;
        }
      } finally {
        this.loadingTriggers = false;
      }
    },

    getTriggerEventById(id) {
      var index = this.triggerEvents.findIndex((p) => p.id === id);
      if (index == -1) {
        this.fetchTriggerEventById(id);
      }
      index = this.triggerEvents.findIndex((p) => p.id === id);
      if (index !== -1) {
        return this.triggerEvents[index];
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

    getTriggerTypeById(id) {
      var index = this.triggerTypes.findIndex((p) => p.slug === id);
      if (index == -1) {
        // console.log("Trigger type not found in store => Fetching it", id)
        // Note: there is not such "fetchTriggerTypeById(id)" function.
        // await this.fetchTriggerTypeById(id)
        //this.fetchTriggerTypeById(id);
        this.fetchTriggers();
      }
      index = this.triggerTypes.findIndex((p) => p.slug === id);
      if (index !== -1) {
        return this.triggerTypes[index];
      }
      return null;
    },

    async createTrigger(trigger) {
      console.log('Create trigger:', trigger.slug, trigger);
      this.loadingTriggers = true;
      this.error = null;
      try {
        const response = await triggerService.createTrigger(trigger);
        this.fetchTriggers();
        this.loadingTriggers = false;
        return response;
      } catch (error) {
        const msg_prefix = 'Error creating trigger ' + trigger.slug + ': ';
        if (error.response?.data?.detail) {
          console.error('1' + msg_prefix, error.response.data.detail);
          this.error = msg_prefix + error.response.data.detail;
        } else if (error.response?.data) {
          console.error('2' + msg_prefix, error.response.data);
          const text = Object.entries(error.response.data)
            .map(([key, messages]) => `- ${key}: ${messages.join(', ')}`)
            .join('\n');
          this.error = msg_prefix + '\n' + text;
        } else {
          console.error('3' + msg_prefix, error);
          this.error = msg_prefix + error.message;
        }
      } finally {
        this.loadingTriggers = false;
      }
    },

    async updateTrigger(trigger) {
      console.log('Update trigger:', trigger.slug, trigger);
      this.loadingTriggers = true;
      this.error = null;
      try {
        const response = await triggerService.updateTrigger(trigger);
        this.fetchTriggers();
        this.loadingTriggers = false;
        return response;
      } catch (error) {
        const msg_prefix = 'Error updating trigger ' + trigger.slug + ': ';
        if (error.response?.data?.detail) {
          console.error(msg_prefix, error, error.response.data.detail);
          this.error = msg_prefix + error.response.data.detail;
        } else if (error.response?.data) {
          console.error('2' + msg_prefix, error.response.data);
          const text = Object.entries(error.response.data)
            .map(([key, messages]) => `- ${key}: ${messages.join(', ')}`)
            .join('\n');
          this.error = msg_prefix + '\n' + text;
        } else {
          console.error(msg_prefix, error);
          this.error = msg_prefix + error.message;
        }
      } finally {
        this.loadingTriggers = false;
      }
    },

    async fetchPipelineExecutions(id) {
      // This is a 2-steps functions: 1/ fetch the events and 2/ fetch the pipeline runs
      this.loadingExecutions = true;
      this.listError = null;
      if (id == undefined) {
        id = this.selectedTriggerId;
      }
      try {
        const pipelineStore = usePipelineStore()
        pipelineStore.executions = await triggerService.getPipelineExecutions(id);
        // console.log('Executions:', this.executions);
      } catch (error) {
        const msg_prefix = 'Error fetching pipeline executions: ';
        if (error.response?.data?.detail) {
          console.error(msg_prefix, error, error.response.data.detail);
          this.listError = msg_prefix + error.response.data.detail;
        } else {
          console.error(msg_prefix, error);
          this.listError = msg_prefix + error.message;
        }
      } finally {
        this.loadingExecutions = false;
      }
    },

    async deleteTrigger(id) {
      console.log('Delete trigger', id);
      this.loadingTriggers = true;
      this.error = null;
      try {
        await triggerService.deleteTrigger(id);
      } catch (error) {
        const msg_prefix = 'Error deleting trigger ' + id + ': ';
        if (error.response?.data?.detail) {
          console.error(msg_prefix, error, error.response.data.detail);
          this.error = msg_prefix + error.response.data.detail;
        } else {
          console.error(msg_prefix, error);
          this.error = msg_prefix + error.message;
        }
      } finally {
        this.fetchTriggers();
        this.loadingTriggers = false;
      }
    },
  },
});
