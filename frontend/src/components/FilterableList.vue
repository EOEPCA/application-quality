<template>
  <v-card class="mx-auto">
    <!-- Search and Filter Section -->
    <v-card-title>
      <v-row align="center">
        <v-col cols="12" sm="6">
          <v-text-field
            v-model="searchQuery"
            prepend-inner-icon="mdi-magnify"
            label="Search"
            variant="outlined"
            density="compact"
            hide-details
            clearable
          />
        </v-col>
        <v-col cols="12" sm="6">
          <v-select
            v-model="selectedCategory"
            :items="categories"
            label="Category"
            variant="outlined"
            density="compact"
            hide-details
            clearable
          />
        </v-col>
      </v-row>
    </v-card-title>

    <!-- List Section -->
    <v-card-text>
      <v-list v-if="filteredItems.length">
        <v-list-item
          v-for="item in filteredItems"
          :key="item.id"
          :title="item.name"
          :subtitle="item.category"
        >
          <template v-slot:prepend>
            <v-avatar color="primary">
              {{ item.name.charAt(0) }}
            </v-avatar>
          </template>

          <template v-slot:append>
            <v-btn
              icon="mdi-dots-vertical"
              variant="text"
              @click="handleItemAction(item)"
            />
          </template>
        </v-list-item>
      </v-list>

      <v-alert
        v-else
        type="info"
        text="No items found matching your criteria"
      />
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'FilterableList',

  props: {
    items: {
      type: Array,
      required: true,
      default: () => [],
    },
  },

  data() {
    return {
      searchQuery: '',
      selectedCategory: null,
    };
  },

  computed: {
    // Get unique categories from items
    categories() {
      return [...new Set(this.items.map((item) => item.category))];
    },

    // Filter items based on search query and selected category
    filteredItems() {
      return this.items.filter((item) => {
        const matchesSearch =
          this.searchQuery === '' ||
          item.name.toLowerCase().includes(this.searchQuery.toLowerCase());

        const matchesCategory =
          !this.selectedCategory || item.category === this.selectedCategory;

        return matchesSearch && matchesCategory;
      });
    },
  },

  methods: {
    handleItemAction(item) {
      this.$emit('item-action', item);
    },
  },
};
</script>
