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

        <v-alert
          v-if="store.error"
          type="error"
          :text="store.error"
          closable
        />

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
            <td class="text-right">
              <v-btn
                icon="mdi-information"
                __size="small"
                color="primary"
                class="mr-2"
                variant="text"
                v-tooltip:bottom-end="'Pipeline information'"
                :__title="'Information'"
                @click="viewPipelineDetails(item)"
              />
              <v-btn
                icon="mdi-monitor-eye"
                __size="small"
                color="primary"
                class="mr-2"
                variant="text"
                v-tooltip:bottom-end="'Pipeline executions'"
                :__title="'Executions'"
                @click="viewPipelineExecutions(item)"
              />
              <v-btn
                icon="mdi-flash"
                color="error"
                variant="text"
                v-tooltip:bottom-end="'Execute ' + (item.description)"
                @click="openExecutionDialog(item)"
                :__title="'Execute ' + (item.description)"
              />
              <v-btn
                icon="mdi-pencil"
                variant="text"
                disabled
                v-tooltip:bottom-end="'Edit this pipeline'"
                :__title="'Edit this pipeline'"
                @click="editPipeline(item)"
              />
              <v-btn
                icon="mdi-delete"
                variant="text"
                disabled
                v-tooltip:bottom-end="'Delete the pipeline'"
                :__title="'Delete the pipeline'"
                @click="deletePipeline(item)"
              />
            </td>
          </tr>
        </template>

        <template v-slot:no-data>
          <v-alert
            type="info"
            text="No pipelines available"
            class="ma-2"
          />
        </template>
      </v-data-table>

        <v-alert
          v-else-if="!store.loadingPipelines"
          type="info"
          text="No pipelines found"
        />
  
        <v-progress-circular
          v-else
          indeterminate
          class="ma-4"
        />
  
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
    </v-card>

  </template>
  
<script>
import { usePipelineStore } from '@/stores/pipelines'
import JsonToHtmlTable from '@/components/JsonToHtmlTable.vue'
import PipelineExecutionDialog from './PipelineExecutionDialog.vue'
import { formatDate } from '@/assets/tools'

export default {
    name: 'PipelineList',

    components: {
      JsonToHtmlTable,
      PipelineExecutionDialog
    },

    data() {
      return {
        search: '',
        showDetails: false,
        selectedPipeline: null,
        showExecutionDialog: false,
        selectedPipelineForExecution: null,
        itemsPerPage: 10,
        sortBy: [{ key: 'name', order:'asc'}],

      headers: [
        {
          title: 'Name',
          key: 'name',
          sortable: true,
          align: 'start'
        },
        {
          title: 'Version',
          key: 'version',
          sortable: true
        },
        {
          title: 'Created',
          key: 'created_at',
          sortable: true
        },
        {
          title: 'Actions',
          key: 'actions',
          sortable: false,
          align: 'center'
        }
      ]
      }
    },
  
    setup() {
      const store = usePipelineStore()
      return { store }
    },
  
    computed: {
    filteredPipelines() {
      if (!this.search) return this.store.pipelines

      const searchTerm = this.search.toLowerCase()
      return this.store.pipelines.filter(pipeline => {
        return (
          (pipeline.description && pipeline.description.toLowerCase().includes(searchTerm)) ||
          pipeline.slug.toLowerCase().includes(searchTerm)
        )
      })
    }
  },

    mounted() {
      this.refreshPipelines()
    },
  
    methods: {
      async refreshPipelines() {
        await this.store.fetchPipelines()
      },
  
    formatDate(date) {
        return formatDate(date)
      },

    prunePipelineDetails(pipeline) {
      const keysToKeep = ['slug', 'description', 'version', 'tools'];
      return Object.fromEntries(
        Object.entries(pipeline).filter(([key]) => keysToKeep.includes(key))
      );
    },

      viewPipelineDetails(pipeline) {
        this.selectedPipeline = pipeline
        this.showDetails = true
      },

      viewPipelineExecutions(pipeline) {
        // Store the selected pipeline in the store so it accessible by the executions page
        // Navigate to the executions page
        this.store.selectedPipelineId = pipeline.slug
        this.$router.push('/executions')
      },

      editPipeline(pipeline) {
        this.selectedPipeline = pipeline
        this.showDetails = true
      },

      openExecutionDialog(pipeline) {
        console.log('Selected pipeline:', pipeline)
        this.selectedPipeline = pipeline
        this.showExecutionDialog = true
      },

      deletePipeline(pipeline) {
        this.selectedPipeline = pipeline
        this.showDetails = true
      },

      handleExecutionSubmitted(execution) {
        // Handle the new execution
        console.log('New execution created:', execution)
        // Navigate to the Monitoring page
        this.viewPipelineExecutions(execution.pipeline)
        // TODO: Show a success message
        this.$emit('execution-created', execution)
      }
    }
  }
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