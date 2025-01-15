<template>
  <div>
    <h2 class="text-h4 mb-4">
      <v-icon icon="mdi-pipe" size="x-small" class="mr-2" />Application Quality Pipelines
    </h2>
    <pipeline-list />
  </div>
</template>

<script>
import PipelineList from '@/components/PipelineList.vue'

export default {
  name: 'PipelinesView',
  components: {
    PipelineList
  }
}
</script>