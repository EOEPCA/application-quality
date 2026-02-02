import { defineStore } from 'pinia';
import { pipelineService } from '@/services/pipelines';

export const usePipelineStore = defineStore('pipeline', {
  state: () => ({
    pipelines: [],
    executions: [],
    reports: [],
    loadingPipelines: false,
    loadingExecutions: false,
    loadingReports: false,
    selectedPipelineId: null,
    selectedExecutionId: null,
    selectedReport: null,
    error: null,
  }),

  actions: {
    async fetchPipelines() {
      this.loading = true;
      this.error = null;
      try {
        this.pipelines = await pipelineService.getPipelines();
        // Use user Id as user name if missing
        this.pipelines = this.pipelines.map((pipeline) => {
          if (!pipeline.owner_name && pipeline.owner) {
            return { ...pipeline, owner_name: pipeline.owner };
          }
          return pipeline;
        });
      } catch (error) {
        const msg_prefix = 'Error fetching pipelines: ';
        if (error.response?.data?.detail) {
          console.error(msg_prefix, error, error.response.data.detail);
          this.error = msg_prefix + error.response.data.detail;
        } else {
          console.error(msg_prefix, error);
          this.error = msg_prefix + error.message;
        }
      } finally {
        this.loadingPipelines = false;
      }
    },

    async fetchPipelineById(id) {
      this.loadingPipelines = true;
      this.error = null;
      try {
        const pipeline = await pipelineService.getPipelineById(id);
        const index = this.pipelines.findIndex((p) => p.id === id);
        if (index !== -1) {
          this.pipelines[index] = pipeline;
        } else {
          this.pipelines.push(pipeline);
        }
      } catch (error) {
        const msg_prefix = 'Error fetching pipeline: ';
        if (error.response?.data?.detail) {
          console.error(msg_prefix, error, error.response.data.detail);
          this.error = msg_prefix + error.response.data.detail;
        } else {
          console.error(msg_prefix, error);
          this.error = msg_prefix + error.message;
        }
      } finally {
        this.loadingPipelines = false;
      }
    },

    async fetchPipelineExecutions(id) {
      this.loadingExecutions = true;
      this.error = null;
      try {
        this.executions = await pipelineService.getPipelineExecutions(id);
        // console.log('Executions:', this.executions);
      } catch (error) {
        const msg_prefix = 'Error fetching pipeline executions: ';
        if (error.response?.data?.detail) {
          console.error(msg_prefix, error, error.response.data.detail);
          this.error = msg_prefix + error.response.data.detail;
        } else {
          console.error(msg_prefix, error);
          this.error = msg_prefix + error.message;
        }
      } finally {
        this.loadingExecutions = false;
      }
    },

    async fetchPipelineExecutionReports(pipelineId, runId) {
      this.loadingReports = true;
      this.error = null;
      try {
        this.reports = await pipelineService.getPipelineExecutionReports(
          pipelineId,
          runId,
        );
        // console.log('Reports:', this.reports);
      } catch (error) {
        const msg_prefix = 'Error fetching pipeline execution reports: ';
        if (error.response?.data?.detail) {
          console.error(msg_prefix, error, error.response.data.detail);
          this.error = msg_prefix + error.response.data.detail;
        } else {
          console.error(msg_prefix, error);
          this.error = msg_prefix + error.message;
        }
      } finally {
        this.loadingReports = false;
      }
    },

    async createPipeline(pipeline) {
      console.log('Create pipeline:', pipeline.name, pipeline);
      this.loading = true;
      this.error = null;
      try {
        const response = await pipelineService.createPipeline(pipeline);
        this.fetchPipelines();
        this.loadingPipelines = false;
        return response;
      } catch (error) {
        const msg_prefix = 'Error creating pipeline ' + pipeline.name + ': ';
        if (error.response?.data?.detail) {
          console.error(msg_prefix, error, error.response.data.detail);
          this.error = msg_prefix + error.response.data.detail;
        } else {
          console.error(msg_prefix, error);
          this.error = msg_prefix + error.message;
        }
      } finally {
        this.loadingPipelines = false;
      }
    },

    async updatePipeline(pipeline) {
      console.log('Update pipeline:', pipeline.name, pipeline);
      this.loading = true;
      this.error = null;
      try {
        const response = await pipelineService.updatePipeline(pipeline);
        this.fetchPipelines();
        this.loadingPipelines = false;
        return response;
      } catch (error) {
        const msg_prefix = 'Error updating pipeline ' + pipeline.name + ': ';
        if (error.response?.data?.detail) {
          console.error(msg_prefix, error, error.response.data.detail);
          this.error = msg_prefix + error.response.data.detail;
        } else {
          console.error(msg_prefix, error);
          this.error = msg_prefix + error.message;
        }
      } finally {
        this.loadingPipelines = false;
      }
    },

    async executePipeline(pipeline, inputs) {
      console.log('Execute pipeline:', pipeline.name, pipeline, inputs);
      this.loading = true;
      this.error = null;
      try {
        const response = await pipelineService.executePipeline(
          pipeline.id,
          inputs,
        );
        this.fetchPipelines();
        this.loadingPipelines = false;
        return response;
      } catch (error) {
        const msg_prefix = 'Error executing pipeline ' + pipeline.name + ': ';
        if (error.response?.data?.detail) {
          console.error(msg_prefix, error, error.response.data.detail);
          this.error = msg_prefix + error.response.data.detail;
        } else {
          console.error(msg_prefix, error);
          this.error = msg_prefix + error.message;
        }
        throw error;
      } finally {
        this.loadingPipelines = false;
      }
    },

    executionById(id) {
      if (!this.executions) this.refreshPipelineExecutions();
      const executions = this.executions.filter((execution) => {
        return execution.id == id;
      });
      // console.debug('Executions with id:', id, executions);
      if (executions) return executions[0];
      return null;
    },

    pipelineById(id) {
      // console.debug('Pipelines in store:', this.pipelines);
      if (id == null || id == undefined) id = this.selectedPipelineId;
      if (id == null || id == undefined) {
        console.warn('Bad request: not pipeline Id provided');
        return null;
      }
      const pipelines = this.pipelines.filter((pipeline) => {
        return pipeline.id == id;
      });
      // console.debug('Pipelines with id:', id, pipelines);
      if (pipelines.length != 0) {
        return pipelines[0];
      }
      console.log('Pipeline with id not found:', id);
      return null;
    },

    selectedExecution() {
      return this.executionById(this.selectedExecutionId);
    },

    selectedPipeline() {
      return this.pipelineById(this.selectedPipelineId);
    },

    async deletePipeline(id) {
      console.log('Delete pipeline with Id:', id);
      this.loading = true;
      this.error = null;
      try {
        await pipelineService.deletePipeline(id);
      } catch (error) {
        const msg_prefix = 'Error deleting pipeline ' + id + ': ';
        if (error.response?.data?.detail) {
          console.error(msg_prefix, error, error.response.data.detail);
          this.error = msg_prefix + error.response.data.detail;
        } else {
          console.error(msg_prefix, error);
          this.error = msg_prefix + error.message;
        }
      } finally {
        this.fetchPipelines();
        this.loadingPipelines = false;
      }
    },
  },
});
