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
        :loading="triggerStore.loadingTriggers"
      />
      <v-btn
        icon="mdi-pencil"
        size="small"
        class="mx-2"
        color="warning"
        :disabled="!canCreateTrigger()"
        v-tooltip:bottom-end="'Create a new trigger'"
        @click="createTrigger"
        :loading="triggerStore.loadingTriggers"
      />
    </v-card-title>

    <v-alert
      icon="mdi-check-bold"
      v-if="successMessage"
      :text="successMessage"
      type="success"
      closable
      @click:close="successMessage = null"
    />

    <v-alert
      v-if="triggerStore.listError"
      type="error"
      closable
    >
      <div class="text-pre-line">{{ triggerStore.listError }}</div>
    </v-alert>

    <!-- eslint-disable vue/no-v-model-argument -->
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
    <!-- eslint-enable vue/no-v-model-argument -->
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
          <td v-if="this.authStore.isAdmin">{{ item.owner_name }}</td>
          <!-- <td>{{ item.trigger_type_name || 'N/A' }}</td> -->
          <!-- <td>{{ item.pipeline_name || 'N/A' }}</td> -->
          <td _v-if="this.authStore.isAdmin">{{ item.status }}</td>
          <td _v-if="this.authStore.isAdmin">{{ item.enabled }}</td>
          <td>{{ item.event_count }}</td>
          <td class="text-right nowrap">
            <v-btn
              color="primary"
              variant="text"
              v-tooltip:bottom-end="'Trigger information'"
              @click="viewTriggerDetails(item)"
            >
              <v-icon size="26px"> mdi-information </v-icon>
            </v-btn>
            <v-btn
              color="primary"
              variant="text"
              v-tooltip:bottom-end="'Pipeline executions'"
              :disabled="item.event_count == 0"
              @click="viewPipelineExecutions(item)"
            >
              <v-icon> mdi-monitor-eye </v-icon>
            </v-btn>
            <!-- Dropdown menu with extra actions: edit, delete -->
            <v-menu location="bottom end" :disabled="!canEditTrigger(item)">
              <template v-slot:activator="{ props }">
                <v-btn
                  v-bind="props"
                  variant="text"
                  :disabled="!canEditTrigger(item)"
                >
                  <v-icon> mdi-dots-vertical </v-icon>
                </v-btn>
              </template>

              <v-list>
                <v-list-item
                  @click="editTrigger(item)"
                  :disabled="!canEditTrigger(item)"
                >
                  <template v-slot:prepend>
                    <v-icon color="warning" icon="mdi-pencil" />
                  </template>
                  <v-list-item-title
                    v-tooltip:bottom-end="'Edit trigger ' + item.name"
                    >Edit</v-list-item-title
                  >
                </v-list-item>

                <!-- <v-list-item
                  v-if="this.authStore.isAdmin"
                  @click="changeTriggerOwner(item)"
                  :disabled="true"
                >
                  <template v-slot:prepend>
                    <v-icon color="warning" icon="mdi-account-edit" />
                  </template>
                  <v-list-item-title
                    v-tooltip:bottom-end="'Change the trigger owner'"
                    >Change Owner</v-list-item-title
                  >
                </v-list-item> -->

                <v-list-item
                  @click="deleteTrigger(item)"
                  :disabled="!canDeleteTrigger(item)"
                >
                  <template v-slot:prepend>
                    <v-icon color="error" icon="mdi-delete" />
                  </template>
                  <v-list-item-title
                    v-tooltip:bottom-end="'Delete this trigger'"
                    >Delete</v-list-item-title
                  >
                </v-list-item>
              </v-list>
            </v-menu>
          </td>
        </tr>
      </template>

      <template v-slot:no-data>
        <v-alert type="info" text="No triggers defined" class="ma-2" />
      </template>
    </v-data-table>

    <v-alert
      v-else-if="!triggerStore.loadingTriggers"
      type="info"
      text="No triggers defined"
    />

    <v-progress-circular v-else indeterminate class="ma-4" />

    <!-- Triggers Details Dialog -->
    <v-dialog v-model="showDetails" max-width="1200px">
      <v-card v-if="selectedTrigger">
        <v-card-text>
          <v-alert
            v-if="selectedTrigger.slug"
            type="info"
            :text="selectedTrigger.slug"
            class="mb-4"
          />
          <JSONTableViewer
            :data="pruneTriggerDetails(selectedTrigger)"
            :dont-convert="['cql2_filter', 'params_default', 'params_mapping']"
            :key-order="['name', 'description', 'owner_name', 'status', 'enabled', 'pipeline_name', 'trigger_type_name', 'event_count']"
          />
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Trigger creation drawer component -->
    <trigger-creation-panel
      v-model="creationParameters"
      :visible="this.creationPanelVisible"
      @creation-submitted="handleCreationSubmitted"
      @creation-cancelled="hideCreationPanel"
      @edition-submitted="handleEditSubmitted"
      @edition-cancelled="hideCreationPanel"
    />

    <!-- Trigger Delete Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="800px">
      <v-card v-if="selectedTrigger">
        <v-card-text>
          <v-alert
            type="warning"
            icon="mdi-delete"
            text="Delete Trigger"
            class="mb-4"
            style="font-size: 1.25rem"
          />
          Are you sure you want to delete the trigger definition "<span
            class="font-weight-bold"
            >{{ selectedTrigger?.slug }}</span
          >"?
          <div class="font-weight-light">
            {{ selectedTrigger?.description }}
          </div>
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
            :loading="deletingTrigger"
            @click="confirmDeleteTrigger(selectedTrigger)"
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
import { usePipelineStore } from '@/stores/pipelines';
import { useTriggerStore } from '@/stores/triggers';
import JSONTableViewer from '@/components/JSONTableViewer.vue';
import TriggerCreationPanel from './TriggerCreationPanel.vue';

