<template>
  <div>
    <h2 class="text-h4 mb-4">
      <v-icon icon="mdi-tools" size="x-small" class="mr-2" />
      Application Quality Analysis Tools
    </h2>
    <tool-list />
  </div>
</template>

<script>
import ToolList from '@/components/ToolList.vue';

export default {
  name: 'ToolsView',
  components: {
    ToolList,
  },
};
</script>
