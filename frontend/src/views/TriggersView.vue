<template>
  <div>
    <h2 class="text-h4 mb-4">
      <v-icon icon="mdi-animation-play" size="x-small" class="mr-2" />
      Triggers
    </h2>
    <trigger-list />
  </div>
</template>

<script>
import TriggerList from '@/components/TriggerList.vue';

export default {
  name: 'TriggersView',
  components: {
    TriggerList,
  },
};
</script>
