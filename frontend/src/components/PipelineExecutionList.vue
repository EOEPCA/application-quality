<template>
  <v-card flat>
    <v-card-title class="d-flex align-center">
      <v-spacer />

      <v-select
        v-model="selectedPipeline"
        label="Pipeline"
        :items="pipelineStore.pipelines"
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
        @click="search = ''; pipelineStore.selectedPipelineId = null"
      /> -->
      <!-- Instant refresh button -->
      <!-- <v-btn
          icon="mdi-refresh"
          size="small"
          class="mx-2"
          @click="refreshPipelineExecutions"
          :loading="pipelineStore.loadingExecutions"
        /> -->
    </v-card-title>

    <v-alert v-if="pipelineStore.error" type="error" :text="pipelineStore.error" closable />

    <!-- eslint-disable vue/no-v-model-argument -->
    <v-data-table
      v-model:items-per-page="itemsPerPage"
      v-model:sort-by="sortBy"
      :headers="filteredHeaders"
      :items="pipelineStore.executions"
      :filter-keys="['pipeline']"
      :custom-filter="filterOnPipelineId"
      class="elevation-1"
      hover
    >
    <!-- eslint-enable vue/no-v-model-argument -->
      <template v-slot:top> </template>

      <template v-slot:item="{ item }">
        <tr>
          <td>
            {{ item.pipeline && pipelineStore.pipelineById(item.pipeline).name }}
          </td>
          <!-- <td>
            {{ item.pipeline && pipelineStore.pipelineById(item.pipeline).version }}
          </td> -->
          <td v-if="this.authStore.isAdmin">{{ item.started_by }}</td>
          <td>{{ formatDate(item.start_time) }}</td>
          <td>{{ formatDate(item.completion_time) }}</td>
          <td>
            <div class="d-flex align-center">
              <span 
                :class="statusColors[item.status] || 'bg-grey'" 
                class="d-inline-block rounded-circle mr-2"
                style="width: 10px; height: 10px;"
              ></span>
              <span class="text-capitalize">{{ item.status }}</span>
            </div>
          </td>
          <td>
            <div class="d-flex align-center">
              <span 
                :class="qualityColors[item.digest_quality] || 'bg-grey'" 
                class="d-inline-block rounded-circle mr-2"
                style="width: 10px; height: 10px;"
              ></span>
              <span class="text-capitalize nowrap">{{ item.digest_quality.replaceAll("_", " ") }}</span>
            </div>
          </td>
          <td class="text-right nowrap">
            <v-btn
              color="primary"
              variant="text"
              v-tooltip:bottom-end="'Execution details'"
              @click="viewPipelineExecutionDetails(item)"
            >
              <v-icon size="26px"> mdi-information </v-icon>
            </v-btn>
            <v-btn
              color="primary"
              variant="text"
              :disabled="item.trigger_event == undefined"
              v-tooltip:bottom-end="'Trigger details'"
              @click="viewTriggerEventDetails(item)"
            >
              <v-icon size="26px"> mdi-animation-play-outline </v-icon>
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
              <!-- Add a badge on the icon to display the reports count -->
              <v-badge
                color="primary"
                :content="item.job_reports_count"
                :model-value="item.job_reports_count > 0"
              >
                <v-icon size="28px"> mdi-note-text-outline </v-icon>
              </v-badge>
            </v-btn>
            <v-btn
              v-if="settings.isGrafanaEnabled()"
              color="secondary"
              variant="text"
              v-tooltip:bottom-end="'View execution dashboard (new page)'"
              @click="viewPipelineExecutionDashboard(item)"
            >
              <v-icon size="28px"> mdi-chart-box-outline </v-icon>
            </v-btn>

            <!-- Dropdown menu with extra actions: mark pending, success, failed -->
            <v-menu v-if="this.authStore.isAdmin" location="bottom end">
              <template v-slot:activator="{ props }">
                <v-btn
                  v-bind="props"
                  variant="text"
                  :disabled="!hasTriggerAndDigestQuality(item)"
                  v-tooltip:bottom-end="'Manually change the digest quality'"
                >
                  <v-icon> mdi-dots-vertical </v-icon>
                </v-btn>
              </template>

              <v-list>
                <v-list-item
                  @click="setQualityStatus(item, 'pending')"
                >
                  <template v-slot:prepend>
                    <v-icon color="warning" icon="mdi-pencil" />
                  </template>
                  <v-list-item-title
                    >Mark Quality as Pending</v-list-item-title
                  >
                </v-list-item>
                <v-list-item
                  @click="setQualityStatus(item, 'pass')"
                >
                  <template v-slot:prepend>
                    <v-icon color="success" icon="mdi-pencil" />
                  </template>
                  <v-list-item-title
                    >Mark Quality as Passed</v-list-item-title
                  >
                </v-list-item>
                <v-list-item
                  @click="setQualityStatus(item, 'fail')"
                >
                  <template v-slot:prepend>
                    <v-icon color="error" icon="mdi-pencil" />
                  </template>
                  <v-list-item-title
                    >Mark Quality as Failed</v-list-item-title
                  >
                </v-list-item>
              </v-list>
            </v-menu>
          </td>
        </tr>
      </template>

      <template v-slot:no-data>
        <v-alert
          v-if="pipelineStore.selectedPipelineId"
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
          v-else-if="!pipelineStore.loadingExecutions"
          type="info"
          text="No pipeline executions found"
        />
  
        <v-progress-circular
          v-else
          indeterminate
          class="ma-4"
        /> -->

    <!-- Pipeline Execution Details Dialog -->
    <v-dialog v-model="showDetails" max-width="1200px">
      <v-card v-if="selectedExecution">
        <v-card-title class="d-flex align-center">
          <v-alert
            type="info"
            :text="pipelineStore.pipelineById(selectedExecution.pipeline).name + ' executed on ' + formatDate(selectedExecution.start_time) + ': ' + selectedExecution.status"
            class="ma-2"
            icon-size="2rem"
          />
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="flex-grow-1 overflow-y-auto">
          <JSONTableViewer
            :data="prunePipelineExecutionDetails(selectedExecution)"
            :dont-convert="['usage_report', 'inputs', 'digest']"
            :key-order="['pipeline_name', 'started_by', 'start_time', 'completion_time', 'status', 'job_reports_count', 'user', 'inputs', 'digest', 'digest_quality']"
          />
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Pipeline Execution Trigger Event Dialog -->
    <v-dialog v-model="showTriggerEvent" max-width="1200px">
      <v-card v-if="selectedExecution">
        <v-card-title class="d-flex align-center">
          <v-alert
            type="info"
            :text="triggerEventDetailsTitle(selectedExecution)"
            class="ma-2"
            icon="mdi-animation-play-outline"
            icon-size="2rem"
          />
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="flex-grow-1 overflow-y-auto">
          <JSONTableViewer
            :data="pruneTriggerEventDetails(selectedExecution)"
            :dont-convert="['event_headers', 'event_body']"
            :key-order="['id', 'trigger_type_name', 'pipeline_name', 'event_time', 'source', 'event_type']"
          />
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
import { useTriggerStore } from '@/stores/triggers';
import { formatDate } from '@/assets/tools';
import JSONTableViewer from '@/components/JSONTableViewer.vue';

