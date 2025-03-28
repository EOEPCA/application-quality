<!-- eslint-disable vue/no-mutating-props -->
<template>
  <v-navigation-drawer
    __v-if="pipeline"
    v-model="isVisible"
    location="right"
    temporary
    :width="800"
  >
    <v-card>
      <v-card-title class="d-flex align-center">
        <span v-if="modelValue.creation">New pipeline: {{ pipelineName }}</span>
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
                v-model="modelValue.name"
                label="Name"
                required
                :disabled="!modelValue.isCreation"
                v-on:input="onPipelineNameChange"
                :rules="[(v) => !!v || 'The name may not be empty']"
              />
              <v-text-field
                v-model="modelValue.description"
                label="Description (optional)"
                required
                :__rules="[(v) => !!v || 'The Git repository URL is required']"
              />
              <v-text-field
                v-model="modelValue.version"
                label="Version (free text)"
                required
                :rules="[(v) => !!v || 'The version may not be empty']"
              />
              <v-combobox
                v-model="modelValue.selectedTools"
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
                    class="d-flex flex-row align-stretch"
                  >
                    <template v-slot:prepend>
                      <v-icon
                        :icon="item.raw.icon || 'mdi-tools'"
                        class="mr-2"
                      />
                    </template>
                    <!-- eslint-disable vue/no-v-text-v-html-on-component -->
                    <v-list-item-subtitle
                      class="text-wrap"
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

          <v-card
            title="Default values"
            elevation="3"
            class="mb-4"
            v-if="false"
          >
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
          </v-card>
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

export default {
  name: 'PipelineCreationPanel',

  data() {
    return {
      pipelineName: '',
      form: null,
      isValid: false,
      isBusy: false,
      error: false,
      panelVisible: false,
    };
  },

  props: {
    // modelValue contains the creation data
    modelValue: {
      type: Object,
      default: () => ({
        availableTools: [],
        selectedTools: null,
      }),
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

  methods: {
    resetForm() {
      this.error = null;
    },

    onPipelineNameChange() {
      this.pipelineName = this.modelValue.name;
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

    async submitCreation() {
      if (!this.isValid) return;

      this.isBusy = true;
      this.error = null;

      try {
        console.log('Pipeline to create:', this.modelValue.name);
        const data = {
          name: this.modelValue.name,
          description: this.modelValue.description || this.modelValue.name,
          tools: this.modelValue.selectedTools.map((tool) =>
            typeof tool === 'object' ? tool.slug : tool,
          ),
          version: this.modelValue.version,
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
        console.log('Pipeline to update:', this.modelValue.name);
        const data = {
          name: this.modelValue.name,
          description: this.modelValue.description || this.modelValue.name,
          tools: this.modelValue.selectedTools.map((tool) =>
            typeof tool === 'object' ? tool.slug : tool,
          ),
          version: this.modelValue.version,
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
      this.modelValue.isCreation ? this.submitCreation() : this.submitEdition();
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
