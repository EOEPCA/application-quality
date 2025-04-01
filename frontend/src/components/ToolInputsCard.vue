<template>
  <div>
    <v-card
      v-if="localToolId && toolStore.hasToolUserParams(localToolId)"
      elevation="3"
      class="mb-4"
      color="info"
      variant="outlined"
    >
      <!-- indigo / tonal -->
      <v-card-title v-if="toolStore.isInitTool(localToolId)">
        Pipeline Initialisation:
        {{ toolStore.getToolName(localToolId) }}
      </v-card-title>
      <v-card-title v-else>
        Analysis Tool:
        {{ toolStore.getToolName(localToolId) }}
      </v-card-title>

      <v-card-text
        v-for="(step_params, step_id) in localToolParams"
        :key="step_id"
      >
        <v-card
          elevation="3"
          class="mb-2"
          color="black lighten-4"
          variant="tonal"
        >
          <v-card-title v-if="step_params">Step: {{ step_id }}</v-card-title>
          <v-card-text v-for="(param, param_id) in step_params" :key="param_id">
            <!-- CWL input types: string, boolean, int, long, float, double, and null -->
            <v-text-field
              v-if="param.type == 'string'"
              :key="param_id"
              v-model="localToolParams[step_id][param_id].default"
              :label="param.label"
              :hint="param.doc"
              :placeholder="param.default"
              :rules="[(v) => !!v || 'The value is required']"
              persistent-hint
            />
            <v-checkbox
              v-if="param.type.startsWith('bool')"
              :key="param_id"
              v-model="localToolParams[step_id][param_id].default"
              :label="param.label"
              :hint="param.doc"
              :placeholder="param.default"
              persistent-hint
            />
            <v-text-field
              v-if="param.type == 'int'"
              :key="param_id"
              v-model="localToolParams[step_id][param_id].default"
              :label="param.label"
              :hint="param.doc"
              :placeholder="param.default"
              :rules="[
                (v) => !!v || 'Value is required',
                (v) =>
                  (!isNaN(parseInt(v)) && Number.isInteger(Number(v))) ||
                  'Must be an integer',
              ]"
              persistent-hint
            />
          </v-card-text>
        </v-card>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { useToolStore } from '@/stores/tools';

export default {
  name: 'ToolInputsCard',
  emits: ['update:toolParams'],

  data() {
    return {
      localToolId: null,
      localToolParams: {},
    };
  },

  setup() {
    const toolStore = useToolStore();
    return { toolStore };
  },

  mounted() {
    this.localToolId = this.toolId;
    if (this.defaultInputs !== undefined) {
      this.localToolParams = this.defaultInputs;
    } else {
      this.localToolParams = this.toolParams;
    }
    // this.localDefaultInputs = this.defaultInputs;
    console.log('Tool Id, params, default:', this.toolId, this.toolParams, this.defaultInputs);
  },

  // Properties provided by the parent component
  props: {
    toolId: {
      type: String,
      required: true,
    },
    toolParams: {
      type: Object,
      required: true,
    },
    defaultInputs: {
      type: Object,
      required: false,
    },
  },

  watch: {
    localToolParams: {
      handler() {
        console.log('Tool new params:', this.localToolId, this.localToolParams);
        this.$emit('update:toolParams', this.localToolId, this.localToolParams);
      },
      deep: true,
    },
  },
};
</script>

<style scoped>
.tool-json {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  font-family: monospace;
}

.v-table {
  margin-top: 1rem;
}

.nowrap {
  white-space: nowrap;
}

.reset-colors {
  /* Reset to specific colors */
  background-color: white !important;
  color: rgba(255, 255, 255, 1) !important;
}
</style>
