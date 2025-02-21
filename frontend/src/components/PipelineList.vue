<template>
  <v-card flat>
    <v-card-title class="d-flex align-center">
      <v-spacer />
      <v-text-field
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
        @click="search = ''"
      />
      <v-btn
        icon="mdi-refresh"
        size="small"
        class="mx-2"
        @click="refreshPipelines"
        :loading="store.loadingPipelines"
      />
    </v-card-title>

    <v-alert v-if="store.error" type="error" :text="store.error" closable />

    <v-data-table
      v-if="store.pipelines.length"
      v-model:items-per-page="itemsPerPage"
      v-model:sort-by="sortBy"
      :headers="headers"
      :items="filteredPipelines"
      :search="search"
      class="elevation-1"
      hover
    >
      <!-- template v-slot:top>
          <v-toolbar flat>
            <v-toolbar-title>Pipelines</v-toolbar-title>
            <v-divider
              class="mx-4"
              inset
              vertical
            />
            <v-spacer />
            <v-btn
              color="primary"
              @click="openExecutionDialog"
              :disabled="!store.pipelines.length"
            >
              New Execution
            </v-btn>
          </v-toolbar>
        </template -->

      <template v-slot:item="{ item }">
        <tr>
          <td>{{ item.description || 'No description' }}</td>
          <td>{{ item.version || 'N/A' }}</td>
          <td>{{ formatDate(item.created_at) }}</td>
          <td class="text-right nowrap">
            <v-btn
              icon="mdi-information"
              color="primary"
              class="mr-2"
              variant="text"
              v-tooltip:bottom-end="'Pipeline information'"
              @click="viewPipelineDetails(item)"
            />
            <v-btn
              icon="mdi-monitor-eye"
              color="primary"
              class="mr-2"
              variant="text"
              v-tooltip:bottom-end="'Pipeline executions'"
              @click="viewPipelineExecutions(item)"
            />
            <!-- <v-btn
                icon="mdi-flash"
                color="error"
                variant="text"
                v-tooltip:bottom-end="'Execute ' + (item.description)"
                @click="openExecutionDialog(item)"
                :__title="'Execute ' + (item.description)"
              /> -->
            <v-btn
              icon="mdi-flash"
              color="error"
              variant="text"
              v-tooltip:bottom-end="'Execute ' + item.description"
              @click="showExecutionPanel(item)"
            />
            <v-btn
              icon="mdi-pencil"
              variant="text"
              disabled
              v-tooltip:bottom-end="'Edit this pipeline'"
              @click="editPipeline(item)"
            />
            <v-btn
              icon="mdi-delete"
              variant="text"
              disabled
              v-tooltip:bottom-end="'Delete the pipeline'"
              @click="deletePipeline(item)"
            />
          </td>
        </tr>
      </template>

      <template v-slot:no-data>
        <v-alert type="info" text="No pipelines available" class="ma-2" />
      </template>
    </v-data-table>

    <v-alert
      v-else-if="!store.loadingPipelines"
      type="info"
      text="No pipelines found"
    />

    <v-progress-circular v-else indeterminate class="ma-4" />

    <!-- Pipeline Details Dialog -->
    <v-dialog v-model="showDetails" max-width="800px">
      <v-card v-if="selectedPipeline">
        <!-- v-card-title>
            {{ selectedPipeline.name || selectedPipeline.id }}
            <v-spacer />
            <v-btn icon="mdi-close" variant="text" @click="showDetails = false" />
          </v-card-title -->
        <v-card-text>
          <v-alert
            v-if="selectedPipeline.description"
            type="info"
            :text="selectedPipeline.description"
            class="mb-4"
          />
          <JsonToHtmlTable :data="prunePipelineDetails(selectedPipeline)" />
          <!-- pre class="pipeline-json">{{ JSON.stringify(selectedPipeline, null, 2) }}</pre -->
        </v-card-text>
      </v-card>
    </v-dialog>

    <pipeline-execution-dialog
      v-model="showExecutionDialog"
      :pipeline="this.selectedPipeline"
      @execution-submitted="handleExecutionSubmitted"
    />

    <!-- Pipeline execution drawer component -->
    <pipeline-execution-panel
      v-model="executionParameters"
      :visible="this.executionPanelVisible"
      :pipeline="this.selectedPipeline"
      @execution-submitted="handleExecutionSubmitted"
      @execution-cancelled="hideExecutionPanel"
    />
  </v-card>
</template>

<script>
import { useToolStore } from '@/stores/tools';
import { usePipelineStore } from '@/stores/pipelines';
import JsonToHtmlTable from '@/components/JsonToHtmlTable.vue';
import PipelineExecutionDialog from './PipelineExecutionDialog.vue';
import PipelineExecutionPanel from './PipelineExecutionPanel.vue';
import { formatDate } from '@/assets/tools';

