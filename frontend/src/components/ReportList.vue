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
        @update:menu="refreshReports()"
      ></v-select>

      <v-select
        v-model="store.selectedExecutionId"
        label="Execution Time"
        :items="filteredExecutions"
        item-title="start_time"
        item-value="id"
        variant="solo"
        density="compact"
        class="pa-1"
        @update:menu="refreshReports()"
      >
        <template v-slot:selection="{ item }">
          {{ formatDate(item.props.title) }}
        </template>
        <template v-slot:item="{ item, props }">
          <v-list-item
            v-bind="props"
            :title="formatDate(item.props.title)"
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
        :loading="store.loadingReports"
      / -->
    </v-card-title>

    <v-alert v-if="store.error" type="error" :text="store.error" closable />

    <v-data-table
      v-if="store.reports.length"
      v-model:items-per-page="itemsPerPage"
      v-model:sort-by="sortBy"
      :headers="headers"
      :items="store.reports"
      :search="search"
      class="elevation-1"
      hover
    >
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
              :disabled="!store.reports.length"
            >
              New Execution
            </v-btn>
          </v-toolbar>
        </template -->

      <template v-slot:item="{ item }">
        <tr>
          <td>
            {{
              store.pipelineById(store.executionById(item.run).pipeline).name ||
              '-'
            }}
          </td>
          <td>
            {{
              store.pipelineById(store.executionById(item.run).pipeline)
                .version || '-'
            }}
          </td>
          <td>{{ formatDate(store.executionById(item.run).start_time) }}</td>
          <td>{{ item.name || 'No name' }}</td>
          <td>{{ formatDate(item.created_at) }}</td>
          <td class="text-right nowrap">
            <v-btn
              icon="mdi-information"
              __size="small"
              color="primary"
              class="mr-2"
              variant="text"
              v-tooltip:bottom-end="'Report content'"
              :__title="'Information'"
              @click="viewReport(item)"
            />
            <v-btn
              v-if="settings.isGrafanaEnabled()"
              icon="mdi-chart-box"
              variant="text"
              color="primary"
              :disabled="item.job_reports_count == 0"
              v-tooltip:bottom-end="'View report in dashboard (new page)'"
              @click="viewPipelineExecutionReportDashboard(item)"
            />
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
      v-else-if="!store.loading"
      type="info"
      text="No analysis reports found"
    />

    <v-progress-circular v-else indeterminate class="ma-4" />

    <!-- Tools Details Dialog -->
    <v-dialog v-model="showDetails" max-width="800px">
      <v-card v-if="selectedReport">
        <!-- v-card-title>
            {{ selectedReport.name || selectedReport.id }}
            <v-spacer />
            <v-btn icon="mdi-close" variant="text" @click="showDetails = false" />
          </v-card-title -->
        <v-card-text>
          <v-alert
            v-if="selectedReport.name"
            type="info"
            :text="selectedReport.name"
            class="mb-4"
          />
          <pre class="report-json">{{
            JSON.stringify(selectedReport, null, 2)
          }}</pre>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import { useSettingsStore } from '@/stores/settings';
import { usePipelineStore } from '@/stores/pipelines';
import { formatDate } from '@/assets/tools';

export default {
  name: 'ReportList',

  data() {
    return {
      search: '',
      showDetails: false,
      //selectedPipelineId: null,
      //selectedExecutionId: null,
      selectedReport: null,
      itemsPerPage: 10,
      sortBy: [{ key: 'execution_time', order: 'asc' }],

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
          align: 'start',
        },
        {
          title: 'Pipeline Start Time',
          key: 'pipeline_start_time',
          sortable: true,
          align: 'start',
        },
        {
          title: 'Tool',
          key: 'tool_name',
          sortable: true,
          align: 'start',
        },
        {
          title: 'Report Time',
          key: 'report_time',
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
    const store = usePipelineStore();
    return { settings, store };
  },

  computed: {
    filteredExecutions() {
      if (!this.store.selectedPipelineId) return [];
      // console.log("Filtering the executions ...")
      const executions = this.store.executions.filter((execution) => {
        return (
          execution.job_reports_count != 0 &&
          execution.pipeline == this.store.selectedPipelineId
        );
      });
      // console.log("Sorting the executions ...")
      return executions.sort((a, b) =>
        b.start_time.localeCompare(a.start_time),
      );
    },

    // filteredReports() {
    //   if (!this.search) return this.store.tools
    //   const searchTerm = this.search.toLowerCase()
    //   return this.store.reports.filter(report => {
    //     return (
    //       (report.description && report.description.toLowerCase().includes(searchTerm)) ||
    //       report.slug.toLowerCase().includes(searchTerm)
    //     )
    //   })
    // },
  },

  mounted() {
    this.refreshPipelines();
    this.refreshPipelineExecutions();
    this.refreshReports();
  },

  methods: {
    async refreshPipelines() {
      console.info('Retrieving pipelines');
      await this.store.fetchPipelines();
    },
    async refreshPipelineExecutions() {
      console.info('Retrieving pipeline executions');
      await this.store.fetchPipelineExecutions();
    },
    async refreshReports() {
      console.info('Retrieving pipeline execution reports');
      //this.store.selectedPipeline = this.pipelineById(this.selectedPipelineId)
      //this.store.selectedExecution = this.executionById(this.selectedExecutionId)
      if (this.store.selectedExecutionId) {
        console.info(
          'Retrieving reports for pipeline execution',
          this.store.selectedPipelineId,
          this.store.selectedExecutionId,
        );
        await this.store.fetchPipelineExecutionReports(
          this.store.selectedPipelineId,
          this.store.selectedExecutionId,
        );
      } else {
        console.debug('No execution selected for fetching reports');
      }
    },

    formatDate(date) {
      return formatDate(date);
    },

    viewReport(report) {
      this.selectedReport = report;
      this.showDetails = true;
    },

    viewPipelineExecutionReportDashboard(report) {
      console.log('Selected execution:', report);
      // TODO: Currently the backend does not return the report Id
      // Actually, report.run == pipeline execution Id
      // => Update when the backend returns the report id
      const url = this.settings.getGrafanaPipelineExecutionReportURL(
        this.store.selectedPipelineId,
        this.store.selectedExecutionId,
        report.name,
        report.run, // TODO: change to report.id
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

.nowrap {
  white-space: nowrap;
}
</style>
