<template>
  <v-navigation-drawer
    v-if="visible && pipeline && modelValue && resetForm()"
    v-model="localVisible"
    location="right"
    temporary
    :width="800"
  >
    <v-card>
      <v-card-title class="d-flex align-center">
        Execute: {{ pipeline.name }}
        <v-spacer />
        <v-btn
          icon="mdi-close"
          variant="text"
          @click="cancelExecution"
          :disabled="loading"
        />
      </v-card-title>

      <v-card-text>
        <v-alert
          v-if="error"
          type="error"
          :text="error"
          closable
          class="mb-4"
        />

        <v-form ref="form" v-model="isValid" @submit.prevent="submitExecution">
          <!-- Input Parameters -->
          <template v-if="pipeline.init_params">
            <div
              v-for="(init_params, init_tool_id) in pipeline.init_params"
              :key="init_tool_id"
            >
              <tool-inputs-card
                v-if="toolStore.hasToolUserParams(init_tool_id)"
                :toolId="init_tool_id"
                :toolParams="pipeline.default_inputs[init_tool_id]"
                @update:toolParams="
                  (toolId, toolParams) => updateToolParams(toolId, toolParams)
                "
              >
              </tool-inputs-card>
            </div>
          </template>
          <!-- <v-card title="Application Repository" elevation="3" class="mb-4">
            <v-card-text>
              <v-text-field
                v-model="localModelValue.repo_url"
                label="Git repository URL"
                required
                :rules="[(v) => !!v || 'The Git repository URL is required']"
              />
              <v-text-field
                v-model="localModelValue.repo_branch"
                label="Git branch (default: main)"
                :rules="[(v) => !!v || 'The Git branch is required']"
              />
            </v-card-text>
          </v-card> -->
          <template v-if="pipeline.user_params">
            <div
              v-for="(tool_params, tool_id) in pipeline.user_params"
              :key="tool_id"
            >
              <tool-inputs-card
                v-if="toolStore.hasToolUserParams(tool_id)"
                :toolId="tool_id"
                :toolParams="pipeline.default_inputs[tool_id]"
                @update:toolParams="
                  (toolId, toolParams) => updateToolParams(toolId, toolParams)
                "
              >
              </tool-inputs-card>
            </div>
          </template>
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn
          color="grey"
          variant="text"
          @click="cancelExecution"
          :disabled="loading"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          @click="submitExecution"
          :loading="loading"
          :disabled="!isValid"
        >
          Execute
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-navigation-drawer>
</template>

<script>
import { usePipelineStore } from '@/stores/pipelines';
import { useToolStore } from '@/stores/tools';
import ToolInputsCard from './ToolInputsCard.vue';

export default {
  name: 'PipelineExecutionPanel',

  components: {
    ToolInputsCard,
  },

  data() {
    return {
      form: null,
      isValid: false,
      loading: false,
      error: false,
      panelVisible: false,
      // These are given values in resetForm()
      localModelValue: null,
      localPipeline: null,
      localVisible: false,
    };
  },

  props: {
    // modelValue contains the execution payload
    modelValue: {
      type: Object,
      required: true,
    },
    visible: {
      type: Boolean,
      default: false,
      required: true,
    },
    pipeline: {
      // Invalid prop: type check failed for prop "pipeline". Expected Object, got Null
      // type: Object,
      required: true,
    },
  },

  emits: ['update:visible', 'execution-cancelled', 'execution-submitted'],

  setup() {
    const toolStore = useToolStore();
    const pipelineStore = usePipelineStore();
    return {
      toolStore,
      pipelineStore,
    };
  },

  mounted() {
    this.resetForm();
  },

  methods: {
    resetForm() {
      // console.log('Re-initialising the pipeline execution form');
      this.error = null;
      this.localModelValue = this.modelValue
        ? JSON.parse(JSON.stringify(this.modelValue))
        : null;
      this.localPipeline = this.pipeline;
      this.localVisible = this.visible;
      return true;
    },

    cancelExecution() {
      // console.log("Resetting and closing the pipeline execution panel")
      this.resetForm();
      this.$emit('execution-cancelled');
    },

    updateToolParams(toolId, toolParams) {
      console.log(
        'Received "update:toolParams" event:',
        toolId,
        toolParams,
        this.localModelValue,
      );
      // Update the localModelValue
      this.localModelValue.parameters[toolId] = toolParams;
    },

    async submitExecution() {
      if (!this.isValid) return;
      this.loading = true;
      this.error = null;
      try {
        console.log(
          'Pipeline to execute:',
          this.pipeline,
          this.localModelValue,
        );
        var execParams = {};
        for (var toolId in this.localModelValue.parameters) {
          console.log('Tool:', toolId);
          execParams[toolId] = {};
          for (var stepId in this.localModelValue.parameters[toolId]) {
            console.debug('  Step:', stepId);
            execParams[toolId][stepId] = {};
            for (var paramId in this.localModelValue.parameters[toolId][
              stepId
            ]) {
              console.debug('    Param:', paramId);
              let value =
                this.localModelValue.parameters[toolId][stepId][paramId]
                  .default;
              if (stepId == 'clone' && paramId == 'repo_url') {
                // Special treatment for Git repo URLs
                console.debug('      Repo URL entered by the user:', value);
                // Prevent URLs ending with '/' or '.git'
                if (value) {
                  if (value.endsWith('/') || value.endsWith('.git')) {
                    value = value.replace(/\/$/, '');
                    value = value.replace(/\.git$/, '');
                    console.debug('      Repo URL replaced with:', value);
                  }
                }
              }
              execParams[toolId][stepId][paramId] = value;
              console.debug('    Value:', execParams[toolId][stepId][paramId]);
            }
          }
        }
        const response = await this.pipelineStore.executePipeline(
          this.pipeline,
          { parameters: execParams },
        );
        // The panel is closed when the parent component receives this signal
        this.$emit('execution-submitted', response);
      } catch (err) {
        this.error = err.message || 'Failed to submit execution';
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style>
.v-input__details {
  color: blue;
}

.v-checkbox .v-input__details {
  padding-top: 0;
  padding-inline: 16px;
  min-height: 0;
}
</style>