export default {
  name: 'PipelineList',

  components: {
    JsonToHtmlTable,
    PipelineExecutionDialog,
    PipelineExecutionPanel,
  },

  data() {
    return {
      search: '',
      showDetails: false,
      selectedPipeline: null,
      showExecutionDialog: false,
      executionPanelVisible: false,
      executionParameters: {},
      selectedPipelineForExecution: null,
      itemsPerPage: 10,
      sortBy: [{ key: 'name', order: 'asc' }],

      headers: [
        {
          title: 'Name',
          key: 'name',
          sortable: true,
          align: 'start',
        },
        {
          title: 'Version',
          key: 'version',
          sortable: true,
        },
        {
          title: 'Created',
          key: 'created_at',
          sortable: true,
        },
        {
          title: 'Actions',
          key: 'actions',
          sortable: false,
          align: 'center',
        },
      ],
    };
  },

  setup() {
    const store = usePipelineStore();
    const toolStore = useToolStore();
    return { store, toolStore };
  },

  mounted() {
    this.refreshTools();
    this.refreshPipelines();
  },

  computed: {
    filteredPipelines() {
      if (!this.search) return this.store.pipelines;

      const searchTerm = this.search.toLowerCase();
      return this.store.pipelines.filter((pipeline) => {
        return (
          (pipeline.description &&
            pipeline.description.toLowerCase().includes(searchTerm)) ||
          pipeline.slug.toLowerCase().includes(searchTerm)
        );
      });
    },
  },

  methods: {
    async refreshPipelines() {
      await this.store.fetchPipelines();
    },

    async refreshTools() {
      await this.toolStore.fetchTools();
    },

    formatDate(date) {
      return formatDate(date);
    },

    prunePipelineDetails(pipeline) {
      const keysToKeep = ['slug', 'description', 'version', 'tools'];
      return Object.fromEntries(
        Object.entries(pipeline).filter(([key]) => keysToKeep.includes(key)),
      );
    },

    viewPipelineDetails(pipeline) {
      this.selectedPipeline = pipeline;
      this.showDetails = true;
    },

    viewPipelineExecutions(pipeline) {
      // Store the selected pipeline in the store so it accessible by the executions page
      // Navigate to the executions page
      this.store.selectedPipelineId = pipeline.slug;
      this.$router.push('/executions');
    },

    editPipeline(pipeline) {
      this.selectedPipeline = pipeline;
      this.showDetails = true;
    },

    getPipelineUserParams(pipeline) {
      const pipeline_params = {};

      for (var tool_id of pipeline['tools']) {
        if (!this.toolStore.hasToolUserParams(tool_id)) {
          continue;
        }
        const tool_params = this.toolStore.getToolUserParams(tool_id);
        // console.log("Tool params", tool_params)
        pipeline_params[tool_id] = {};
        for (const [step_id, step_params] of Object.entries(tool_params)) {
          // console.log("Step:", step_id, step_params)
          pipeline_params[tool_id][step_id] = {};
          for (const [param_id, param_data] of Object.entries(step_params)) {
            // console.log("Step param:", param_id, param_data)
            pipeline_params[tool_id][step_id][param_id] = param_data.default;
          }
        }
      }
      console.log('Pipeline params', pipeline_params);
      return pipeline_params;
    },

    openExecutionDialog(pipeline) {
      console.log('Selected pipeline:', pipeline);
      this.selectedPipeline = pipeline;
      this.showExecutionDialog = true;
    },

    showExecutionPanel(pipeline) {
      console.log('Selected pipeline:', pipeline);
      this.refreshTools();
      pipeline['user_params'] = {};
      for (var tool_id of pipeline['tools']) {
        const tool = this.toolStore.getToolById(tool_id);
        pipeline['user_params'][tool_id] = tool ? tool['user_params'] : null;
      }

      this.executionParameters = {
        repo_url: 'https://github.com/pypa/sampleproject',
        repo_branch: 'main',
        parameters: this.getPipelineUserParams(pipeline),
      };
      this.selectedPipeline = pipeline;
      this.executionPanelVisible = true;
    },

    hideExecutionPanel() {
      this.executionPanelVisible = false;
    },

    deletePipeline(pipeline) {
      this.selectedPipeline = pipeline;
      this.showDetails = true;
    },

    handleExecutionSubmitted(execution) {
      // Handle the new execution
      console.log('New execution created:', execution);
      // Navigate to the Monitoring page
      this.viewPipelineExecutions(execution.pipeline);
      // TODO: Show a success message
      this.$emit('execution-created', execution);
    },
  },
};
</script>

<style scoped>
.pipeline-json {
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
