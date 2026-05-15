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
        @click="refreshTriggers"
        :loading="triggerStore.loading"
      />
    </v-card-title>

    <v-alert
      v-if="triggerStore.error"
      type="error"
      :text="triggerStore.error"
      closable
    />

    <v-data-table
      v-if="triggerStore.triggers.length"
      v-model:items-per-page="itemsPerPage"
      v-model:sort-by="sortBy"
      :headers="filteredHeaders"
      :items="filteredTriggers"
      :search="search"
      class="elevation-1"
      hover
    >

      <template v-slot:item="{ item }">
        <tr>
          <td>
            <div>
                <span class="font-weight-bold">{{ item.trigger_type_name }}</span>
                -->
                <span class="font-weight-bold">{{ item.pipeline_name }}</span>
            </div>
            <div class="font-weight-light">{{ item.description }}</div>
          </td>
          <td v-if="this.authStore.isAdmin">{{ item.owner }}</td>
          <!-- <td>{{ item.trigger_type_name || 'N/A' }}</td> -->
          <!-- <td>{{ item.pipeline_name || 'N/A' }}</td> -->
          <td _v-if="this.authStore.isAdmin">{{ item.status }}</td>
          <td _v-if="this.authStore.isAdmin">{{ item.enabled }}</td>
          <td class="text-right nowrap">
            <v-btn
              color="primary"
              variant="text"
              v-tooltip:bottom-end="'Trigger information'"
              @click="viewTriggerDetails(item)"
            >
              <v-icon size="26px"> mdi-information </v-icon>
            </v-btn>
            <!-- <v-btn
              icon="mdi-pencil"
              variant="text"
              disabled
              v-tooltip:bottom-end="'Edit this trigger'"
              :__title="'Edit this trigger'"
              @click="editTrigger(item)"
            />
            <v-btn
              icon="mdi-delete"
              variant="text"
              disabled
              v-tooltip:bottom-end="'Delete the trigger'"
              :__title="'Delete the trigger'"
              @click="deleteTrigger(item)"
            /> -->
          </td>
        </tr>
      </template>

      <template v-slot:no-data>
        <v-alert type="info" text="No triggers defined" class="ma-2" />
      </template>
    </v-data-table>

    <v-alert
      v-else-if="!triggerStore.loading"
      type="info"
      text="No triggers defined"
    />

    <v-progress-circular v-else indeterminate class="ma-4" />

    <!-- Triggers Details Dialog -->
    <v-dialog v-model="showDetails" max-width="1200px">
      <v-card v-if="selectedTrigger">
        <!-- v-card-title>
          {{ selectedTrigger.name || selectedTrigger.id }}
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="showDetails = false" />
        </v-card-title -->
        <v-card-text>
          <v-alert
            v-if="selectedTrigger.name"
            type="info"
            :text="selectedTrigger.name"
            class="mb-4"
          />
          <JsonToHtmlTable
            :data="pruneTriggerDetails(selectedTrigger)"
            :showDataType="false"
            :showKey="false"
          />
          <!-- pre class="trigger-json">{{ JSON.stringify(selectedTrigger, null, 2) }}</pre -->
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import { useAuthStore } from '@/stores/auth';
import { useTriggerStore } from '@/stores/triggers';
import JsonToHtmlTable from '@/components/JsonToHtmlTable.vue';
import 'vue-json-to-html-table/dist/style.css';

export default {
  name: 'TriggerList',
  components: {
    JsonToHtmlTable,
  },
  data() {
    return {
      search: '',
      showDetails: false,
      selectedTrigger: null,
      itemsPerPage: 10,
      sortBy: [{ key: 'description', order: 'asc' }],

      headers: [
        {
          title: 'Trigger',
          key: 'description',
          sortable: true,
          align: 'start',
        },
        {
          title: 'Owner',
          key: 'owner',
          sortable: true,
          admins_only: true,
        },
        // {
        //   title: 'Event',
        //   key: 'type',
        //   sortable: true,
        // },
        // {
        //   title: 'Pipeline',
        //   key: 'pipeline',
        //   sortable: true,
        // },
        {
          title: 'Status',
          key: 'status',
          sortable: true,
          // admins_only: true,
        },
        {
          title: 'Enabled',
          key: 'enabled',
          sortable: true,
          admins_only: false,
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
    const triggerStore = useTriggerStore();
    return { authStore, triggerStore };
  },

  computed: {
    filteredTriggers() {
      if (!this.search) return this.triggerStore.triggers;
      const searchTerm = this.search.toLowerCase();
      return this.triggerStore.triggers.filter((trigger) => {
        return (
          //(trigger.name && trigger.name.toLowerCase().includes(searchTerm)) ||
          (trigger.description &&
            trigger.description.toLowerCase().includes(searchTerm)) ||
          //trigger.id.toLowerCase().includes(searchTerm)
          trigger.slug.toLowerCase().includes(searchTerm)
        );
      });
    },

    filteredHeaders() {
      // Do not display trigger properties restricted to admin users
      return this.headers.filter(
        (x) => !x.admins_only || this.authStore.isAdmin,
      );
    },
  },

  mounted() {
    this.refreshTriggers();
  },

  methods: {
    async refreshTriggers() {
      await this.triggerStore.fetchTriggers();
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

    pruneTriggerDetails(trigger) {
      const keysToKeep = [
        'slug',
        'description',
        'owner',
        'status',
        'enabled',
        'trigger_type_name',
        'pipeline_name',
        'cql2_filter',
        'params_default',
        'params_mapping',
      ];
      return Object.fromEntries(
        Object.entries(trigger).filter(([key]) => keysToKeep.includes(key)),
      );
    },

    viewTriggerDetails(trigger) {
      this.selectedTrigger = trigger;
      this.showDetails = true;
    },

    editTrigger(trigger) {
      this.selectedTrigger = trigger;
      this.showDetails = true;
    },

    deleteTrigger(trigger) {
      this.selectedTrigger = trigger;
      this.showDetails = true;
    },
  },
};
</script>

<style scoped>
.trigger-json {
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
