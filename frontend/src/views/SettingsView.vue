<template>
  <div>
    <h2 class="text-h4 mb-4">
      <v-icon icon="mdi-cog" size="x-small" class="mr-2" />Settings
    </h2>
    <p>Instance name: {{ settings.instance__name }}</p>
    <p>Version: {{ settings.instance__version }}</p>
    <p>Date: {{ settings.instance__date }}</p>

    <p v-if="settings.isGrafanaEnabled() == true">Grafana powered 
      <a target="_blank" :href="settings.getGrafanaDashboardsURL()"
        >Dashboards</a
      >
    </p>
    <p v-if="settings.isDebugEnabled() == true">
      <a target="_blank" :href="settings.getGrafanaPipelineExecutionsURL()"
        >Grafana Dashboards Pipeline executions</a
      >
    </p>
    <p v-if="settings.isDebugEnabled() == true">
      <a
        target="_blank"
        :href="settings.getGrafanaPipelineExecutionURL('Python pipeline', 38)"
        >Grafana Dashboards Pipeline execution 38</a
      >.
    </p>
    <p v-if="settings.isDebugEnabled() == true">
      <a
        target="_blank"
        :href="
          settings.getGrafanaPipelineExecutionReportURL(
            'Python pipeline',
            38,
            'ruff',
            35,
          )
        "
        >Grafana Dashboards Pipeline execution report 35</a
      >.
    </p>
  </div>
</template>

<script>
import { useSettingsStore } from '@/stores/settings';

export default {
  name: 'SettingsView',

  setup() {
    const settings = useSettingsStore();
    return { settings };
  },
};
</script>