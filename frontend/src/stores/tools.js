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
        const index = this.tools.findIndex(p => p.id === id)
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

  }
})