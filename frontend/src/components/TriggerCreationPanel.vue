<!-- eslint-disable vue/no-mutating-props -->
<template>
  <v-navigation-drawer
    v-if="localModelValue"
    v-model="isVisible"
    location="right"
    temporary
    :width="800"
  >
    <v-card class="h-100 d-flex flex-column">
      <v-card-title class="d-flex align-center">
        <span v-if="modelValue.isCreation"
          >New trigger: {{ triggerSlug }}</span
        >
        <span v-else>Edit trigger: {{ localModelValue.name }}</span>
        <v-spacer />
        <v-btn
          icon="mdi-close"
          variant="text"
          @click="cancel"
          :disabled="isBusy"
        />
      </v-card-title>

      <v-card-subtitle
        v-if="triggerStore.error"
      >
        <v-alert
          type="error"
          closable
        >
          <div class="text-pre-line">{{ triggerStore.error }}</div>
        </v-alert>
      </v-card-subtitle>

      <v-divider></v-divider>

      <v-card-text class="flex-grow-1 overflow-y-auto">
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
              <!-- Owner (editable only by admins) -->
              <v-text-field
                v-model="localModelValue.owner_name"
                label="User"
                required
                :disabled="!localModelValue.isUserAdmin"
                :rules="[(v) => !!v || 'The user may not be empty']"
              />
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
                label="Description"
                required
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
                <template v-slot:selection="{ item }">
                  <v-icon 
                    color="primary"
                    class="me-2 pe-none" 
                    :icon="item.raw.icon || 'mdi-flash'"
                  ></v-icon>
                  <span class="pe-none">
                    {{ item.raw.name || item.raw }}
                  </span>
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
                <template v-slot:selection="{ item }">
                  <v-icon 
                    color="primary"
                    class="me-2 pe-none" 
                    :icon="item.raw.icon || 'mdi-pipe'"
                  ></v-icon>
                  <span class="pe-none">
                    {{ item.raw.name || item.raw }}
                  </span>
                </template>
              </v-select>

              <v-select
                label="Status"
                v-model="localModelValue.status"
                :items="localModelValue.availableStatus"
                :rules="[(v) => !!v || 'A status must be selected']"
              ></v-select>
              <!-- eslint-disable vue/no-v-model-argument -->
              <!-- CQL2 Filter (JSON) -->
              <v-divider
                :thickness="3"
                class="border-opacity-50 my-4"
                color="info"
                opacity=".7"
                gradient
              >CQL2 Filter (JSON)</v-divider>

              <json-editor
                ref="cql2FilterEditor"
                height="400"
                mode="tree"
                :expandedOnStart="true"
                v-model:json="localModelValue.cql2Filter"
                @change="(content, previousContent, status) => handleJsonEditorChange('cql2_filter', status)"
              />

              <!-- Default Input Parameters (JSON) -->
              <v-divider
                :thickness="3"
                class="border-opacity-50 my-4"
                color="info"
                opacity=".7"
                gradient
              >Default Input Parameters (JSON)</v-divider>

              <json-editor
                ref="paramsDefaultEditor"
                height="400"
                mode="tree"
                v-model:json="localModelValue.paramsDefault"
                @change="(content, previousContent, status) => handleJsonEditorChange('params_default', status)"
              />

              <!-- Parameters Mapping (JSON) -->
              <v-divider
                :thickness="3"
                class="border-opacity-50 my-4"
                color="info"
                opacity=".7"
                gradient
              >Parameters Mapping (JSON)</v-divider>

              <json-editor
                ref="paramsMappingEditor"
                height="400"
                mode="tree"
                v-model:json="localModelValue.paramsMapping"
                @change="(content, previousContent, status) => handleJsonEditorChange('params_mapping', status)"
              />

            </v-card-text>
          </v-card>
        </v-form>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions>
        <v-spacer />
        <v-btn color="grey" variant="text" @click="cancel" :disabled="isBusy">
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          @click="submit"
          :loading="isBusy"
          :disabled="!isValid || isJsonInvalid"
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
import { slugify, jsonParse } from '@/assets/tools';

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
      editorErrors: {
        cql2_filter: false,
        params_default: false,
        params_mapping: false
      },
    };
  },

  props: {
    // modelValue contains the creation/edit data
    modelValue: {
      type: Object,
      // default: () => ({
      //   availablePipelines: [],
      //   selectedPipeline: null,
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
    return { triggerStore };
  },

  mounted() {
    this.resetForm();
  },

  computed: {
    isVisible() {
      return this.visible;
    },

    isJsonInvalid() {
      console.debug("Editor errors:", Object.values(this.editorErrors));
      return Object.values(this.editorErrors).some(hasError => hasError === true);
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
        console.log('Watch: Local model value: ', this.localModelValue);
      },
      deep: true,
    },
  },

  methods: {

    expandAllJsonEditors() {
      this.$nextTick(() => {
        const ed1 = this.$refs.cql2FilterEditor;
        // console.log("CQL2 Editor: ", ed1);
        if (ed1 && typeof ed1.$expand === 'function') {
          ed1.$expand([], (_path) => true);
        }
        const ed2 = this.$refs.paramsDefaultEditor;
        if (ed2 && typeof ed2.$expand === 'function') {
          ed2.$expand([], (_path) => true);
        }
        const ed3 = this.$refs.paramsMappingEditor;
        if (ed3 && typeof ed3.$expand === 'function') {
          ed3.$expand([], (_path) => true);
        }
      });
    },

    resetForm() {
      // console.log('Re-initialising the trigger creation form');
      console.debug("Reset Form: Model value:", this.modelValue);
      console.debug("Reset Form: Local model value", this.localModelValue);
      this.error = null;
      this.localModelValue = this.modelValue
        ? JSON.parse(JSON.stringify(this.modelValue))
        : null;
      if (this.localModelValue.cql2Filter === undefined) {
        this.localModelValue.cql2Filter = {};
      }
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
      // Expand the contents of the JSON editors
      this.expandAllJsonEditors();
      return true;
    },

    onTriggerNameChange() {
      this.triggerName = this.localModelValue.name;
    },

    handleJsonEditorChange(editorKey, status) {
      console.debug("Editor content change:", editorKey, status);
      this.editorErrors[editorKey] = (status.contentErrors != undefined);
      console.debug("Editor errors:", Object.values(this.editorErrors));
    },

    cancel() {
      // console.log("Resetting and closing the trigger creation/edition panel")
      this.resetForm();
      this.modelValue.isCreation
        ? this.$emit('creation-cancelled')
        : this.$emit('edition-cancelled');
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
          params_default: jsonParse(this.localModelValue.paramsDefault) || {},
          params_mapping: jsonParse(this.localModelValue.paramsMapping) || {},
          cql2_filter: jsonParse(this.localModelValue.cql2Filter) || {},
          pipeline: this.localModelValue.selectedPipeline.id,
          trigger_type: this.localModelValue.selectedType.slug,
        };
        const response = await this.triggerStore.createTrigger(data);
        if (response == undefined) {
          console.error("Could not create the trigger:", this.triggerStore.error);
          return; 
        }
        // The panel is closed when the parent component receives this signal
        this.$emit('creation-submitted', response);
      } catch (err) {
        console.log('Error:', err);
        if (err.response == undefined) {
          this.error = err.message || 'Failed to submit creation request';
        } else {
          this.error =
            err.response.data['detail'] || err.message || 'Failed to submit creation request';
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
        console.log('Trigger to update:', this.localModelValue.name);
        const data = {
          // The name is not editable after creation and is already a slug
          slug: this.localModelValue.name,
          description: this.localModelValue.description,
          status: this.localModelValue.status,
          enabled: this.localModelValue.enabled,
          owner: this.localModelValue.owner,  // Cannot be changed by non-admin
          cql2_filter: jsonParse(this.localModelValue.cql2Filter) || {},
          params_default: jsonParse(this.localModelValue.paramsDefault) || {},
          params_mapping: jsonParse(this.localModelValue.paramsMapping) || {},
          pipeline: this.localModelValue.selectedPipeline.id,
          trigger_type: this.localModelValue.selectedType.slug,
        };
        const response = await this.triggerStore.updateTrigger(data);
        if (response == undefined) {
          console.error("Could not update the trigger:", this.triggerStore.error);
          return; 
        }
        // The panel is closed when the parent component receives this signal
        this.$emit('edition-submitted', response);
      } catch (err) {
        console.log('Error:', err);
        if (err.response == undefined) {
          this.error = err.message || 'Failed to submit update request';
        } else {
          this.error =
            err.response.data['detail'] || err.message || 'Failed to submit update request';
        }
      } finally {
        this.isBusy = false;
      }
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
