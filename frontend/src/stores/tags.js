import { defineStore } from 'pinia';
import { tagService } from '@/services/tags';

export const useTagStore = defineStore('tag', {
  state: () => ({
    tags: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetchTags() {
      this.loading = true;
      this.error = null;
      try {
        this.tags = await tagService.getTags();
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },

    async fetchTagById(id) {
      this.loading = true;
      this.error = null;
      try {
        const tag = await tagService.getTagById(id);
        const index = this.tags.findIndex((p) => p.slug === id);
        if (index !== -1) {
          this.tags[index] = tag;
        } else {
          this.tags.push(tag);
        }
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },

    // async getTagById(id) {
    getTagById(id) {
      var index = this.tags.findIndex((p) => p.slug === id);
      if (index == -1) {
        // console.log("Tag not found in store => Fetching it", id)
        // await this.fetchTagById(id)
        this.fetchTagById(id);
      }
      index = this.tags.findIndex((p) => p.slug === id);
      if (index !== -1) {
        return this.tags[index];
      }
      return null;
    },

    getTagName(id) {
      const tag = this.getTagById(id);
      return tag ? tag.name : null;
    },
  },
});