export default {
  name: 'PipelineExecutionList',
  components: {
    JSONTableViewer,
  },

  data() {
    return {
      showDetails: false,
      showTriggerEvent: false,
      selectedPipeline: null,
      selectedTrigger: null,
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
        // {
        //   title: 'Version',
        //   key: 'version',
        //   sortable: true,
        //   admins_only: true,
        // },
        {
          // Only shown to admins using computed property, below
          title: 'User',
          key: 'started_by',
          sortable: true,
          admins_only: true,
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
          title: 'Quality',
          key: 'digest_quality',
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
      statusColors: {
        "failed": "bg-error",
        "running": "bg-warning",
        "starting": "bg-info",
        "active": "bg-warning",
        "succeeded": "bg-success",
      },
      qualityColors: {
        "undefined": "bg-grey",
        "unknown": "bg-grey",
        "pass_with_comments": "bg-warning",
        "pass": "bg-success",
        "fail": "bg-error",
        "exception": "bg-info",
      },
    };
  },

  setup() {
    const settings = useSettingsStore();
    const pipelineStore = usePipelineStore();
    const triggerStore = useTriggerStore();
    const toolStore = useToolStore();
    const authStore = useAuthStore();
    return { settings, pipelineStore, triggerStore, toolStore, authStore };
  },

  computed: {
    timeSinceLastPoll() {
      if (!this.lastPollTime) return 'Never';
      const seconds = Math.floor((Date.now() - this.lastPollTime) / 1000);
      return `${seconds}s ago`;
    },

    filteredHeaders() {
      // Filter out columns restricted to admins if necessary
      return this.headers.filter(
        (x) => !x.admins_only || this.authStore.isAdmin,
      );
    },
  },

  mounted() {
    // Called each time the Pipeline Executions page is navigated to
    this.refreshTools();
    this.pipelineStore.selectedPipelineId = this.$route.query['pipeline'];
    this.triggerStore.selectedTriggerId = this.$route.query['trigger'];
    if (this.pipelineStore.selectedPipelineId) {
      this.selectedPipeline = this.pipelineStore.pipelineById();
      console.log("Selected pipeline:", this.selectedPipeline);
    } else {
      this.selectedPipeline = undefined;
    }
    if (this.pipelineStore.selectedTriggerId) {
      this.selectedTrigger = this.triggerStore.triggerById();
      console.log("Selected trigger:", this.selectedTrigger);
    } else {
      this.selectedTrigger = undefined;
    }
    this.refreshPipelineExecutions();
    // this.isPolling = false
    // this.togglePolling()
  },

  methods: {
    progress(execution) {
      // console.log("Progress of", execution.id, execution.job_reports_count)
      // console.log("Max progress:", this.pipelineStore.pipelineById(execution.pipeline).tools.length)
      return execution.job_reports_count;
    },

    progressMax(execution) {
      // console.log("Max progress:", this.pipelineStore.pipelineById(execution.pipeline).tools.length)
      const pipeline = this.pipelineStore.pipelineById(execution.pipeline);
      // Do not include init tools as they don't generate reports
      // console.debug('Pipeline tools:', pipeline.tools);
      const analysisTools = pipeline.tools.filter(
        (tool) => !this.toolStore.isInitTool(tool),
      );
      // console.debug('Analysis tools:', analysisTools);
      return analysisTools.length;
    },

    filterOnPipelineId(value, query, item) {
      console.info('filterOnPipelineId:', value, query, item);
      return value == query;
    },

    filterOnTriggerId(value, query, item) {
      console.info('filterOnTriggerId:', value, query, item);
      return value == query;
    },

    async refreshTools() {
      await this.toolStore.fetchTools();
    },

    async refreshPipelineExecutions() {
      this.pipelineStore.selectedPipelineId = this.selectedPipeline?.id || this.selectedPipeline;
      await this.pipelineStore.fetchPipelines();
      if (this.pipelineStore.selectedPipelineId) {
        console.info('Retrieving executions of pipeline', this.pipelineStore.selectedPipelineId);
        await this.pipelineStore.fetchPipelineExecutions(this.pipelineStore.selectedPipelineId);
      } else if (this.triggerStore.selectedTriggerId) {
        console.info('Retrieving executions triggered by', this.triggerStore.selectedTriggerId);
        await this.triggerStore.fetchPipelineExecutions(this.triggerStore.selectedTriggerId);
      } else {
        console.info('Retrieving all pipeline executions');
        await this.pipelineStore.fetchPipelineExecutions();
      }
    },

    isUserInput(key) {
      const inputsToKeep = ['repo_url', 'repo_branch'];
      return inputsToKeep.includes(key) || key.includes('.');
    },

    hasTriggerAndDigestQuality(execution) {
      return execution.trigger_event && execution.digest?.digest_quality;
    },

    prunePipelineExecutionDetails(execution) {
      const keysToKeep = [
        'pipeline_name', // Pipeline name (inserted in the execution details below)
        // 'pipeline',
        'start_time',
        'completion_time',
        'job_reports_count',
        'status',
        'user',
        'started_by',
        'usage_report',
        'digest',
        'digest_quality',
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
      // Add the pipeline name
      details.pipeline_name = this.pipelineStore.pipelineById(execution.pipeline).name;
      // Add all inputs values if the user is admin
      if (this.authStore.isAdmin) {
        // Display all inputs to admin users
        details.inputs = execution.inputs;
      } else {
        details.inputs = userInputs;
      }
      return details;
    },

    pruneTriggerEventDetails(execution) {
      console.log('pruneTriggerEventDetails for trigger event Id', execution?.trigger_event);
      if (execution?.trigger_event == undefined) {
        return { 'Status': 'Not trigger event found' };
      }
      const event = this.triggerStore.getTriggerEventById(execution.trigger_event);
      console.log('Trigger event:', event);
      if (event == undefined) {
        return { 'Status': 'Loading ...' };
      }
      const keysToKeep = [
        'id',
        'trigger_type_name',
        'pipeline_name',
        'event_time',
        'source',
        'event_type',
        'event_headers',
        'event_body',
      ];
      const details = Object.fromEntries(
        Object.entries(event).filter(([key]) => keysToKeep.includes(key)),
      );
      return details;
    },

    triggerEventDetailsTitle(execution) {
      console.log('triggerEventDetailsTitle for trigger event Id', execution?.trigger_event);
      if (execution?.trigger_event == undefined) {
        return 'No trigger event found';
      }
      const event = this.triggerStore.getTriggerEventById(execution.trigger_event);
      if (event == undefined) {
        return 'Loading ...';
      }
      return 'Trigger event: ' + event.trigger_type_name + ' received on ' + formatDate(event.event_time);
    },

    viewPipelineExecutionDetails(execution) {
      console.log('Selected execution:', execution);
      this.selectedExecution = execution;
      this.showDetails = true;
    },

    viewTriggerEventDetails(execution) {
      console.log('Selected execution:', execution);
      this.selectedExecution = execution;
      this.showTriggerEvent = true;
    },

    viewPipelineExecutionReports(execution) {
      console.log('Selected execution:', execution);
      this.selectedExecution = execution;
      this.pipelineStore.selectedPipelineId = execution.pipeline;
      this.pipelineStore.selectedExecutionId = execution.id;
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

    async setQualityStatus(execution, status) {
      console.log('Set quality status of execution to ', execution, status);
      try {
        await this.pipelineStore.setExecutionQualityStatus(execution, status);
        this.refreshPipelineExecutions();
        this.$notify({
          title: `Successfully changed the quality status to: ${status}`,
          type: 'success',
        });
      } catch (error) {
        this.$notify({
          title: 'Failed to change the quality status:',
          text: error,
          type: 'error',
        });
      }
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

.nowrap {
  white-space: nowrap;
}

.v-btn {
  padding: 5px;
  min-width: 0px;
}

.v-icon {
  font-size: 26px;
  min-width: 30px;
}
</style>
