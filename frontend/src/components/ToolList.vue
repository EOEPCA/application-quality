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
        @click="refreshTools"
        :loading="store.loading"
      />
    </v-card-title>

    <v-alert v-if="store.error" type="error" :text="store.error" closable />

    <v-data-table
      v-if="store.tools.length"
      v-model:items-per-page="itemsPerPage"
      v-model:sort-by="sortBy"
      :headers="headers"
      :items="filteredTools"
      :search="search"
      class="elevation-1"
      hover
    >
      <!-- template v-slot:top>
          <v-toolbar flat>
            <v-toolbar-title>Tools</v-toolbar-title>
            <v-divider
              class="mx-4"
              inset
              vertical
            />
            <v-spacer />
            <v-btn
              color="primary"
              @click="openExecutionDialog"
              :disabled="!store.tools.length"
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
              __size="small"
              color="primary"
              class="mr-2"
              variant="text"
              v-tooltip:bottom-end="'Tool information'"
              :__title="'Information'"
              @click="viewToolDetails(item)"
            />
            <v-btn
              icon="mdi-pencil"
              variant="text"
              disabled
              v-tooltip:bottom-end="'Edit this tool'"
              :__title="'Edit this tool'"
              @click="editTool(item)"
            />
            <v-btn
              icon="mdi-delete"
              variant="text"
              disabled
              v-tooltip:bottom-end="'Delete the tool'"
              :__title="'Delete the tool'"
              @click="deleteTool(item)"
            />
          </td>
        </tr>
      </template>

      <template v-slot:no-data>
        <v-alert type="info" text="No tools available" class="ma-2" />
      </template>
    </v-data-table>

    <v-alert
      v-else-if="!store.loading"
      type="info"
      text="No analysis tools found"
    />

    <v-progress-circular v-else indeterminate class="ma-4" />

    <!-- Tools Details Dialog -->
    <v-dialog v-model="showDetails" max-width="1200px">
      <v-card v-if="selectedTool">
        <!-- v-card-title>
          {{ selectedTool.name || selectedTool.id }}
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="showDetails = false" />
        </v-card-title -->
        <v-card-text>
          <v-alert
            v-if="selectedTool.description"
            type="info"
            :text="selectedTool.description"
            class="mb-4"
          />
          <JsonToHtmlTable :data="pruneToolDetails(selectedTool)" />
          <!-- pre class="tool-json">{{ JSON.stringify(selectedTool, null, 2) }}</pre -->
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import { useToolStore } from '@/stores/tools';
import JsonToHtmlTable from '@/components/JsonToHtmlTable.vue';
//import VueJsonToHtmlTable from 'vue-json-to-html-table'
import 'vue-json-to-html-table/dist/style.css';

export default {
  name: 'ToolList',
  components: {
    JsonToHtmlTable,
  },
  data() {
    return {
      search: '',
      showDetails: false,
      selectedTool: null,
      itemsPerPage: 10,
      sortBy: [{ key: 'description', order: 'asc' }],

      headers: [
        {
          title: 'Description',
          key: 'description',
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
      jsonData: {
        test: 123,
      },
    };
  },

  setup() {
    const store = useToolStore();
    return { store };
  },

  computed: {
    filteredTools() {
      if (!this.search) return this.store.tools;

      const searchTerm = this.search.toLowerCase();
      return this.store.tools.filter((tool) => {
        return (
          //(tool.name && tool.name.toLowerCase().includes(searchTerm)) ||
          (tool.description &&
            tool.description.toLowerCase().includes(searchTerm)) ||
          //tool.id.toLowerCase().includes(searchTerm)
          tool.slug.toLowerCase().includes(searchTerm)
        );
      });
    },
  },

  mounted() {
    this.refreshTools();
  },

  methods: {
    async refreshTools() {
      await this.store.fetchTools();
    },

    formatDate(date) {
      if (!date) return 'N/A';
      return new Date(date).toLocaleDateString('en-UK', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        second: 'numeric',
      });
    },

    pruneToolDetails(tool) {
      const keysToKeep = [
        'name',
        'description',
        'version',
        'tags',
        'tools',
        'user_params',
      ];
      return Object.fromEntries(
        Object.entries(tool).filter(([key]) => keysToKeep.includes(key)),
      );
    },

    viewToolDetails(tool) {
      this.selectedTool = tool;
      this.showDetails = true;
    },

    editTool(tool) {
      this.selectedTool = tool;
      this.showDetails = true;
    },

    deleteTool(tool) {
      this.selectedTool = tool;
      this.showDetails = true;
    },
  },
};
</script>

<style scoped>
.tool-json {
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
