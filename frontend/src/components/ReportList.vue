<template>
  <v-card flat>
    <v-card-title class="d-flex align-center">
      <v-spacer />

      <v-select
        v-model="pipelineStore.selectedPipelineId"
        label="Pipeline"
        :items="pipelineStore.pipelines"
        item-title="name"
        item-value="id"
        variant="solo"
        density="compact"
        class="pa-1"
        @update:model-value="refreshPipelineExecutionTimes()"
      ></v-select>

      <v-select
        v-model="pipelineStore.selectedExecutionId"
        label="Execution"
        :items="executionTimes"
        item-value="id"
        variant="solo"
        density="compact"
        class="pa-1"
        @update:model-value="refreshReports()"
      >
        <template v-slot:selection="{ item }">
          {{ formatExecution(item.props.title) }}
        </template>
        <template v-slot:item="{ item, props }">
          <v-list-item
            v-bind="props"
            :title="formatExecution(item.props.title)"
          ></v-list-item>
        </template>
      </v-select>

      <!-- v-text-field
        v-model="search"
        prepend-inner-icon="mdi-magnify"
        label="Search"
        single-line
        hide-details
        density="compact"
        class="mx-2"
        style="max-width: 300px"
      / -->
      <!-- v-btn
        icon="mdi-backspace-outline"
        size="small"
        class="mx-2"
        @click="search = ''"
      / -->
      <!-- v-btn
        icon="mdi-refresh"
        size="small"
        __class="mx-2"
        @click="refreshReports"
        :loading="pipelineStore.loadingReports"
      / -->
    </v-card-title>

    <v-alert v-if="pipelineStore.error" type="error" :text="pipelineStore.error" closable />

    <!-- eslint-disable vue/no-v-model-argument -->
    <v-data-table
      v-if="pipelineStore.reports.length"
      v-model:items-per-page="itemsPerPage"
      v-model:sort-by="sortBy"
      :headers="headers"
      :items="pipelineStore.reports"
      :search="search"
      class="elevation-1"
      hover
    >
    <!-- eslint-enable vue/no-v-model-argument -->
      <!-- template v-slot:top>
          <v-toolbar flat>
            <v-toolbar-title>Reports</v-toolbar-title>
            <v-divider
              class="mx-4"
              inset
              vertical
            />
            <v-spacer />
            <v-btn
              color="primary"
              @click="openExecutionDialog"
              :disabled="!pipelineStore.reports.length"
            >
              New Execution
            </v-btn>
          </v-toolbar>
        </template -->

      <template v-slot:item="{ item }">
        <tr>
          <td>
            {{
              pipelineStore.pipelineById(pipelineStore.executionById(item.run)?.pipeline)?.name ||
              '-'
            }}
          </td>
          <!-- <td>
            {{
              pipelineStore.pipelineById(pipelineStore.executionById(item.run).pipeline)
                .version || '-'
            }}
          </td> -->
          <!-- <td>{{ formatDate(pipelineStore.executionById(item.run).start_time) }}</td> -->
          <td>{{ item.name || 'No name' }}</td>
          <td>{{ item.instance || '' }}</td>
          <td>{{ formatDate(item.created_at) }}</td>
          <td>
            <!-- The v-tooltip style is a trick to display multiline text -->
            <div
              v-tooltip:bottom="{
                text: digestTooltip(item),
                style: 'white-space: pre-line;'
              }" 
              class="d-flex align-center ga-10 cursor-pointer"
              v-if="item.digest?.counts"
            >
              <v-badge
                color="success"
                :content="item.digest?.counts?.info"
              />
              <v-badge
                color="primary"
                :content="item.digest?.counts?.convention"
              />
              <v-badge
                color="warning"
                :content="item.digest?.counts?.warning"
              />
              <v-badge
                color="secondary"
                :content="item.digest.counts.security"
              />
              <v-badge
                color="error"
                :content="item.digest.counts.error"
              />
              <v-badge
                color="error"
                :content="item.digest.counts.critical"
              />
            </div>
            <div v-else>
              -
            </div>
          </td>
          <td class="text-right nowrap">
            <v-btn
              color="primary"
              variant="text"
              v-tooltip:bottom-end="'Report content'"
              @click="viewReport(item)"
            >
              <v-icon size="26px"> mdi-information </v-icon>
            </v-btn>
            <v-btn
              v-if="settings.isGrafanaEnabled()"
              color="secondary"
              variant="text"
              :disabled="item.job_reports_count == 0"
              v-tooltip:bottom-end="'View report in dashboard (new page)'"
              @click="viewPipelineExecutionReportDashboard(item)"
            >
              <v-icon size="28px"> mdi-chart-box-outline </v-icon>
            </v-btn>
          </td>
        </tr>
      </template>

      <template v-slot:no-data>
        <v-alert
          type="info"
          text="No analysis reports available"
          class="ma-2"
        />
      </template>
    </v-data-table>

    <v-alert
      v-else-if="!pipelineStore.loading"
      type="info"
      text="No analysis reports found"
    />

    <v-progress-circular v-else indeterminate class="ma-4" />

    <!-- Pipeline Report Dialog -->
    <v-dialog v-model="showDetails" max-width="1200px">
      <v-card v-if="selectedReport">
        <v-card-title class="d-flex align-center">
          <v-alert
            type="info"
            :text="selectedReport.name + ' report generated on ' + formatDate(selectedReport.created_at)"
            class="ma-2"
            icon-size="2rem"
          />
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="flex-grow-1 overflow-y-auto">
          <JSONTableViewer
            :data="pruneReportDetails(selectedReport)"
            :dont-convert="['output', 'digest']"
            :key-order="['tool_name', 'run_id', 'report_id', 'created_at', 'name', 'digest']"
          />
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import { useSettingsStore } from '@/stores/settings';
import { usePipelineStore } from '@/stores/pipelines';
import JSONTableViewer from '@/components/JSONTableViewer.vue';
import { formatDate, formatTime } from '@/assets/tools';

