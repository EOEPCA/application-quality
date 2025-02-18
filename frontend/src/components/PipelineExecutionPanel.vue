<template>
    <v-navigation-drawer
        v-if="pipeline"
        v-model="isVisible"
        location="right"
        temporary
        :width="800"
      >
      <v-card>
        <v-card-title class="d-flex align-center">
          {{ pipeline.slug }}
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
  
          <v-form
            ref="form"
            v-model="isValid"
            @submit.prevent="submitExecution"
          >
            <!-- Input Parameters -->
            <v-card
              title="Application Repository"
              elevation="3"
              class="mb-4"
            >
            <v-card-text>
              <v-text-field
                v-model="localModelValue.repo_url"
                label="Git repository URL"
                required
                :rules="[v => !!v || 'The Git repository URL is required']"
              />
              <v-text-field
                v-model="localModelValue.repo_branch"
                label="Git branch (default: main)"
                :rules="[v => !!v || 'The Git branch is required']"
              />
            </v-card-text>

            </v-card>
            <template v-if="pipeline.user_params">
              <div v-for="tool_params, tool_id in pipeline.user_params" :key="tool_id">
              
                <v-card v-if="toolStore.hasToolUserParams(tool_id)"
                elevation="3"
              class="mb-4">
                  <v-card-title>
                    Analysis Tool: {{ toolStore.getToolName(tool_id) }}
                  </v-card-title>
                  <v-card-text>
                  <v-card
                    v-for="step_params, step_id in tool_params"
                    :key="step_id"
                    elevation="3"
                    class="mb-4"
                  >
                    <v-card-title>
                      Tool Step: {{ step_id }}
                    </v-card-title>
                    <v-card-text>
                    <div v-for="param, param_id in step_params" :key="param_id">
                <!-- CWL input types: string, boolean, int, long, float, double, and null -->
                <v-text-field
                    v-if="param.type == 'string'"
                    :key="param_id"
                    v-model="localModelValue['parameters'][tool_id][step_id][param_id]"
                    :label="param.label"
                    :hint="param.doc"
                    :placeholder="param.default"
                    :rules="[v => !!v || 'The value is required']"
                    persistent-hint
                />
                <v-checkbox
                    v-if="param.type == 'bool'"
                    :key="param_id"
                    v-model="localModelValue['parameters'][tool_id][step_id][param_id]"
                    :label="param.label"
                    :hint="param.doc"
                    :placeholder="param.default"
                    persistent-hint
                />
                <v-text-field
                    v-if="param.type == 'int'"
                    :key="param_id"
                    v-model="localModelValue['parameters'][tool_id][step_id][param_id]"
                    :label="param.label"
                    :hint="param.doc"
                    :placeholder="param.default"
                    :rules="[
                      v => !!v || 'Value is required',
                      v => !isNaN(parseInt(v)) && Number.isInteger(Number(v)) || 'Must be an integer'
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
import { pipelineService } from '@/services/pipelines'
import { useToolStore } from '@/stores/tools'

export default {
  name: 'PipelineExecutionPanel',

  data() {
    return {
      form: null,
      isValid: false,
      loading: false,
      error: false,
      panelVisible: false,
      localModelValue: Object.assign({}, this.modelValue),
    }
  },

  props: {
    // modelValue contains the execution payload
    modelValue: {
      type: Object,
      required: true
    },
    visible: {
      type: Boolean,
      default: false,
      required: true
    },
    pipeline: {
      // Invalid prop: type check failed for prop "pipeline". Expected Object, got Null
      // type: Object,
      required: true
    }
  },

  emits: ['update:visible', 'execution-cancelled', 'execution-submitted'],

  setup() {
    const toolStore = useToolStore()
    return {
      toolStore,
    }
  },

  mounted() {
    this.resetForm()
  },

  computed: {
    isVisible() {
      return this.visible;
    },
  },

  methods: {

    resetForm() {
      this.error = null
    },

    cancelExecution() {
      // console.log("Resetting and closing the pipeline execution panel")
      this.resetForm()
      this.$emit('execution-cancelled')
    },

    getPipelineUserParams() {
      const tools_params = {}
      for (var tool_id of this.pipeline["tools"]) {
        if (!this.toolStore.hasToolUserParams(tool_id)) {
          continue
        }
        const user_params = this.toolStore.getToolUserParams(tool_id)
        console.log("User params", user_params)
        tools_params[tool_id] = {}
        for (var param_id in user_params ) {
          tools_params[tool_id][param_id] = this.pipeline.user_params[tool_id][param_id].value
        }
      }
      console.log("Tools params", tools_params)
      return tools_params
    },

    async submitExecution() {
      if (!this.isValid) return
  
      this.loading = true
      this.error = null
  
      try {
        console.log("Pipeline to execute:", this.pipeline)
        const response = await pipelineService.executePipeline(
          this.pipeline.slug,
          this.localModelValue,
        )
        // The panel is closed when the parent component receives this signal
        this.$emit('execution-submitted', response)
      } catch (err) {
        this.error = err.message || 'Failed to submit execution'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>