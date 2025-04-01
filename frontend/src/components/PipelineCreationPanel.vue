<!-- eslint-disable vue/no-mutating-props -->
<template>
  <v-navigation-drawer
    v-if="localModelValue"
    v-model="isVisible"
    location="right"
    temporary
    :width="800"
  >
    <v-card>
      <v-card-title class="d-flex align-center">
        <span v-if="modelValue.isCreation"
          >New pipeline: {{ pipelineName }}</span
        >
        <span v-else>Edit pipeline: {{ pipelineName }}</span>
        <v-spacer />
        <v-btn
          icon="mdi-close"
          variant="text"
          @click="cancel"
          :disabled="isBusy"
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

        <v-form ref="form" v-model="isValid" @submit.prevent="submit">
          <!-- Input Parameters -->
          <v-card title="Properties" elevation="3" class="mb-4">
            <v-card-text>
              <v-text-field
                v-model="localModelValue.name"
                label="Name"
                required
                :disabled="!modelValue.isCreation"
                v-on:input="onPipelineNameChange"
                :rules="[(v) => !!v || 'The name may not be empty']"
              />
              <v-text-field
                v-model="localModelValue.description"
                label="Description (optional)"
                required
                :__rules="[(v) => !!v || 'The Git repository URL is required']"
              />
              <v-text-field
                v-model="localModelValue.version"
                label="Version (free text)"
                required
                :rules="[(v) => !!v || 'The version may not be empty']"
              />
              <v-combobox
                v-model="localModelValue.selectedTools"
                :items="modelValue.availableTools"
                label="Selected analysis tools"
                multiple
                chips
                closable-chips
                required
                :rules="[
                  (v) =>
                    (v && v.length > 0) || 'At least one tool must be selected',
                ]"
              >
                <!-- Template for the items in the dropdown -->
                <template v-slot:item="{ props, item }">
                  <v-list-item
                    v-bind="props"
                    :title="item.raw.name"
                    class="d-flex flex-row align-stretch font-weight-bold"
                  >
                    <template v-slot:prepend>
                      <v-icon
                        :icon="item.raw.icon || 'mdi-tools'"
                        class="mr-2"
                      />
                    </template>
                    <!-- eslint-disable vue/no-v-text-v-html-on-component -->
                    <v-list-item-subtitle
                      class="text-wrap font-weight-light"
                      v-html="item.raw.description"
                    />
                  </v-list-item>
                </template>

                <!-- Template for the selected chips -->
                <template v-slot:chip="{ props, item }">
                  <v-chip
                    v-bind="props"
                    :prepend-icon="item.icon || 'mdi-tools'"
                  >
                    {{ item.raw.name || item }}
                  </v-chip>
                </template>
              </v-combobox>
            </v-card-text>
          </v-card>

          <!-- <v-card title="Default values" elevation="3" class="mb-4" v-if="true">
            <v-card-text>
              <v-text-field
                v-model="modelValue.repo_url"
                label="Git repository URL"
                required
                :rules="[(v) => !!v || 'The Git repository URL is required']"
              />
              <v-text-field
                v-model="modelValue.repo_branch"
                label="Git branch (default: main)"
                :rules="[(v) => !!v || 'The Git branch is required']"
              />
            </v-card-text>
          </v-card> -->

          <template v-if="selectedTools.init_params">
            <div
              v-for="(init_params, init_tool_id) in selectedTools.init_params"
              :key="init_tool_id"
            >
              <tool-inputs-card
                v-if="toolStore.hasToolUserParams(init_tool_id)"
                :toolId="init_tool_id"
                :toolParams="selectedTools.init_params[init_tool_id]"
                :defaultInputs="defaultInputs(init_tool_id)"
                @update:toolParams="
                  (toolId, toolParams) => updateToolParams(toolId, toolParams)
                "
              >
              </tool-inputs-card>
            </div>
          </template>

          <template v-if="selectedTools.user_params">
            <div
              v-for="(tool_params, tool_id) in selectedTools.user_params"
              :key="tool_id"
            >
              <tool-inputs-card
                v-if="toolStore.hasToolUserParams(tool_id)"
                :toolId="tool_id"
                :toolParams="selectedTools.user_params[tool_id]"
                :defaultInputs="defaultInputs(tool_id)"
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
        <v-btn color="grey" variant="text" @click="cancel" :disabled="isBusy">
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          @click="submit"
          :loading="isBusy"
          :disabled="!isValid"
        >
          {{ modelValue.creation ? 'Create' : 'Submit' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-navigation-drawer>
</template>

<script>
// import { ref, computed } from 'vue'
import { pipelineService } from '@/services/pipelines';
import { useToolStore } from '@/stores/tools';
import ToolInputsCard from './ToolInputsCard.vue';

export default {
  name: 'PipelineCreationPanel',

  components: {
    ToolInputsCard,
  },

  data() {
    return {
      pipelineName: '',
      form: null,
      isValid: false,
      isBusy: false,
      error: false,
      panelVisible: false,
      selectedTools: {
        init_params: {},
        user_params: {},
      },
      // These are given values in resetForm()
      localModelValue: null,
      localPipeline: null,
      localVisible: false,
    };
  },

  props: {
    // modelValue contains the creation data
    modelValue: {
      type: Object,
      // default: () => ({
      //   availableTools: [],
      //   selectedTools: null,
      //   defaultInputs: {},
      // }),
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
      default: null,
      required: false,
    },
  },

  emits: [
    'update:visible',
    'creation-cancelled',
    'creation-submitted',
    'edition-cancelled',
    'edition-submitted',
  ],

  //setup(props, { emit }) {
  setup() {
    const toolStore = useToolStore();
    return {
      toolStore,
    };
  },

  mounted() {
    this.resetForm();
  },

  computed: {
    isVisible() {
      return this.visible;
    },
  },

  watch: {
    visible: {
      handler() {
        console.log('Creation/edition panel becomes visible');
        this.resetForm();  // updateCreationPanel();
      }
    },
    localModelValue: {
      handler() {
        console.log('Selected tools:', this.localModelValue.selectedTools);
        console.log('Default inputs:', this.localModelValue.defaultInputs);
        this.updateCreationPanel();
        //this.$emit('update:toolParams', this.localToolId, this.localToolParams);
      },
      deep: true,
    },
  },

  methods: {
    resetForm() {
      // console.log('Re-initialising the pipeline creation form');
      this.error = null;
      this.localModelValue = this.modelValue
        ? JSON.parse(JSON.stringify(this.modelValue))
        : null;
      if (this.localModelValue.selectedTools === undefined) {
        this.localModelValue.selectedTools = [];
      }
      this.localPipeline = this.pipeline;
      this.localVisible = this.visible;
      this.updateCreationPanel();
      return true;
    },

    onPipelineNameChange() {
      this.pipelineName = this.localModelValue.name;
    },

    cancel() {
      // console.log("Resetting and closing the pipeline creation/edition panel")
      this.resetForm();
      this.modelValue.isCreation
        ? this.$emit('creation-cancelled')
        : this.$emit('edition-cancelled');
    },

    // TODO: After the tools have been selected, the user must be able
    // to enter default values for the user parameters

    // getPipelineUserParams() {
    //   const tools_params = {}
    //   for (var tool_id of this.pipeline["tools"]) {
    //     if (!this.toolStore.hasToolUserParams(tool_id)) {
    //       continue
    //     }
    //     const user_params = this.toolStore.getToolUserParams(tool_id)
    //     console.log("User params", user_params)
    //     tools_params[tool_id] = {}
    //     for (var param_id in user_params ) {
    //       tools_params[tool_id][param_id] = this.pipeline.user_params[tool_id][param_id].value
    //     }
    //   }
    //   console.log("Tools params", tools_params)
    //   return tools_params
    // },

    // After the tools have been selected, the user must be able
    // to enter or edit the default values for the user parameters
    updateCreationPanel() {
      this.selectedTools.init_params = {};
      this.selectedTools.user_params = {};
      console.log('Selected tools:', this.localModelValue.selectedTools);
      console.log('Default inputs:', this.localModelValue.defaultInputs);
      for (var tool of this.localModelValue.selectedTools) {
        // const tool = this.toolStore.getToolById(tool_id);
        if (this.toolStore.isInitTool(tool.slug)) {
          this.selectedTools.init_params[tool.slug] = tool
            ? tool['user_params']
            : null;
        } else {
          this.selectedTools.user_params[tool.slug] = tool
            ? tool['user_params']
            : null;
        }
      }
    },

    updateToolParams(toolId, toolParams) {
      console.log(
        'Received "update:toolParams" event:',
        toolId,
        toolParams,
        this.selectedTools,
      );
      // Update the defaultToolsValues
      if (this.toolStore.isInitTool(toolId)) {
        this.selectedTools.init_params[toolId] = toolParams;
      } else {
        this.selectedTools.user_params[toolId] = toolParams;
      }
    },

    defaultInputs(toolId) {
      if (this.localModelValue.defaultInputs !== undefined) {
        return this.localModelValue.defaultInputs[toolId];
      } else if (this.selectedTools.init_params[toolId]) {
        return this.selectedTools.init_params[toolId]
      } else {
        this.selectedTools.user_params[toolId]
      }
    },
    
    async submitCreation() {
      if (!this.isValid) return;

      this.isBusy = true;
      this.error = null;

      try {
        console.log('Pipeline to create:', this.localModelValue.name);
        var defaultInputs = {};
        for (var tool of this.localModelValue.selectedTools) {
          console.log('Selected tool:', tool.slug, tool);
          defaultInputs[tool.slug] = tool.user_params;
        }
        const data = {
          name: this.localModelValue.name,
          description:
            this.localModelValue.description || this.localModelValue.name,
          version: this.localModelValue.version,
          tools: this.localModelValue.selectedTools.map((tool) =>
            typeof tool === 'object' ? tool.slug : tool,
          ),
          default_inputs: defaultInputs,
        };
        const response = await pipelineService.createPipeline(data);
        // The panel is closed when the parent component receives this signal
        this.$emit('creation-submitted', response);
      } catch (err) {
        if (err.response == undefined) {
          this.error = err.message || 'Failed to submit creation';
        } else {
          if (err.response.data['name'] != undefined) {
            this.error = 'Name: ' + err.response.data['name'];
          } else if (err.response.data['version'] != undefined) {
            this.error = 'Version: ' + err.response.data['version'];
          } else if (err.response.data['tools'] != undefined) {
            this.error = 'Selected tools: ' + err.response.data['tools'];
          } else {
            this.error =
              err.response.data['detail'] ||
              err.message ||
              'Failed to submit creation';
          }
        }
      } finally {
        this.isBusy = false;
      }
    },

    async submitEdition() {
      if (!this.isValid) return;

      this.isBusy = true;
      this.error = null;

      try {
        console.log('Pipeline to update:', this.localModelValue.id, this.localModelValue.name);
        var defaultInputs = {};
        for (var tool of this.localModelValue.selectedTools) {
          console.log('Selected tool:', tool.slug, tool);
          if (this.toolStore.isInitTool(tool.slug)) {
            defaultInputs[tool.slug] = this.selectedTools.init_params[tool.slug];
          } else {
            defaultInputs[tool.slug] = this.selectedTools.user_params[tool.slug];
          }
        }
        console.log('New default inputs:', defaultInputs);
        const data = {
          id: this.localModelValue.id,
          name: this.localModelValue.name,
          description: this.localModelValue.description || this.localModelValue.name,
          tools: this.localModelValue.selectedTools.map((tool) =>
            typeof tool === 'object' ? tool.slug : tool,
          ),
          version: this.localModelValue.version,
          default_inputs: defaultInputs,
        };
        const response = await pipelineService.updatePipeline(data);
        // The panel is closed when the parent component receives this signal
        this.$emit('edition-submitted', response);
      } catch (err) {
        if (err.response == undefined) {
          this.error = err.message || 'Failed to submit edition';
        } else {
          if (err.response.data['name'] != undefined) {
            this.error = 'Name: ' + err.response.data['name'];
          } else if (err.response.data['version'] != undefined) {
            this.error = 'Version: ' + err.response.data['version'];
          } else if (err.response.data['tools'] != undefined) {
            this.error = 'Selected tools: ' + err.response.data['tools'];
          } else {
            this.error =
              err.response.data['detail'] ||
              err.message ||
              'Failed to submit edition';
          }
        }
      } finally {
        this.isBusy = false;
      }
    },

    async submit() {
      this.localModelValue.isCreation ? this.submitCreation() : this.submitEdition();
    },
  },
};
</script>

<style scoped>
.text-wrap {
  -webkit-line-clamp: unset !important;
  line-clamp: unset !important;
  white-space: normal !important;
  overflow-wrap: break-word;
  word-wrap: break-word;
  max-width: 600px;
}
</style>
