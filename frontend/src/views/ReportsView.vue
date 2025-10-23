<template>
  <div>
    <h2 class="text-h4 mb-4">
      <v-icon icon="mdi-note-text-outline" size="x-small" class="mr-2" />
      Pipeline Execution Reports
    </h2>
    <report-list />
  </div>
</template>

<script>
import ReportList from '@/components/ReportList.vue';

export default {
  name: 'ReportsView',
  components: {
    ReportList,
  },
};
</script>
