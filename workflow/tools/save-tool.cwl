#!/usr/bin/env cwltool

cwlVersion: v1.0
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: curlimages/curl
  InlineJavascriptRequirement: {}

inputs:
  report:
    type: File
  run_id:
    type: string
  step_id:
    type: string

outputs: []

baseCommand: curl
arguments:
- prefix: -X
  valueFrom: POST
- prefix: -L
  valueFrom: |-
    $('http://127.0.0.1:8000/save/' + inputs.run_id + '/' + inputs.step_id + '_report.json')
- prefix: -H
  valueFrom: 'Content-Type: application/json'
- prefix: -d
  valueFrom: $('@' + inputs.report.path)
