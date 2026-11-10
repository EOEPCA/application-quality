<template>
  <div>
    <h2 class="text-h4 mb-4">
      <v-icon icon="mdi-cog" size="x-small" class="mr-2" />Settings
    </h2>
    <p>Instance name: {{ settings.instance__name }}</p>
    <p>Version: {{ settings.instance__version }}</p>
    <p>Date: {{ settings.instance__date }}</p>

    <p v-if="settings.isGrafanaEnabled() == true">
      Grafana powered
      <a target="_blank" :href="settings.getGrafanaDashboardsURL()"
        >Dashboards</a
      >
    </p>
    <p v-if="settings.isDebugEnabled() == true">
      <a target="_blank" :href="settings.getGrafanaPipelineExecutionsURL()"
        >Grafana Dashboards Pipeline executions</a
      >
    </p>
    <p v-if="settings.isDebugEnabled() == true">
      <a
        target="_blank"
        :href="settings.getGrafanaPipelineExecutionURL('Python pipeline', 38)"
        >Grafana Dashboards Pipeline execution 38</a
      >.
    </p>
    <p v-if="settings.isDebugEnabled() == true">
      <a
        target="_blank"
        :href="
          settings.getGrafanaPipelineExecutionReportURL(
            'Python pipeline',
            38,
            'ruff',
            35,
          )
        "
        >Grafana Dashboards Pipeline execution report 35</a
      >.
    </p>
    <p>
      <label v-if="this.authStore.isAdmin">
        <span>
          Show Deleted Triggers:
        </span>
        <input 
          type="checkbox" 
          v-model="settings.showDeletedTriggers" 
        />
      </label>
    </p>
    <br/>
    <p>
      <label v-if="this.authStore.isAdmin">
        <v-btn color="primary" @click="gitHubDialog = true" class="text-none">
          Update Quality Check Status in GitHub
        </v-btn>
        <v-dialog v-model="gitHubDialog" max-width="640">
          <GitHubStatusCheckForm @submit="onGitHubSubmit" @cancel="onGitHubCancel" />
        </v-dialog>
      </label>
    </p>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';
import { actionsService } from '@/services/actions';
import GitHubStatusCheckForm from '@/components/GitHubStatusCheckForm.vue';

export default {
  name: 'SettingsView',
  components: {
    GitHubStatusCheckForm,
  },
  data() {
    return {
      gitHubDialog: false,
    }
  },
  setup() {
    const authStore = useAuthStore();
    const settings = useSettingsStore();
    return { settings, authStore };
  },
  methods: {
    async onGitHubSubmit(payload) {
      // payload = { repoUrl, refType, ref, status }
      console.log('Received submit payload:', payload)

      try {
        await actionsService.setGitHubQualityCheckStatus(payload)
        this.$notify({
          title: 'Quality Check status updated successfully',
          type: 'success',
        });
      } catch (err) {
        let message = err.response?.data?.error;
        if (message == undefined) {
          message = err.message;
        }
        this.$notify({
          title: `Failed to update status: ${message}`,
          type: 'error',
        });
      }
      this.gitHubDialog = false
    },

    onGitHubCancel() {
      // console.log('Dialog was cancelled')
      this.gitHubDialog = false
    },
  },
};
</script>
