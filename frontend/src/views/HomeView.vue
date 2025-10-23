<template>
  <div>
    <h2 class="text-h4 mb-4">
      <v-icon icon="mdi-home" size="x-small" class="mr-2" />
      Home
    </h2>
    <p>
      The Application Quality Service aims to support the evolution of
      scientific algorithms (processing workflows) from research projects to
      ones that can be utilised in a production environment. To achieve this,
      the Service provides tools for verifying non-functional requirements -
      including code quality, software development best practice for open
      reproducible science, and optimisation through performance testing.
    </p>
    <p style="padding-top: 1em">
      Read about the Service capabilities in the online
      <a target="_blank" :href="settings.user_manual__url">User Manual</a>.
    </p>
    <p v-if="settings.isGrafanaEnabled()" style="padding-top: 1em">
      Analyse the pipeline executions and reports in the interactive
      <a target="_blank" :href="settings.getGrafanaDashboardsURL()"
        >Dashboards</a
      >.
    </p>
    <!-- p v-else>
      The accompagying Dashboards tool has not been deployed or is not configured properly.
    </p -->
    <p style="padding-top: 1em">More links:</p>
    <v-list lines="one">
      <v-list-item>
        <a target="_blank" :href="settings.design__url"
          >Reference architecture</a
        >
      </v-list-item>
      <v-list-item>
        <a target="_blank" :href="settings.source__url">GitHub repository</a>
      </v-list-item>
    </v-list>
  </div>
</template>

<script>
import { useSettingsStore } from '@/stores/settings';

export default {
  name: 'HomeView',

  setup() {
    const settings = useSettingsStore();
    return { settings };
  },
};
</script>
