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
              <v-card
                v-if="toolStore.hasToolUserParams(init_tool_id)"
                elevation="3"
                class="mb-4"
              >
                <v-card-title>
                  Pipeline Initialisation:
                  {{ toolStore.getToolName(init_tool_id) }}
                </v-card-title>

                <v-card-text>
                  <v-card
                    v-for="(step_params, step_id) in init_params"
                    :key="step_id"
                    elevation="3"
                    class="mb-4"
                  >
                    <v-card-title v-if="step_params"
                      >Step: {{ step_id }}</v-card-title
                    >
                    <v-card-text>
                      <div
                        v-for="(param, param_id) in step_params"
                        :key="param_id"
                      >
                        <!-- CWL input types: string, boolean, int, long, float, double, and null -->
                        <v-text-field
                          v-if="param.type == 'string'"
                          :key="param_id"
                          v-model="
                            localModelValue['parameters'][init_tool_id][
                              step_id
                            ][param_id]
                          "
                          :label="param.label"
                          :hint="param.doc"
                          :placeholder="param.default"
                          :rules="[(v) => !!v || 'The value is required']"
                          persistent-hint
                        />
                        <v-checkbox
                          v-if="param.type.startsWith('bool')"
                          :key="param_id"
                          v-model="
                            localModelValue['parameters'][init_tool_id][
                              step_id
                            ][param_id]
                          "
                          :label="param.label"
                          :hint="param.doc"
                          :placeholder="param.default"
                          persistent-hint
                        />
                        <v-text-field
                          v-if="param.type == 'int'"
                          :key="param_id"
                          v-model="
                            localModelValue['parameters'][init_tool_id][
                              step_id
                            ][param_id]
                          "
                          :label="param.label"
                          :hint="param.doc"
                          :placeholder="param.default"
                          :rules="[
                            (v) => !!v || 'Value is required',
                            (v) =>
                              (!isNaN(parseInt(v)) &&
                                Number.isInteger(Number(v))) ||
                              'Must be an integer',
                          ]"
                          persistent-hint
                        />
                      </div>
                    </v-card-text>
                  </v-card>
                </v-card-text>
              </v-card>
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
              <v-card
                v-if="toolStore.hasToolUserParams(tool_id)"
                elevation="3"
                class="mb-4"
              >
                <v-card-title>
                  Analysis Tool: {{ toolStore.getToolName(tool_id) }}
                </v-card-title>
                <v-card-text>
                  <v-card
                    v-for="(step_params, step_id) in tool_params"
                    :key="step_id"
                    elevation="3"
                    class="mb-4"
                  >
                    <v-card-title v-if="step_params"
                      >Tool Step: {{ step_id }}</v-card-title
                    >
                    <v-card-text>
                      <div
                        v-for="(param, param_id) in step_params"
                        :key="param_id"
                      >
                        <!-- CWL input types: string, boolean, int, long, float, double, and null -->
                        <v-text-field
                          v-if="param.type == 'string'"
                          :key="param_id"
                          v-model="
                            localModelValue['parameters'][tool_id][step_id][
                              param_id
                            ]
                          "
                          :label="param.label"
                          :hint="param.doc"
                          :placeholder="param.default"
                          :rules="[(v) => !!v || 'The value is required']"
                          persistent-hint
                        />
                        <v-checkbox
                          v-if="param.type.startsWith('bool')"
                          :key="param_id"
                          v-model="
                            localModelValue['parameters'][tool_id][step_id][
                              param_id
                            ]
                          "
                          :label="param.label"
                          :hint="param.doc"
                          :placeholder="param.default"
                          persistent-hint
                        />
                        <v-text-field
                          v-if="param.type == 'int'"
                          :key="param_id"
                          v-model="
                            localModelValue['parameters'][tool_id][step_id][
                              param_id
                            ]
                          "
                          :label="param.label"
                          :hint="param.doc"
                          :placeholder="param.default"
                          :rules="[
                            (v) => !!v || 'Value is required',
                            (v) =>
                              (!isNaN(parseInt(v)) &&
                                Number.isInteger(Number(v))) ||
                              'Must be an integer',
                          ]"
                          persistent-hint
                        />
                      </div>
                    </v-card-text>
                  </v-card>
                </v-card-text>
              </v-card>
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
import { pipelineService } from '@/services/pipelines';
import { useToolStore } from '@/stores/tools';

export default {
  name: 'PipelineExecutionPanel',

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
    return {
      toolStore,
    };
  },

  mounted() {
    this.resetForm();
  },

  methods: {
    resetForm() {
      // console.log('Re-initialising the execution form');
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

    async submitExecution() {
      if (!this.isValid) return;
      this.loading = true;
      this.error = null;
      try {
        console.log('Pipeline to execute:', this.pipeline);
        const response = await pipelineService.executePipeline(
          this.pipeline.id,
          this.localModelValue,
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
