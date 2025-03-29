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
        v-tooltip:bottom-end="'Clear the search field'"
        @click="search = ''"
      />
      <v-btn
        icon="mdi-refresh"
        size="small"
        class="mx-2"
        v-tooltip:bottom-end="'Reload the pipeline definitions'"
        @click="refreshPipelines"
        :loading="store.loadingPipelines"
      />
      <v-btn
        icon="mdi-pencil"
        size="small"
        class="mx-2"
        color="warning"
        :disabled="!canCreatePipeline()"
        v-tooltip:bottom-end="'Create a new pipeline'"
        @click="createPipeline"
        :loading="store.loadingPipelines"
      />
    </v-card-title>

    <v-alert
      icon="mdi-check-bold"
      v-if="pipelineSuccessMessage"
      :text="pipelineSuccessMessage"
      type="success"
      closable
      @click:close="pipelineSuccessMessage = null"
    />

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
          <td>
            <div class="font-weight-bold">{{ item.name }}</div>
            <div class="font-weight-light">{{ item.description }}</div>
          </td>
          <td>{{ item.version || 'N/A' }}</td>
          <td>{{ item.owner || '-' }}</td>
          <td>{{ formatDate(item.created_at) }}</td>
          <td class="text-right">
            <v-btn
              icon="mdi-information"
              color="primary"
              class="mr-2"
              variant="text"
              v-tooltip:bottom-end="'Pipeline information (' + item.name + ')'"
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
              color="success"
              variant="text"
              v-tooltip:bottom-end="'Execute ' + item.description"
              @click="showExecutionPanel(item)"
            />
            <!-- Dropdown menu with extra actions: edit, delete -->
            <v-menu location="bottom end" :disabled="!canEditPipeline(item)">
              <template v-slot:activator="{ props }">
                <v-btn
                  icon="mdi-dots-vertical"
                  v-bind="props"
                  variant="text"
                  :disabled="!canEditPipeline(item)"
                />
              </template>

              <v-list>
                <v-list-item
                  @click="editPipeline(item)"
                  :disabled="!canEditPipeline(item)"
                >
                  <template v-slot:prepend>
                    <v-icon color="warning" icon="mdi-pencil" />
                  </template>
                  <v-list-item-title>Edit</v-list-item-title>
                </v-list-item>

                <v-list-item
                  @click="deletePipeline(item)"
                  :disabled="!canDeletePipeline(item)"
                >
                  <template v-slot:prepend>
                    <v-icon color="error" icon="mdi-delete" />
                  </template>
                  <v-list-item-title>Delete</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
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
    <v-dialog v-model="showDetailsDialog" max-width="800px">
      <v-card v-if="selectedPipeline">
        <!-- v-card-title>
            {{ selectedPipeline.name || selectedPipeline.id }}
            <v-spacer />
            <v-btn icon="mdi-close" variant="text" @click="showDetailsDialog = false" />
        </v-card-title -->
        <v-card-text>
          <v-alert
            v-if="selectedPipeline.name"
            type="info"
            :text="selectedPipeline.name"
            class="mb-4"
          />
          <JsonToHtmlTable :data="prunePipelineDetails(selectedPipeline)" />
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Pipeline creation drawer component -->
    <pipeline-creation-panel
      v-model="creationParameters"
      :visible="this.creationPanelVisible"
      @creation-submitted="handleCreationSubmitted"
      @creation-cancelled="hideCreationPanel"
      @edition-submitted="handleEditionSubmitted"
      @edition-cancelled="hideCreationPanel"
    />

    <!-- Pipeline execution drawer component -->
    <pipeline-execution-panel
      v-model="executionParameters"
      :visible="this.executionPanelVisible"
      :pipeline="this.selectedPipeline"
      @execution-submitted="handleExecutionSubmitted"
      @execution-cancelled="hideExecutionPanel"
    />

    <!-- Pipeline Delete Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="800px">
      <v-card v-if="selectedPipeline">
        <v-card-text>
          <v-alert
            type="warning"
            icon="mdi-delete"
            text="Delete Pipeline"
            class="mb-4"
            style="font-size: 1.25rem"
          />
          Are you sure you want to delete the pipeline "<span
            class="font-weight-bold"
            >{{ selectedPipeline?.description }}</span
          >"?
          <v-alert type="warning" variant="outlined" class="mt-4">
            This action cannot be undone.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            variant="text"
            @click="showDeleteDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            :loading="deletingPipeline"
            @click="confirmDeletePipeline(selectedPipeline)"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import { useAuthStore } from '@/stores/auth';
