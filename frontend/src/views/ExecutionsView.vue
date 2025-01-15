<template>
  <div>
    <h2 class="text-h4 mb-4">
      <v-icon icon="mdi-monitor-eye" size="x-small" class="mr-2" />Analysis Pipeline Executions
    </h2>
    <pipeline-execution-list />
  </div>
</template>

<script>
import PipelineExecutionList from '@/components/PipelineExecutionList.vue'

export default {
  name: 'PipelineExecutionsView',
  components: {
    PipelineExecutionList
  }
}
</script>
