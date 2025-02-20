<template>
  <v-dialog v-model="dialogVisible" max-width="800px" persistent>
    <v-card>
      <v-card-title class="d-flex align-center">
        Execute Pipeline: {{ pipeline.slug }}
        <v-spacer />
        <v-btn
          icon="mdi-close"
          variant="text"
          @click="closeDialog"
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
          <!-- Pipeline Selection -->
          <!-- v-select
              v-model="formData.pipelineId"
              :items="pipelines"
              item-title="name"
              item-value="id"
              label="Select Pipeline"
              required
              :rules="[v => !!v || 'Pipeline is required']"
              class="mb-4"
            / -->

          <!-- Input Parameters -->
          <v-text-field
            v-model="formData.git_repo"
            label="Git repository URL"
            required
            :rules="[(v) => !!v || 'The Git repository URL is required']"
            class="mb-4"
          />

          <v-text-field
            v-model="formData.git_branch"
            label="Git branch (default: main)"
            :rules="[(v) => !!v || 'The Git branch is required']"
            class="mb-4"
          />

          <!-- v-textarea
              v-model="formData.description"
              label="Description"
              rows="3"
              class="mb-4"
            / -->

          <!-- Dynamic Parameters based on selected pipeline -->
          <!-- template v-if="selectedPipeline">
              <v-card-subtitle>Parameters</v-card-subtitle>
              <v-row>
                <v-col
                  v-for="param in selectedPipeline.parameters"
                  :key="param.name"
                  cols="12"
                  sm="6"
                >
                  <v-text-field
                    v-model="formData.parameters[param.name]"
                    :label="param.name"
                    :hint="param.description"
                    persistent-hint
                    :required="param.required"
                    :rules="param.required ? [v => !!v || `${param.name} is required`] : []"
                  />
                </v-col>
              </v-row>
            </template -->
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn
          color="grey"
          variant="text"
          @click="closeDialog"
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
  </v-dialog>
</template>

<script>
import { ref, computed } from 'vue';
import { pipelineService } from '@/services/pipelines';

export default {
  name: 'PipelineExecutionDialog',

  props: {
    modelValue: {
      type: Boolean,
      required: true,
    },
    pipeline: {
      // Invalid prop: type check failed for prop "pipeline". Expected Object, got Null
      // type: Object,
      required: true,
    },
  },

  emits: ['update:modelValue', 'execution-submitted'],

  setup(props, { emit }) {
    const form = ref(null);
    const isValid = ref(false);
    const loading = ref(false);
    const error = ref(null);

    const formData = ref({
      git_repo: '',
      git_branch: '',
      //parameters: {}
    });

    const dialogVisible = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value),
    });

    const selectedPipeline = computed({
      get: () => props.pipeline,
      set: (value) => emit('update:pipeline', value),
    });

    const resetForm = () => {
      if (form.value) {
        form.value.reset();
      }
      formData.value = {
        //git_repo: 'https://github.com/EOEPCA/application-quality',
        git_repo: 'https://github.com/pypa/sampleproject',
        git_branch: 'main',
      };
      error.value = null;
    };

    resetForm();

    const closeDialog = () => {
      resetForm();
      dialogVisible.value = false;
    };

    const submitExecution = async () => {
      if (!form.value.validate()) return;

      loading.value = true;
      error.value = null;

      try {
        console.log('Selected pipeline:', selectedPipeline.value);
        const response = await pipelineService.executePipeline(
          selectedPipeline.value.slug,
          {
            repo_url: formData.value.git_repo,
            repo_branch: formData.value.git_branch,
            //parameters: formData.value.parameters
          },
        );

        emit('execution-submitted', response);
        closeDialog();
      } catch (err) {
        error.value = err.message || 'Failed to submit execution';
      } finally {
        loading.value = false;
      }
    };

    return {
      form,
      formData,
      isValid,
      loading,
      error,
      dialogVisible,
      selectedPipeline,
      closeDialog,
      submitExecution,
    };
  },
};
</script>
