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
          >New trigger: {{ triggerSlug }}</span
        >
        <span v-else>Edit trigger: {{ triggerSlug }}</span>
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
          <v-card elevation="3" class="mb-4">
            <v-card-text>
              <!-- Enabled/Disabled switch -->
              <div class="d-flex align-center ga-4">
                <span class="text-body-1">Enabled</span>
                <v-switch
                  v-model="localModelValue.enabled"
                  color="primary"
                  hide-details
                ></v-switch>
              </div>
              <!-- Trigger name / slug -->
              <v-text-field
                v-model="localModelValue.name"
                label="Name"
                required
                :disabled="!modelValue.isCreation"
                v-on:input="onTriggerNameChange"
                :rules="[(v) => !!v || 'The name may not be empty']"
              />
              <!-- Description multi-line text -->
              <v-textarea
                v-model="localModelValue.description"
                label="Description (optional)"
              />
              <!-- Trigger Type drop-down list -->
              <v-select
                label="Event type"
                v-model="localModelValue.selectedType"
                :items="localModelValue.availableTypes"
                :rules="[(v) => !!v || 'An event type must be selected']"
              >
                <template v-slot:item="{ props, item }">
                  <v-list-item
                    v-bind="props"
                    :title="item.raw.name"
                    class="d-flex flex-row align-stretch font-weight-bold"
                  >
                    <!-- eslint-disable vue/no-v-text-v-html-on-component -->
                    <v-list-item-subtitle
                      class="text-wrap font-weight-light"
                      v-html="item.raw.description"
                    />
                    <!-- eslint-enable vue/no-v-text-v-html-on-component -->
                  </v-list-item>
                </template>
                <!-- Template for the selected entry -->
                <template v-slot:chip="{ props, item }">
                  <div
                    v-bind="props"
                    :prepend-icon="item.icon || 'mdi-tools'"
                  >
                    {{ item.raw.name || item }}
                  </div>
                </template>
              </v-select>
              <!-- Pipeline drop-down list -->
              <v-select
                label="Pipeline to execute"
                v-model="localModelValue.selectedPipeline"
                :items="localModelValue.availablePipelines"
                :rules="[(v) => !!v || 'A pipeline must be selected']"
              >
                <template v-slot:item="{ props, item }">
                  <v-list-item
                    v-bind="props"
                    :title="item.raw.name"
                    class="d-flex flex-row align-stretch font-weight-bold"
                  >
                    <!-- eslint-disable vue/no-v-text-v-html-on-component -->
                    <v-list-item-subtitle
                      class="text-wrap font-weight-light"
                      v-html="item.raw.description"
                    />
                    <!-- eslint-enable vue/no-v-text-v-html-on-component -->
                  </v-list-item>
                </template>
                <!-- Template for the selected entry -->
                <template v-slot:chip="{ props, item }">
                  <div
                    v-bind="props"
                    :prepend-icon="item.icon || 'mdi-tools'"
                  >
                    {{ item.raw.name || item }}
                  </div>
                </template>
              </v-select>

              <v-select
                label="Status"
                v-model="localModelValue.status"
                :items="localModelValue.availableStatus"
                :rules="[(v) => !!v || 'A status must be selected']"
              ></v-select>

              <!-- CQL2 Filter (JSON) -->
              <v-divider
                :thickness="3"
                class="border-opacity-25"
                color="info"
                opacity=".7"
                gradient
              >CQL2 Filter (JSON)</v-divider>

              <json-editor
                height="400"
                mode="tree"
                v-model="localModelValue.cql2Filter" 
              />

              <!-- Default Input Parameters (JSON) -->
              <v-divider
                :thickness="3"
                class="border-opacity-25"
                color="info"
                opacity=".7"
                gradient
              >Default Input Parameters (JSON)</v-divider>

              <json-editor
                height="400"
                mode="tree"
                v-model="localModelValue.paramsDefault" 
              />

              <!-- Parameters Mapping (JSON) -->
              <v-divider
                :thickness="3"
                class="border-opacity-25"
                color="info"
                opacity=".7"
                gradient
              >Parameters Mapping (JSON)</v-divider>

              <json-editor
                height="400"
                mode="tree"
                v-model="localModelValue.paramsMapping" 
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
          {{ modelValue.creation ? 'Create' : 'Submit Changes' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-navigation-drawer>
</template>

<script>
import { useTriggerStore } from '@/stores/triggers';
import JsonEditor from 'vue3-ts-jsoneditor';
import { slugify } from '@/assets/tools';

export default {
  name: 'TriggerCreationPanel',

  components: {
    JsonEditor,
  },

  data() {
    return {
      triggerSlug: '',
      form: null,
      isValid: false,
      isBusy: false,
      error: false,
      panelVisible: false,
      // These are given values in resetForm()
      localModelValue: null,
      localTrigger: null,
      localVisible: false,
    };
  },

  props: {
    // modelValue contains the creation/edit data
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
    const triggerStore = useTriggerStore();
    //const pipelineStore = usePipelineStore();
    return {
      triggerStore,
    //  pipelineStore,
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
        if (this.visible) {
          if (this.modelValue.isCreation) {
            console.log('Initialising the trigger creation panel');
          } else {
            console.log('Initialising the trigger edition panel');
          }
          this.resetForm();
        }
      },
    },
    localModelValue: {
      handler() {
        console.log('local model value...');
        console.debug('Enabled:', this.localModelValue.enabled);
        console.debug('Status:', this.localModelValue.status);
        console.debug('CQL2 filter:', this.localModelValue.cql2Filter);
        console.debug('Params default:', this.localModelValue.paramsDefault);
        console.debug('Params mapping:', this.localModelValue.paramsMapping);
        console.debug('Trigger type:', this.localModelValue.triggerType);
        console.debug('Selected type:', this.localModelValue.selectedType);
        console.debug('Trigger types:', this.localModelValue.triggerTypes);
        console.debug('Pipeline:', this.localModelValue.pipeline);
        console.debug('Selected pipeline:', this.localModelValue.selectedPipeline);
        console.debug('Available pipelines:', this.localModelValue.availablePipelines);
        console.debug('Default inputs:', this.localModelValue.defaultInputs);
        this.updateCreationPanel();
      },
      deep: true,
    },
  },

  methods: {
    resetForm() {
      // console.log('Re-initialising the trigger creation form');
      console.debug("this.modelValue", this.modelValue);
      console.debug("this.localModelValue", this.localModelValue);
      this.error = null;
      this.localModelValue = this.modelValue
        ? JSON.parse(JSON.stringify(this.modelValue))
        : null;
      if (this.localModelValue.paramsDefault === undefined) {
        this.localModelValue.paramsDefault = {};
      }
      if (this.localModelValue.paramsMapping === undefined) {
        this.localModelValue.paramsMapping = {};
      }
      this.localModelValue.selectedType = this.localModelValue.triggerType;
      this.localModelValue.selectedPipeline = this.localModelValue.pipeline;
      this.localTrigger = this.trigger;
      this.localVisible = this.visible;
      this.updateCreationPanel();
      return true;
    },

    onTriggerNameChange() {
      this.triggerName = this.localModelValue.name;
    },

    cancel() {
      // console.log("Resetting and closing the trigger creation/edition panel")
      this.resetForm();
      this.modelValue.isCreation
        ? this.$emit('creation-cancelled')
        : this.$emit('edition-cancelled');
    },

    updateCreationPanel() {
      return;
    },

    async submitCreation() {
      if (!this.isValid) return;
      this.isBusy = true;
      this.error = null;
      try {
        console.log('Trigger to create:', this.localModelValue.name);
        const data = {
          slug: slugify(this.localModelValue.name),
          description: this.localModelValue.description,
          status: this.localModelValue.status,
          enabled: this.localModelValue.enabled,
          owner: this.localModelValue.owner,  // Cannot be changed by non-admin
          params_default: this.localModelValue.params_default,
          params_mapping: this.localModelValue.params_mapping,
          cql2_filter: this.localModelValue.cql2Filter,
          pipeline_id: this.localModelValue.selectedPipeline.id,
          pipeline_name: this.localModelValue.selectedPipeline.name,
          pipeline_version: this.localModelValue.selectedPipeline.version,
          trigger_type: this.localModelValue.selectedType.id,
          trigger_type_name: this.localModelValue.selectedType.name,
        };
        const response = await this.triggerStore.createTrigger(data);
        // The panel is closed when the parent component receives this signal
        this.$emit('creation-submitted', response);
      } catch (err) {
        console.log('Error:', err);
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

      // TODO

    },

    async submit() {
      this.localModelValue.isCreation
        ? this.submitCreation()
        : this.submitEdition();
    },
  }
}
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
