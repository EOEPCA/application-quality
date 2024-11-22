#!/usr/bin/env cwltool

cwlVersion: v1.0
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: curlimages/curl
  InlineJavascriptRequirement: {}

inputs:
  name:
    type: string
  pipeline_id:
    type: string
  report:
    type: File
  run_id:
    type: string
  server_url:
    type: string

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