export default {
  name: 'TriggerList',
  components: {
    JSONTableViewer,
    TriggerCreationPanel,
  },
  data() {
    return {
      search: '',
      showDetails: false,
      selectedTrigger: null,
      creationPanelVisible: false,
      creationParameters: {},
      successMessage: null,
      showDeleteDialog: false,
      deletingTrigger: false,
      itemsPerPage: 10,
      // Contains the default/current sorting parameters
      sortBy: [{ key: 'slug', order: 'asc' }],

      headers: [
        {
          title: 'Trigger',
          key: 'slug',
          sortable: true,
          align: 'start',
          sort: this.customTriggerSort,
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
          title: 'Events',
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
    };
  },

  setup() {
    const authStore = useAuthStore();
    const pipelineStore = usePipelineStore();
    const triggerStore = useTriggerStore();
    return { authStore, pipelineStore, triggerStore };
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
      await this.pipelineStore.fetchPipelines();
      await this.triggerStore.fetchTriggers();
    },

    customTriggerSort(slugA, slugB) {
      // The function receives values, not rows, so searching for the rows ...
      const rowA = this.triggerStore.triggers.find(item => item.slug === slugA);
      const rowB = this.triggerStore.triggers.find(item => item.slug === slugB);
      // console.debug("Custom trigger sort:", slugA, slugB, rowA, rowB);
      if (!rowA || !rowB) return 0
      const typeComp = (rowA.trigger_type_name || '').localeCompare(rowB.trigger_type_name || '');
      if (typeComp != 0) return typeComp;
      const pipelineComp = (rowA.pipeline_name || '').localeCompare(rowB.pipeline_name || '');
      if (pipelineComp != 0) return pipelineComp;
      const descComp = (rowA.description || '').localeCompare(rowB.description || '');
      return descComp;
    },

    canCreateTrigger() {
      // Any authenticated user has the right to create triggers
      return this.authStore.username != undefined;
    },

    canEditTrigger(trigger) {
      // Check if the user is either an admin or the owner of the trigger
      return (
        this.authStore.username != null &&
        (this.authStore.isAdmin ||
          this.authStore.username == trigger.owner)
      );
    },

    canDeleteTrigger(trigger) {
      // Check if the user is either an admin or the owner of the trigger
      return (
        this.authStore.username != null &&
        (this.authStore.isAdmin ||
          this.authStore.username == trigger.owner)
      );
    },

    pruneTriggerDetails(trigger) {
      const keysToKeep = [
        'slug',
        'description',
        'owner_name',
        'status',
        'event_count',
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

    viewPipelineExecutions(trigger) {
      // Store the selected trigger in the store so it is accessible by the executions page
      // Navigate to the executions page
      this.triggerStore.selectedTriggerId = trigger.slug;
      this.$router.push('/executions?trigger=' + trigger.slug);
    },

    createTrigger() {
      console.log('Create a new trigger ...');
      this.refreshTriggers();
      console.debug('Trigger types', this.triggerStore.triggerTypes)
      console.debug('Pipelines', this.pipelineStore.pipelines)
      
      this.creationParameters = {
        isUserAdmin: this.authStore.isAdmin,
        description: "",
        owner: this.authStore.details.id,  // The current user. Only admins may change the value.
        owner_name: this.authStore.username,
        status: "Testing",
        enabled: true,
        cql2Filter: {},
        paramsDefault: {},
        paramsMapping: {},
        availableTypes: this.triggerStore.triggerTypes,
        availablePipelines: this.pipelineStore.pipelines,
        // Statuses are enforced in the backend DB model (see the Trigger Model definition)
        availableStatus: ['Disabled', 'Testing', 'Restricted', 'Enabled'],  // 'Deleted'
        isCreation: true,
      };
      this.creationPanelVisible = true;
    },

    hideCreationPanel() {
      console.log('Cancel trigger creation/edit');
      this.creationPanelVisible = false;
    },

    handleCreationSubmitted(trigger) {
      // Handle the creation of the new trigger
      if (trigger == undefined) {
        console.error('Failed to create the trigger:', trigger);

      }
      console.log('Trigger created:', trigger);
      // Close the trigger creation panel
      this.creationPanelVisible = false;
      this.refreshTriggers();
      // Display a success message
      this.$notify({
        title: `Created trigger "${trigger.slug}"`,
        type: 'success',
      });
      this.$emit('trigger-created', trigger);
    },

    editTrigger(trigger) {
      console.log('Edit trigger ...', trigger);
      this.selectedTrigger = trigger;

      this.creationParameters = {
        isUserAdmin: this.authStore.isAdmin,
        name: trigger.slug,
        description: trigger.description,
        // By default, the owner is the current user.
        // Only admins may change a trigger owner.
        owner: trigger.owner,
        owner_name: trigger.owner_name,
        status: trigger.status,
        enabled: trigger.enabled,
        triggerType: this.triggerStore.getTriggerTypeById(trigger.trigger_type),
        availableTypes: this.triggerStore.triggerTypes,
        pipeline: this.pipelineStore.pipelineById(trigger.pipeline),
        availablePipelines: this.pipelineStore.pipelines,
        cql2Filter: trigger.cql2_filter,
        paramsDefault: trigger.params_default,
        paramsMapping: trigger.params_mapping,
        isCreation: false,
        // Statuses are enforced in the backend DB model (see the Trigger Model definition)
        availableStatus: ['Disabled', 'Testing', 'Restricted', 'Enabled'],  // 'Deleted'
      };
      this.creationPanelVisible = true;
    },

    handleEditSubmitted(trigger) {
      // Handle the creation of the new trigger
      console.log('Trigger edited:', trigger);
      // Close the trigger creation panel
      this.creationPanelVisible = false;
      this.refreshTriggers();
      // Display a success message
      this.$notify({
        title: `Saved trigger "${trigger.slug}"`,
        type: 'success',
      });
      this.$emit('trigger-edited', trigger);
    },

    hideEditingPanel() {
      console.log('Cancel trigger editing');
      this.creationPanelVisible = false;
    },

    deleteTrigger(trigger) {
      console.log('Delete trigger:', trigger);
      this.selectedTrigger = trigger;
      this.showDeleteDialog = true;
    },

    async confirmDeleteTrigger(trigger) {
      this.deletingTrigger = true;
      try {
        await this.triggerStore.deleteTrigger(this.selectedTrigger);
        this.showDeleteDialog = false;
        // Display a success message
        this.$notify({
          title: `Deleted trigger "${trigger.slug}"`,
          type: 'success',
        });
        this.$emit('trigger-deleted', trigger);
        await this.refreshTriggers();
      } catch (error) {
        this.$notify({
          title: `Failed to delete trigger "${trigger.slug}"`,
          text: error.message,
          type: 'error',
        });
        console.log('Failed to delete the trigger: ', error.message);
      } finally {
        this.deletingTrigger = false;
      }
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

.v-icon {
  font-size: 26px;
  min-width: 30px;
}

.nowrap {
  white-space: nowrap;
}
</style>
