import { defineStore } from 'pinia';
import { toolService } from '@/services/tools';
import { tagService } from '@/services/tags';

export const useToolStore = defineStore('tool', {
  state: () => ({
    tools: [],
    tags: [],
    executions: [],
    loading: false,
    error: null,
  }),

  actions: {
    updateToolsTags(tools, tags) {
      // Replace tag IDs with tag names in the tools array
      this.tools = tools.map((tool) => {
        if (tool.tags && Array.isArray(tool.tags)) {
          // Create a new tool object with updated tags
          return {
            ...tool,
            tags: tool.tags.map((tagId) => {
              // Find the tag object that matches the tagId
              const tag = tags.find((t) => t.id === tagId || t._id === tagId);
              // Return the tag name if found, otherwise return the original tagId
              return tag ? tag.name : tagId;
            }),
          };
        }
        // If tool doesn't have tags, return it unchanged
        return tool;
      });
    },

    async fetchTools() {
      this.loading = true;
      this.error = null;
      try {
        this.tools = await toolService.getTools();
        this.tags = await tagService.getTags();
        this.updateToolsTags(this.tools, this.tags);
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },

    async fetchToolById(id) {
      this.loading = true;
      this.error = null;
      try {
        const tool = await toolService.getToolById(id);
        const index = this.tools.findIndex((p) => p.slug === id);
        if (index !== -1) {
          this.tools[index] = tool;
        } else {
          this.tools.push(tool);
        }
        this.updateToolsTags(this.tools, this.tags);
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },

    // async getToolById(id) {
    getToolById(id) {
      var index = this.tools.findIndex((p) => p.slug === id);
      if (index == -1) {
        // console.log("Tool not found in store => Fetching it", id)
        // await this.fetchToolById(id)
        this.fetchToolById(id);
      }
      index = this.tools.findIndex((p) => p.slug === id);
      if (index !== -1) {
        return this.tools[index];
      }
      return null;
    },

    getToolName(id) {
      const tool = this.getToolById(id);
      return tool ? tool.name : null;
    },

    getToolUserParams(id) {
      const tool = this.getToolById(id);
      return tool ? tool.user_params : null;
    },

    hasToolUserParams(id) {
      const tool = this.getToolById(id);
      return tool ? Object.keys(tool.user_params).length !== 0 : false;
    },

    getToolTags(id) {
      const tool = this.getToolById(id);
      return tool ? tool.tags : null;
    },
  },
});
