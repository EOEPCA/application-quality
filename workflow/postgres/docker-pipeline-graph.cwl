#!/usr/bin/env cwltool

$graph:
- class: Workflow

  requirements:
    SubworkflowFeatureRequirement: {}

  inputs:
    pipeline_id:
      type: string
      default: docker
    run_id: string
    server_url: string
    trivy_subworkflow.trivy.image: string

  outputs: []

  steps:
    trivy_subworkflow:
      in:
        pipeline_id: pipeline_id
        run_id: run_id
        server_url: server_url
        trivy.image: trivy_subworkflow.trivy.image
      run: '#trivy_subworkflow'
      out: []
  id: main
- class: Workflow

  inputs:
    name:
      type: string
      default: trivy
    pipeline_id: string
    run_id: string
    server_url: string
    trivy.image: string

  outputs: []

  steps:
    save_step:
      in:
        name: name
        pipeline_id: pipeline_id
        report: trivy_step/trivy_report
        run_id: run_id
        server_url: server_url
      run: '#save_tool'
      out: []
    trivy_step:
      in:
        image: trivy.image
      run: '#trivy_tool'
      out:
      - trivy_report
  id: trivy_subworkflow
- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: aquasec/trivy:latest

  inputs:
    image: string

  outputs:
    trivy_report:
      type: File
      outputBinding:
        glob: trivy_report.json

  baseCommand: trivy
  arguments:
  - image
  - prefix: -f
    valueFrom: json
  - prefix: -o
    valueFrom: trivy_report.json
  - $(inputs.image)
  id: trivy_tool
- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: curlimages/curl
    InlineJavascriptRequirement: {}

  inputs:
    name: string
    pipeline_id: string
    report: File
    run_id: string
    server_url: string

  outputs: []

  baseCommand: curl
  arguments:
  - prefix: -X
    valueFrom: POST
  - prefix: -L
    valueFrom: |-
      $('http://' + inputs.server_url + '/api/pipelines/' + inputs.pipeline_id + '/runs/' + inputs.run_id + '/jobreports/?name=' + inputs.name)
  - prefix: -H
    valueFrom: Content-Type:application/json
  - prefix: -d
    valueFrom: $('@' + inputs.report.path)
  id: save_tool
cwlVersion: v1.0
