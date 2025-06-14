import { defineStore } from 'pinia';
import { settingsService } from '@/services/settings';
import { removeTrailingSlashes } from '@/assets/tools';

// TODO: When the end-point is working, set to default values null, false, true, ...
export const useSettingsStore = defineStore('settings', {
  state: () => ({
    instance__name: 'EOEPCA - Application Quality Service',
    instance__version: '1.0',
    instance__date: 'yyyy-mm-dd',
    instance__theme: 'default',
    user_manual__url:
      'https://eoepca.readthedocs.io/projects/application-quality/en/latest/usage/user-manual/',
    source__url: 'https://github.com/EOEPCA/application-quality/',
    deployment_guide__url: '',
    design__url:
      'https://eoepca.readthedocs.io/projects/architecture/en/latest/reference-architecture/application-quality-BB/',
    sso__enabled: true,
    workspace__enabled: false,
    grafana__enabled: true,
    grafana__url: 'http://eoepca-plus-testing:3000',
    grafana__pipeline_executions__path:
      '/d/pipeline-executions/pipeline-executions?from=now-90d&to=now',
    grafana__pipeline_execution__path:
      '/d/pipeline-execution/pipeline-execution?var-execution_id={execution_id}&var-pipeline_id={pipeline_name}',
    grafana__pipeline_execution_report__path:
      '/d/default-{tool_name}-report/{tool_name}-report?var-pipeline_id={pipeline_name}&var-execution_id={execution_id}&var-report_id={report_id}&var-tool_name={tool_name}',
    settingsReceived: false,
  }),

  actions: {
    async fetchSettings() {
      this.loading = true;
      this.error = null;
      try {
        const settings = await settingsService.getSettings();
        for (const key in settings) {
          // Ensure the property belongs to the settings object itself
          if (Object.prototype.hasOwnProperty.call(settings, key)) {
            this[key] = settings[key].replaceAll('.', '__');
          }
        }
        // Ensure the Grafana URL does not end with a '/'
        this.grafana__url = removeTrailingSlashes(this.grafana__url);
        this.settingsReceived = true;
      } catch (error) {
        this.error = error.message;
        this.settingsReceived = false;
      } finally {
        this.loading = false;
      }
    },

    isGrafanaEnabled() {
      // Return true or false
      return this.grafana__enabled == true;
    },

    checkGrafanaEnabled() {
      // Throw an exception if false
      if (this.grafana__enabled == false) {
        console.error('Error: Grafana is not enabled');
        throw 'Error: Grafana is not enabled';
      }
    },

    getGrafanaDashboardsURL() {
      this.checkGrafanaEnabled();
      return this.grafana__url;
    },

    getGrafanaPipelineExecutionsURL() {
      this.checkGrafanaEnabled();
      return this.grafana__url + this.grafana__pipeline_executions__path;
    },

    getGrafanaPipelineExecutionURL(pipeline_name, execution_id) {
      this.checkGrafanaEnabled();
      var url = this.grafana__url + this.grafana__pipeline_execution__path;
      return url
        .replaceAll('{pipeline_name}', pipeline_name)
        .replaceAll('{execution_id}', execution_id);
    },

    getGrafanaPipelineExecutionReportURL(
      pipeline_name,
      execution_id,
      tool_name,
      report_id,
    ) {
      this.checkGrafanaEnabled();
      var url =
        this.grafana__url + this.grafana__pipeline_execution_report__path;
      url = url
        .replaceAll('{pipeline_name}', pipeline_name)
        .replaceAll('{execution_id}', execution_id);
      return url
        .replaceAll('{tool_name}', tool_name)
        .replaceAll('{report_id}', report_id);
    },
  },
});