import { useToolStore } from '@/stores/tools';
import { usePipelineStore } from '@/stores/pipelines';
import JsonToHtmlTable from '@/components/JsonToHtmlTable.vue';
// import PipelineExecutionDialog from './PipelineExecutionDialog.vue'
import PipelineCreationPanel from './PipelineCreationPanel.vue';
import PipelineExecutionPanel from './PipelineExecutionPanel.vue';
import { formatDate } from '@/assets/tools';

export default {
  name: 'PipelineList',

  components: {
    JsonToHtmlTable,
    PipelineCreationPanel,
    PipelineExecutionPanel,
  },

  data() {
    return {
      search: '',
      showDetailsDialog: false,
      selectedPipeline: null,
      creationPanelVisible: false,
      creationParameters: {},
      pipelineSuccessMessage: null,
      editionPanelVisible: false,
      editionParameters: {},
      executionPanelVisible: false,
      // Used to collect the values to execute a pipeline
      // Passed as v-model to the pipeline execution panel
      executionParameters: {},
      selectedPipelineForExecution: null,
      showDeleteDialog: false,
      deletingPipeline: false,
      itemsPerPage: 10,
      sortBy: [{ key: 'name', order: 'asc' }],

      headers: [
        {
          title: 'Pipeline',
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
          title: 'Owner',
          key: 'owner',
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
    const authStore = useAuthStore();
    const store = usePipelineStore();
    const toolStore = useToolStore();
    return { store, toolStore, authStore };
  },

  mounted() {
    this.refreshTools();
    this.refreshPipelines();
  },

  emits: ['pipeline-created', 'execution-created', 'pipeline-deleted'],

  computed: {
    filteredPipelines() {
      if (!this.search) return this.store.pipelines;
      const searchTerm = this.search.toLowerCase();
      return this.store.pipelines.filter((pipeline) => {
        const allText =
          pipeline.name + pipeline.description + String(pipeline.tags);
        return (
          // (pipeline.description &&
          //   pipeline.description.toLowerCase().includes(searchTerm)) ||
          // pipeline.name.toLowerCase().includes(searchTerm)
          allText.toLowerCase().includes(searchTerm)
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

    canCreatePipeline() {
      // Any authenticated user has the right to create pipelines
      console.log('Username:', this.authStore.username);
      return this.authStore.username != undefined;
    },

    canEditPipeline(pipeline) {
      // Check if the user is either an admin or the owner of the pipeline
      return (
        this.authStore.isAdmin || this.authStore.username == pipeline.owner
      );
    },

    canDeletePipeline(pipeline) {
      // Check if the user is either an admin or the owner of the pipeline
      return (
        this.authStore.isAdmin || this.authStore.username == pipeline.owner
      );
    },

    prunePipelineDetails(pipeline) {
      const keysToKeep = [
        'name',
        'description',
        'version',
        'created_at',
        'edited_at',
        'tools',
      ];
      if (this.authStore.isAdmin) {
        // Only display these properties to admin users
        keysToKeep.append('id');
      }
      return Object.fromEntries(
        Object.entries(pipeline).filter(([key]) => keysToKeep.includes(key)),
      );
    },

    viewPipelineDetails(pipeline) {
      this.selectedPipeline = pipeline;
      this.showDetailsDialog = true;
    },

    viewPipelineExecutions(pipeline) {
      // Store the selected pipeline in the store so it accessible by the executions page
      // Navigate to the executions page
      this.store.selectedPipelineId = pipeline.id;
      this.$router.push('/executions');
    },

    createPipeline() {
      console.log('Create a new pipeline ...');
      this.refreshTools();
      this.creationParameters = {
        // name: "",
        // description: "",
        version: '0.1',
        availableTools: this.toolStore.tools,
        // selectedTools: [],
        isCreation: true,
      };
      this.creationPanelVisible = true;
    },

    hideCreationPanel() {
      console.log('Cancel pipeline creation/edition');
      this.creationPanelVisible = false;
    },

    handleCreationSubmitted(pipeline) {
      // Handle the creation of the new pipeline
      console.log('Pipeline created:', pipeline);
      // Close the pipeline creation panel
      this.creationPanelVisible = false;
      this.refreshPipelines();
      // Display a success message
      // this.pipelineSuccessMessage = "Pipeline created successfully: " + pipeline.name
      this.$notify({
        title: `Created pipeline "${pipeline.name}"`,
        type: 'success',
      });
      this.$emit('pipeline-created', pipeline);
    },

    editPipeline(pipeline) {
      console.log('Edit pipeline ...', pipeline);
      this.selectedPipeline = pipeline;

      this.creationParameters = {
        id: pipeline.id,
        name: pipeline.name,
        description: pipeline.description,
        version: pipeline.version,
        availableTools: this.toolStore.tools,
        // Retrieve the tool objects
        selectedTools: pipeline.tools.map((tool) =>
          typeof tool === 'string' ? this.toolStore.getToolById(tool) : tool,
        ),
        isCreation: false,
      };
      this.creationPanelVisible = true;
    },

    handleEditionSubmitted(pipeline) {
      // Handle the creation of the new pipeline
      console.log('Pipeline edited:', pipeline);
      // Close the pipeline creation panel
      this.creationPanelVisible = false;
      this.refreshPipelines();
      // Display a success message
      // this.pipelineSuccessMessage = "Pipeline edited successfully: " + pipeline.name
      this.$notify({
        title: `Saved pipeline "${pipeline.name}"`,
        type: 'success',
      });
      this.$emit('pipeline-created', pipeline);
    },

    hideEditionPanel() {
      console.log('Cancel pipeline edition');
      this.editionPanelVisible = false;
    },

    getPipelineUserParams(pipeline) {
      const pipeline_params = {};

      for (var tool_id of pipeline['tools']) {
        if (!this.toolStore.hasToolUserParams(tool_id)) {
          continue;
        }
        const tool_params = this.toolStore.getToolUserParams(tool_id);
        console.log('Tool params', tool_params);
        pipeline_params[tool_id] = {};
        for (const [step_id, step_params] of Object.entries(tool_params)) {
          console.log('Step:', step_id, step_params);
          pipeline_params[tool_id][step_id] = {};
          for (const [param_id, param_data] of Object.entries(step_params)) {
            console.log('Step param:', param_id, param_data);
            pipeline_params[tool_id][step_id][param_id] = param_data.default;
          }
        }
      }
      console.log('Pipeline params', pipeline_params);
      return pipeline_params;
    },

    openDeleteDialog(pipeline) {
      console.log('Delete pipeline:', pipeline);
      this.selectedPipeline = pipeline;
      this.showDeleteDialog = true;
    },

    showExecutionPanel(pipeline) {
      console.log('Selected pipeline:', pipeline);
      this.refreshTools();
      pipeline['init_params'] = {};
      pipeline['user_params'] = {};
      for (var tool_id of pipeline['tools']) {
        const tool = this.toolStore.getToolById(tool_id);
        if (this.toolStore.isInitTool(tool_id)) {
          pipeline['init_params'][tool_id] = tool ? tool['user_params'] : null;
        } else {
          pipeline['user_params'][tool_id] = tool ? tool['user_params'] : null;
        }
      }

      // "executionParameters" is used to collect the values to execute the pipeline
      this.executionParameters = {
        // repo_url: "https://github.com/EOEPCA/application-quality",
        // repo_url: 'https://github.com/pypa/sampleproject',
        // repo_branch: 'main',
        parameters: this.getPipelineUserParams(pipeline),
      };
      this.selectedPipeline = pipeline;
      this.executionPanelVisible = true;
    },

    hideExecutionPanel() {
      console.log('Cancel pipeline execution');
      this.executionPanelVisible = false;
    },

    deletePipeline(pipeline) {
      console.log('Delete pipeline ...');
      this.selectedPipeline = pipeline;
      this.showDeleteDialog = true;
    },

    async confirmDeletePipeline(pipeline) {
      this.deletingPipeline = true;
      try {
        await this.store.deletePipeline(this.selectedPipeline.id);
        this.showDeleteDialog = false;
        // Display a success message
        // this.pipelineSuccessMessage = "Pipeline deleted successfully: " + pipeline.name
        this.$notify({
          title: `Deleted pipeline "${pipeline.name}"`,
          type: 'success',
        });
        this.$emit('pipeline-deleted', pipeline);
        await this.refreshPipelines();
      } catch (error) {
        this.$notify({
          title: `Failed to delete pipeline "${pipeline.name}"`,
          text: error.message,
          type: 'error',
        });
        console.log('Failed to delete the pipeline: ', error.message);
      } finally {
        this.deletingPipeline = false;
      }
    },

    handleExecutionSubmitted(execution) {
      // Handle the new execution
      console.log('New execution created:', execution);
      // Navigate to the Monitoring page
      this.viewPipelineExecutions(execution.pipeline);
      // Show a success message
      this.$notify({
        title: 'Requested pipeline execution',
        type: 'success',
      });
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
</style>
