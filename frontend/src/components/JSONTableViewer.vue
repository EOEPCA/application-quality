<!-- JSONTableViewer.vue -->
<template>
  <div class="json-table-wrapper">
    
    <!-- CASE 1: Object Grid -->
    <table v-if="isObject(data) && !Array.isArray(data)" class="ui-property-table">
    <tbody>
        <tr v-for="key in sortedKeys" :key="key" class="table-row">
        <!-- The key column (Will format normally now, e.g., "Cql2 Filter") -->
        <td class="property-key">{{ formatLabel(key) }}</td>
        
        <td class="property-value">
            <!-- Render the raw value directly if the key is in the dontConvert list -->
            <div v-if="dontConvert.includes(key)">
            <pre class="raw-value-block">{{ data[key] }}</pre>
            </div>
            <!-- Build the display recursively -->
            <div v-else-if="isObject(data[key])">
              <JSONTableViewer 
                :data="data[key]" 
                :dont-convert="dontConvert" 
                :key-order="keyOrder"
              />
            </div>
            <span v-else class="primitive-text">{{ formatPrimitive(data[key]) }}</span>
        </td>
        </tr>
    </tbody>
    </table>

    <!-- CASE 2: Array Grid -->
    <div v-else-if="Array.isArray(data)" class="ui-array-list">
      <div v-for="(item, index) in data" :key="index" class="array-item-card">
        <!-- div class="array-badge">Item #{{ index + 1 }}</div -->
        <div class="array-item-content">
          <div v-if="isObject(item)">
            <!-- Build the display recursively -->
            <JSONTableViewer 
              :data="item" 
              :dont-convert="dontConvert" 
              :key-order="keyOrder"
            />
          </div>
          <span v-else class="primitive-text">{{ formatPrimitive(item) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatDate } from '@/assets/tools';

const props = defineProps({
  data: {
    required: true
  },
  dontConvert: {
    type: Array,
    default: () => []
  },
  keyOrder: {
    type: Array,
    default: () => []
  },
})

const isObject = (val) => val !== null && typeof val === 'object'

// Computed property that organizes object keys based on the explicit keyOrder configuration
const sortedKeys = computed(() => {
  if (!props.data || typeof props.data !== 'object') return []
  const originalKeys = Object.keys(props.data)
  // 1. Extract keys that match your explicit configuration order
  const prioritized = props.keyOrder.filter(key => originalKeys.includes(key))
  // 2. Gather all remaining keys that weren't specified
  const remaining = originalKeys.filter(key => !props.keyOrder.includes(key))
  // 3. Merge them together (Prioritized keys first, followed by everything else)
  return [...prioritized, ...remaining]
})

const formatLabel = (key) => {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

const formatPrimitive = (val) => {
  if (typeof val === 'boolean') return val ? 'Yes' : 'No'

  // Display a dash character instead of null or undefined
  if (val === null || val === undefined) return '-'

  // If the value is a string, check if it matches an ISO date pattern
  if (typeof val === 'string') {
    // Regex matches: YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss.sssZ
    const isoDateRegex = /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?$/
    if (isoDateRegex.test(val)) {
      return formatDate(val)
    }
  }

  return val
}
</script>

<style scoped>
.json-table-wrapper {
  width: 100%;
}
.ui-property-table {
  width: 100%;
  border-collapse: collapse;
  margin: 2px 0;
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 2px;
}
.table-row {
  border-bottom: 1px solid #f0f0f0;
}
.table-row:last-child {
  border-bottom: none;
}
.property-key {
  width: 15%; /* Lower this percentage to shrink the first column */
  padding: 10px 14px;
  font-weight: 600;
  color: #374151;
  background-color: #f9fafb;
  vertical-align: top;
  font-size: 0.9rem;
  border-right: 1px solid #e0e0e0;
  /* Optional additions to keep text looking neat when squeezed: */
  white-space: nowrap;       /* Prevents words from wrapping to a new line */
  text-overflow: ellipsis;   /* Adds '...' if a key is exceptionally long */
  overflow: hidden;
}
.property-value {
  padding: 8px 12px;
  vertical-align: middle;
  font-size: 0.9rem;
  color: #1f2937;
}
.ui-array-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 6px 0;
}
.array-item-card {
  border: 1px solid #e5e7eb;
  border-radius: 2px;
  background-color: #fafafa;
  overflow: hidden;
}
.array-badge {
  background-color: #eceff1;
  color: #455a64;
  font-size: 0.75rem;
  font-weight: bold;
  padding: 4px 10px;
  text-transform: uppercase;
  border-bottom: 1px solid #e5e7eb;
}
.array-item-content {
  padding: 10px;
}
.primitive-text {
  display: inline-block;
  padding: 2px 0;
}
.property-value .ui-property-table {
  margin-top: 0px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
</style>