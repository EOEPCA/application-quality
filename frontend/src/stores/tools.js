import { defineStore } from 'pinia'
import { toolService } from '@/services/tools'

export const useToolStore = defineStore('tool', {
  state: () => ({
    tools: [],
    executions: [],
    loading: false,
    error: null
  }),

  actions: {
    async fetchTools() {
      this.loading = true
      this.error = null
      try {
        this.tools = await toolService.getTools()
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async fetchToolById(id) {
      this.loading = true
      this.error = null
      try {
        const tool = await toolService.getToolById(id)
        const index = this.tools.findIndex(p => p.slug === id)
        if (index !== -1) {
          this.tools[index] = tool
        } else {
          this.tools.push(tool)
        }
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    // async getToolById(id) {
    getToolById(id) {
      var index = this.tools.findIndex(p => p.slug === id)
      if (index == -1) {
        // console.log("Tool not found in store => Fetching it", id)
        // await this.fetchToolById(id)
        this.fetchToolById(id)
      }
      index = this.tools.findIndex(p => p.slug === id)
      if (index !== -1) {
        return this.tools[index]
      }
      return null
    },

    getToolName(id) {
      const tool = this.getToolById(id)
      return tool ? tool.name : null
    },

    getToolUserParams(id) {
      const tool = this.getToolById(id)
      return tool ? tool.user_params : null
    },

    hasToolUserParams(id) {
      const tool = this.getToolById(id)
      return tool ? Object.keys(tool.user_params).length !== 0 : false
    }
  }
})