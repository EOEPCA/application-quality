<template>
    <v-card elevation="4">
      <v-card-title class="text-h6">
        Update Quality Check Status
      </v-card-title>

      <v-card-subtitle>
        Set the Quality Check status for a GitHub pull request or commit
      </v-card-subtitle>

      <v-card-text>
        <v-form ref="formRef" v-model="isFormValid" @submit.prevent="handleSubmit">
          <v-text-field
            v-model="repoUrl"
            label="GitHub repository URL"
            placeholder="https://github.com/owner/repo"
            prepend-inner-icon="mdi-github"
            :rules="[rules.required, rules.url]"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          />

          <v-btn-toggle
            v-model="refType"
            mandatory
            color="primary"
            density="comfortable"
            class="mb-3"
          >
            <v-btn value="pull_request" prepend-icon="mdi-source-pull">
              Pull Request
            </v-btn>
            <v-btn value="commit" prepend-icon="mdi-source-commit">
              Commit
            </v-btn>
          </v-btn-toggle>

          <v-text-field
            v-if="refType === 'pull_request'"
            v-model="prId"
            label="Pull request ID"
            placeholder="123"
            type="number"
            prepend-inner-icon="mdi-source-pull"
            :rules="[rules.required, rules.positiveInt]"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          />

          <v-text-field
            v-else
            v-model="commitId"
            label="Commit SHA (short hash)"
            placeholder="a1b2c3d"
            prepend-inner-icon="mdi-source-commit"
            :rules="[rules.required, rules.shortSha]"
            variant="outlined"
            density="comfortable"
            class="mb-2"
          />

          <v-select
            v-model="status"
            label="Status"
            :items="statusOptions"
            item-title="label"
            item-value="value"
            prepend-inner-icon="mdi-flag"
            :rules="[rules.required]"
            variant="outlined"
            density="comfortable"
          />
        </v-form>
      </v-card-text>

      <v-divider />

      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="handleCancel">
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          variant="flat"
          :disabled="!isFormValid"
          @click="handleSubmit"
        >
          Submit
        </v-btn>
      </v-card-actions>
    </v-card>
</template>

<script>
export default {
  name: 'GitHubStatusCheckForm',

  emits: ['submit', 'cancel'],

  data() {
    return {
      isFormValid: false,

      repoUrl: '',
      refType: 'pull_request', // 'pull_request' | 'commit'
      prId: '',
      commitId: '',
      status: 'pending',

      statusOptions: [
        { label: 'Pending', value: 'pending' },
        { label: 'Failure', value: 'failure' },
        { label: 'Success', value: 'success' },
      ],

      rules: {
        required: (v) => !!v || 'This field is required',
        url: (v) =>
          /^https:\/\/github\.com\/[\w.-]+\/[\w.-]+\/?$/.test(v) ||
          'Must be a valid GitHub repository URL',
        positiveInt: (v) =>
          (Number.isInteger(Number(v)) && Number(v) > 0) ||
          'Must be a positive integer',
        shortSha: (v) =>
          /^[0-9a-f]{7,40}$/i.test(v) ||
          'Must be a valid commit SHA (7-40 hex characters)',
      },
    }
  },

  methods: {
    resetForm() {
      this.$refs.formRef?.reset()
      this.refType = 'pull_request'
      this.status = 'pending'
    },

    handleSubmit() {
      if (!this.isFormValid) return
      this.$emit('submit', {
        repoUrl: this.repoUrl,
        refType: this.refType,
        ref: this.refType === 'pull_request' ? this.prId : this.commitId,
        status: this.status,
      })
      this.resetForm()
    },

    handleCancel() {
      this.resetForm()
      this.$emit('cancel')
    },
  },
}
</script>