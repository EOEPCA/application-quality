<template>
  <v-card flat>
    <v-card-title class="d-flex align-center">
      <v-spacer />

      <v-select
        v-model="store.selectedPipelineId"
        label="Pipeline"
        :items="store.pipelines"
        item-title="name"
        item-value="id"
        variant="solo"
        density="compact"
        class="pa-1"
        @update:menu="refreshPipelineExecutions()"
      ></v-select>

      <!-- Polling status indicator -->
      <v-chip class="ml-2" :color="isPolling ? 'success' : 'grey'" size="small">
        {{ isPolling ? 'Live Updates' : 'Updates Paused' }}
      </v-chip>
      <!-- Polling control button -->
      <v-btn
        :icon="isPolling ? 'mdi-pause' : 'mdi-play'"
        size="small"
        class="ml-2 mr-2"
        :__color="isPolling ? 'warning' : 'success'"
        @click="togglePolling"
        :title="isPolling ? 'Pause Updates' : 'Start Updates'"
      />
      <!-- Search field -->
      <!-- <v-text-field
        v-model="search"
        prepend-inner-icon="mdi-magnify"
        label="Search"
        single-line
        hide-details
        density="compact"
        class="mx-2"
        style="max-width: 300px"
      />
      <v-btn
        icon="mdi-backspace-outline"
        size="small"
        class="mx-2"
        @click="search = ''; store.selectedPipelineId = null"
      /> -->
      <!-- Instant refresh button -->
      <!-- <v-btn
          icon="mdi-refresh"
          size="small"
          class="mx-2"
          @click="refreshPipelineExecutions"
          :loading="store.loadingExecutions"
        /> -->
    </v-card-title>

    <v-alert v-if="store.error" type="error" :text="store.error" closable />

    <v-data-table
      v-model:items-per-page="itemsPerPage"
      v-model:sort-by="sortBy"
      :headers="headers"
      :items="store.executions"
      :filter-keys="['pipeline']"
      :custom-filter="filterOnPipelineId"
      class="elevation-1"
      hover
    >
      <template v-slot:top> </template>

      <template v-slot:item="{ item }">
        <tr>
          <td>
            {{ item.pipeline && store.pipelineById(item.pipeline).name }}
          </td>
          <td>
            {{ item.pipeline && store.pipelineById(item.pipeline).version }}
          </td>
          <td>{{ formatDate(item.start_time) }}</td>
          <td>{{ formatDate(item.completion_time) }}</td>
          <td class="first-letter">{{ item.status || 'Unknown' }}</td>
          <td>
            <v-progress-linear
              :model-value="progress(item)"
              color="rgb(24, 103, 192, 0.5)"
              height="24"
              min="0"
              :max="progressMax(item)"
              :indeterminate="item.status.toLowerCase() == 'starting'"
            >
              <strong>{{ progress(item) }} / {{ progressMax(item) }}</strong>
            </v-progress-linear>
          </td>
          <td class="text-right nowrap">
            <v-btn
              color="primary"
              variant="text"
              v-tooltip:bottom-end="'Execution information'"
              @click="viewPipelineExecutionDetails(item)"
            >
              <v-icon size="26px"> mdi-information </v-icon>
            </v-btn>
            <v-btn
              color="primary"
              variant="text"
              :disabled="item.job_reports_count == 0"
              v-tooltip:bottom-end="
                'View execution reports (' + item.job_reports_count + ')'
              "
              @click="viewPipelineExecutionReports(item)"
            >
              <v-icon size="28px"> mdi-note-text-outline </v-icon>
            </v-btn>
            <v-btn
              v-if="settings.isGrafanaEnabled()"
              color="secondary"
              variant="text"
              :disabled="item.job_reports_count == 0"
              v-tooltip:bottom-end="'View execution dashboard (new page)'"
              @click="viewPipelineExecutionDashboard(item)"
            >
              <v-icon size="28px"> mdi-chart-box-outline </v-icon>
            </v-btn>
          </td>
        </tr>
      </template>

      <template v-slot:no-data>
        <v-alert
          v-if="store.selectedPipelineId"
          type="info"
          text="No execution found for the selected pipeline"
          class="ma-2"
        />
        <v-alert
          v-else
          type="info"
          text="Please select a pipeline in the list above"
          class="ma-2"
        />
      </template>
    </v-data-table>

    <!-- <v-alert
          v-else-if="!store.loadingExecutions"
          type="info"
          text="No pipeline executions found"
        />
  
        <v-progress-circular
          v-else
          indeterminate
          class="ma-4"
        /> -->

    <!-- Pipeline Details Dialog -->
    <v-dialog v-model="showDetails" max-width="800px">
      <v-card v-if="selectedExecution">
        <!-- v-card-title>
            {{ selectedExecution.pipeline}} / {{ selectedExecution.id }}
            <v-spacer />
            <v-btn icon="mdi-close" variant="text" @click="showDetails = false" />
          </v-card-title -->
        <v-card-text>
          <v-alert
            v-if="selectedExecution.status"
            type="info"
            :text="selectedExecution.status"
            class="mb-4"
          />
          <!-- JsonToHtmlTable :data="prunePipelineExecutionDetails(selectedExecution)" / -->
          <pre class="execution-json">{{
            JSON.stringify(
              prunePipelineExecutionDetails(selectedExecution),
              null,
              2,
            )
          }}</pre>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import { useSettingsStore } from '@/stores/settings';
import { useAuthStore } from '@/stores/auth';
import { useToolStore } from '@/stores/tools';
import { usePipelineStore } from '@/stores/pipelines';
import { formatDate } from '@/assets/tools';
// import JsonToHtmlTable from '@/components/JsonToHtmlTable.vue'

