import { defineStore } from 'pinia'
import { pipelineService } from '@/services/pipelines'

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
    error: null
  }),

  actions: {
    async fetchPipelines() {
      this.loading = true
      this.error = null
      try {
        this.pipelines = await pipelineService.getPipelines()
      } catch (error) {
        this.error = error.message
      } finally {
        this.loadingPipelines = false
      }
    },

    async fetchPipelineById(id) {
      this.loadingPipelines = true
      this.error = null
      try {
        const pipeline = await pipelineService.getPipelineById(id)
        const index = this.pipelines.findIndex(p => p.id === id)
        if (index !== -1) {
          this.pipelines[index] = pipeline
        } else {
          this.pipelines.push(pipeline)
        }
      } catch (error) {
        this.error = error.message
      } finally {
        this.loadingPipelines = false
      }
    },

    async fetchPipelineExecutions(id) {
      this.loadingExecutions = true
      this.error = null
      try {
        this.executions = await pipelineService.getPipelineExecutions(id)
      } catch (error) {
        this.error = error.message
      } finally {
        this.loadingExecutions = false
      }
    },

    async fetchPipelineExecutionReports(pipelineId, runId) {
      this.loadingReports = true
      this.error = null
      try {
        this.reports = await pipelineService.getPipelineExecutionReports(pipelineId, runId)
      } catch (error) {
        this.error = error.message
      } finally {
        this.loadingReports = false
      }
    },

    executionById(id) {
      if (! this.executions)
        this.refreshPipelineExecutions()
      const executions = this.executions.filter(execution => {
        return (execution.id == id)
      })
      console.log(executions)
      if (executions)
        return executions[0]
      return null
    },

    pipelineById(id) {
      console.log("Pipelines in store:", this.pipelines)
      if (id == null || id == undefined)
        id = this.selectedPipelineId
      if (id == null || id == undefined) {
        console.log("Bad request: not pipeline Id provided")
        return null
      }
      const pipelines = this.pipelines.filter(pipeline => {
        return (pipeline.slug == id)
      })
      console.log("Pipelines with id:", id, pipelines)
      if (pipelines.length != 0) {
        return pipelines[0]
      }
      console.log("Pipeline with id not found:", id)
      return null
    },

    selectedExecution() {
      return this.executionById(this.selectedExecutionId)
    },

    selectedPipeline() {
      return this.pipelineById(this.selectedPipelineId)
    },
  }
})