export default {
  name: 'ReportList',
  components: {
    JSONTableViewer,
  },
  data() {
    return {
      search: '',
      showDetails: false,
      executionTimes: [],
      selectedReport: null,
      itemsPerPage: 10,
      sortBy: [{ key: 'created_at', order: 'desc' }],

      headers: [
        {
          title: 'Pipeline',
          key: 'pipeline',
          sortable: false,
          align: 'start',
        },
        {
          title: 'Tool',
          key: 'name',
          sortable: true,
          align: 'start',
        },
        {
          title: 'Instance',
          key: 'instance',
          sortable: true,
          align: 'start',
        },
        {
          title: 'Report Time',
          key: 'created_at',
          sortable: true,
        },
        {
          title: 'Digest',
          key: 'digest',
          sortable: true,
        },
        {
          title: '',
          key: 'actions',
          sortable: false,
          align: 'center',
        },
      ],
    };
  },

  setup() {
    const settings = useSettingsStore();
    const pipelineStore = usePipelineStore();
    return { settings, pipelineStore };
  },

  mounted() {
    this.refreshPipelines();
    this.refreshPipelineExecutionTimes();
    this.refreshReports();
  },

  methods: {
    async refreshPipelines() {
      console.info('Retrieving pipelines');
      await this.pipelineStore.fetchPipelines();
    },
    async refreshPipelineExecutionTimes() {
      console.info('Retrieving pipeline execution times');
      if (this.pipelineStore.selectedPipelineId != undefined){
        await this.pipelineStore.fetchPipelineExecutionTimes(this.pipelineStore.selectedPipelineId);
        // Filter out the executions with no reports
        const executions = this.pipelineStore.executionTimes?.filter((execution) => {
          return (execution.job_reports_count != 0);
        });
        // Sort the reports to display the most recent at the top
        this.executionTimes = executions?.sort((a, b) =>
          b.start_time.localeCompare(a.start_time),
        );
        if (this.executionTimes.length == 0) {
          this.pipelineStore.reports = [];
          this.pipelineStore.selectedExecutionId = undefined;
        } else {
          console.log("Checking if in the list", this.pipelineStore.selectedExecutionId);
          // If the execution selected in the store is not in the list, select the most recent one
          const execution = this.executionTimes.find((exec) => exec.id === this.pipelineStore.selectedExecutionId);
          if (execution == undefined) {
            this.pipelineStore.selectedExecutionId = this.executionTimes[0]?.id;
          }
          this.refreshReports();
        }
      }
    },
    async refreshReports() {
      console.info('Retrieving pipeline execution reports');
      if (this.pipelineStore.selectedExecutionId) {
        console.info(
          'Retrieving reports for pipeline execution',
          this.pipelineStore.selectedPipelineId,
          this.pipelineStore.selectedExecutionId,
        );
        await this.pipelineStore.fetchPipelineExecutionReports(
          this.pipelineStore.selectedPipelineId,
          this.pipelineStore.selectedExecutionId,
        );
      } else {
        console.warn('No execution selected for fetching reports');
      }
    },

    formatDate(date) {
      return formatDate(date);
    },

    formatExecution(data) {
      return `${formatDate(data.start_time)} - ${formatTime(data.completion_time)} (${data.job_reports_count} reports)`;
    },

    digestTooltip(report) {
      const counts = report.digest?.counts;
      const part1 = `Info: ${counts.info}\nConvention: ${counts.convention}\nWarnings: ${counts.warning}`;
      const part2 = `Security: ${counts.security}\nError: ${counts.error}\nCritical: ${counts.critical}`;
      return `${part1}\n${part2}`;
    },

    pruneReportDetails(report) {
      const keysToKeep = [
        'tool_name',
        'run_id',
        'report_id',
        'created_at',
        'digest',
        //'id',
        //'run',
        //'instance',
        'output',
      ];
      return Object.fromEntries(
        Object.entries(report).filter(([key]) => keysToKeep.includes(key)),
      );
    },

    viewReport(report) {
      this.selectedReport = report;
      this.selectedReport.run_id = this.selectedReport.run;
      this.selectedReport.report_id = this.selectedReport.id;
      this.selectedReport.tool_name = this.selectedReport.name;
      this.showDetails = true;
    },

    viewPipelineExecutionReportDashboard(report) {
      console.debug('Selected report:', report);
      const url = this.settings.getGrafanaPipelineExecutionReportURL(
        this.pipelineStore.selectedPipelineId,
        this.pipelineStore.selectedExecutionId,
        report.name,
        report.id,
      );
      window.open(url, '_blank');
    },
  },
};
</script>

<style scoped>
.report-json {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  font-family: monospace;
}

.v-table {
  margin-top: 1rem;
}

.v-btn {
  padding: 5px;
  min-width: 0px;
}

.nowrap {
  white-space: nowrap;
}
</style>
