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
        :loading="toolStore.loading"
      />
    </v-card-title>

    <v-alert
      v-if="toolStore.error"
      type="error"
      :text="toolStore.error"
      closable
    />

    <v-data-table
      v-if="toolStore.tools.length"
      v-model:items-per-page="itemsPerPage"
      v-model:sort-by="sortBy"
      :headers="filteredHeaders"
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
              :disabled="!toolStore.tools.length"
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
          <td _v-if="this.authStore.isAdmin">{{ item.status }}</td>
          <td v-if="this.authStore.isAdmin">{{ item.available }}</td>
          <td class="nowrap">
            <v-chip
              v-for="tag_name in item.tags"
              :key="tag_name"
              size="small"
              class="mr-2"
              :color="tagChipColor(tag_name)"
              v-tooltip:bottom-end="tagChipTooltip(tag_name)"
              >{{ tagChipLabel(tag_name) }}</v-chip
            >
          </td>
          <!-- <td>{{ formatDate(item.created_at) }}</td> -->
          <td class="text-right nowrap">
            <v-btn
              color="primary"
              variant="text"
              v-tooltip:bottom-end="'Tool information'"
              @click="viewToolDetails(item)"
            >
              <v-icon size="26px"> mdi-information </v-icon>
            </v-btn>
            <!-- <v-btn
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
            /> -->
          </td>
        </tr>
      </template>

      <template v-slot:no-data>
        <v-alert type="info" text="No tools available" class="ma-2" />
      </template>
    </v-data-table>

    <v-alert
      v-else-if="!toolStore.loading"
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
            v-if="selectedTool.name"
            type="info"
            :text="selectedTool.name"
            class="mb-4"
          />
          <JsonToHtmlTable
            :data="pruneToolDetails(selectedTool)"
            :showDataType="false"
            :showKey="false"
          />
          <!-- pre class="tool-json">{{ JSON.stringify(selectedTool, null, 2) }}</pre -->
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import { useAuthStore } from '@/stores/auth';
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
          title: 'Tool',
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
          title: 'Status',
          key: 'status',
          sortable: true,
          // admins_only: true,
        },
        {
          title: 'Available',
          key: 'available',
          sortable: true,
          admins_only: true,
        },
        {
          title: 'Purposes',
          key: 'tags',
          sortable: true,
        },
        {
          title: '',
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
    const authStore = useAuthStore();
    const toolStore = useToolStore();
    return { authStore, toolStore };
  },

  computed: {
    filteredTools() {
      if (!this.search) return this.toolStore.tools;
      const searchTerm = this.search.toLowerCase();
      return this.toolStore.tools.filter((tool) => {
        return (
          //(tool.name && tool.name.toLowerCase().includes(searchTerm)) ||
          (tool.description &&
            tool.description.toLowerCase().includes(searchTerm)) ||
          //tool.id.toLowerCase().includes(searchTerm)
          tool.slug.toLowerCase().includes(searchTerm)
        );
      });
    },

    filteredHeaders() {
      // Do not display tool properties restricted to admin users
      return this.headers.filter(
        (x) => !x.admins_only || this.authStore.isAdmin,
      );
    },
  },

  mounted() {
    this.refreshTools();
  },

  methods: {
    async refreshTools() {
      await this.toolStore.fetchTools();
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

    tagChipColor(tagName) {
      // Determine color based on tag name prefix
      let color = 'grey';
      if (typeof tagName === 'string') {
        if (tagName.toLowerCase().startsWith('asset')) {
          color = 'blue';
        } else if (tagName.toLowerCase().startsWith('type')) {
          color = 'green';
        }
      }
      console.debug(`Chip color for tag ${tagName} is ${color}`);
      return color;
    },

    tagChipLabel(tagName) {
      // Extract the substring after colon
      if (typeof tagName !== 'string') return tagName;
      const colonIndex = tagName.indexOf(':');
      if (colonIndex !== -1 && colonIndex < tagName.length - 1) {
        return tagName.substring(colonIndex + 1).trim();
      }
      return tagName;
    },

    tagChipTooltip(tagName) {
      let tooltip = 'Not an analysis tool';
      let label = this.tagChipLabel(tagName);
      if (label == 'python') {
        tooltip = 'Analyses Python scripts';
      } else if (label == 'notebook') {
        tooltip = 'Analyses iPython / Jupyter notebooks';
      } else if (label == 'cwl') {
        tooltip = 'Analyses Application Package CWL files';
      } else if (label == 'best practice') {
        tooltip = 'Verifies the applications compliance with best practices';
      } else if (label == 'app quality') {
        tooltip = 'Verifies the applications quality';
      } else if (label == 'app security') {
        tooltip = 'Verifies the applications security and safety';
      }
      return tooltip;
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

.v-btn {
  padding: 5px;
  min-width: 0px;
}

.nowrap {
  white-space: nowrap;
}
</style>
