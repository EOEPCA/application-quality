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