export default {
  name: 'PipelineExecutionList',
  // components: {
  //   JsonToHtmlTable
  // },

  data() {
    return {
      showDetails: false,
      selectedExecution: null,
      itemsPerPage: 10,
      sortBy: [{ key: 'start_time', order: 'desc' }],
      headers: [
        {
          title: 'Pipeline',
          key: 'pipeline',
          sortable: true,
          align: 'start',
        },
        {
          title: 'Version',
          key: 'version',
          sortable: true,
        },
        {
          title: 'Started',
          key: 'start_time',
          sortable: true,
        },
        {
          title: 'Completed',
          key: 'completion_time',
          sortable: true,
        },
        {
          title: 'Status',
          key: 'status',
          sortable: true,
        },
        {
          title: 'Progress',
          key: 'progress',
          sortable: true,
        },
        {
          title: '',
          key: 'actions',
          sortable: false,
          align: 'center',
        },
      ],
      // Polling properties
      pollingInterval: null,
      isPolling: false,
      pollingDelay: 5000, // 5 seconds
      lastPollTime: null,
      errorCount: 0,
      maxErrors: 3, // Stop polling after 3 consecutive errors
    };
  },

  setup() {
    const settings = useSettingsStore();
    const store = usePipelineStore();
    const toolStore = useToolStore();
    const authStore = useAuthStore();
    return { settings, store, toolStore, authStore };
  },

  computed: {
    timeSinceLastPoll() {
      if (!this.lastPollTime) return 'Never';
      const seconds = Math.floor((Date.now() - this.lastPollTime) / 1000);
      return `${seconds}s ago`;
    },
  },

  mounted() {
    this.refreshTools();
    this.refreshPipelineExecutions();
    // this.isPolling = false
    // this.togglePolling()
  },

  methods: {
    progress(execution) {
      // console.log("Progress of", execution.id, execution.job_reports_count)
      // console.log("Max progress:", this.store.pipelineById(execution.pipeline).tools.length)
      return execution.job_reports_count;
    },

    progressMax(execution) {
      // console.log("Max progress:", this.store.pipelineById(execution.pipeline).tools.length)
      const pipeline = this.store.pipelineById(execution.pipeline);
      // Do not include init tools as they don't generate reports
      console.log('Pipeline tools:', pipeline.tools);
      const analysisTools = pipeline.tools.filter(
        (tool) => !this.toolStore.isInitTool(tool),
      );
      console.log('Analysis tools:', analysisTools);
      return analysisTools.length;
    },

    filterOnPipelineId(value, query, item) {
      console.info('filterOnPipelineId:', value, query, item);
      return value == query;
    },

    async refreshTools() {
      await this.toolStore.fetchTools();
    },

    async refreshPipelineExecutions() {
      console.info('Retrieving pipelines');
      await this.store.fetchPipelines();
      console.info('Retrieving pipeline executions');
      await this.store.fetchPipelineExecutions(this.store.selectedPipelineId);
    },

    isUserInput(key) {
      const inputsToKeep = ['repo_url', 'repo_branch'];
      return inputsToKeep.includes(key) || key.includes('.');
    },

    prunePipelineExecutionDetails(execution) {
      const keysToKeep = [
        'pipeline',
        'start_time',
        'completion_time',
        'job_reports_count',
        'status',
        'user',
        'started_by',
        'usage_report',
        // 'inputs' are filtered separately below
      ];
      const details = Object.fromEntries(
        Object.entries(execution).filter(([key]) => keysToKeep.includes(key)),
      );
      // Add user parameters only
      //const executionInputs = execution.inputs;
      const userInputs = Object.fromEntries(
        Object.entries(execution.inputs).filter(([key]) =>
          this.isUserInput(key),
        ),
      );
      if (this.authStore.isAdmin) {
        // Display all inputs to admin users
        details.inputs = execution.inputs;
      } else {
        details.inputs = userInputs;
      }
      return details;
    },

    viewPipelineExecutionDetails(execution) {
      console.log('Selected execution:', execution);
      this.selectedExecution = execution;
      this.showDetails = true;
    },

    viewPipelineExecutionReports(execution) {
      console.log('Selected execution:', execution);
      this.selectedExecution = execution;
      this.store.selectedPipelineId = execution.pipeline;
      this.store.selectedExecutionId = execution.id;
      this.$router.push('/reports');
    },

    viewPipelineExecutionDashboard(execution) {
      console.log('Selected execution:', execution);
      const url = this.settings.getGrafanaPipelineExecutionURL(
        execution.pipeline,
        execution.id,
      );
      window.open(url, '_blank');
    },

    formatDate(date) {
      return formatDate(date);
    },

    startPolling() {
      if (this.isPolling) return;

      this.isPolling = true;
      this.errorCount = 0;
      this.pollingInterval = setInterval(async () => {
        await this.refreshPipelineExecutions();
      }, this.pollingDelay);

      // Initial fetch
      this.refreshPipelineExecutions();
    },

    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
        this.pollingInterval = null;
      }
      this.isPolling = false;
    },

    togglePolling() {
      if (this.isPolling) {
        this.stopPolling();
      } else {
        this.startPolling();
      }
    },

    // Method to adjust polling delay (optional)
    setPollingDelay(delay) {
      this.pollingDelay = delay;
      if (this.isPolling) {
        // Restart polling with new delay
        this.stopPolling();
        this.startPolling();
      }
    },
  },
};
</script>

<style scoped>
.execution-json {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  font-family: monospace;
}

.first-letter {
  text-transform: capitalize;
}

.nowrap {
  white-space: nowrap;
}

.v-btn {
  padding: 5px;
  min-width: 0px;
}
</style>
