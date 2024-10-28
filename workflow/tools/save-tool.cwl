#!/usr/bin/env cwltool

cwlVersion: v1.0
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: curlimages/curl
  InlineJavascriptRequirement: {}

inputs:
  server_url:
    type: string
  pipeline_id:
    type: string
  run_id:
    type: string
  step_id:
    type: string
  report:
    type: File

outputs: []

baseCommand: curl
arguments:
- prefix: -X
  valueFrom: POST
- prefix: -L
  valueFrom: |-
    $('http://' + inputs.server_url + '/save/' + inputs.pipeline_id + '-' + inputs.run_id + '/' + inputs.step_id + '_report.json')
- prefix: -H
  valueFrom: Content-Type:application/json
- prefix: -d
  valueFrom: $('@' + inputs.report.path)
