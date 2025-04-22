- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: curlimages/curl
    InlineJavascriptRequirement: {}

  inputs:
    sonarqube_project_key:
      type: string
    sonarqube_server:
      type: string
      default: sonarqube-sonarqube.sonarqube:9000
    sonarqube_token:
      type: string

  outputs:
    sonarqube_project_key:
      type: string
      outputBinding:
        outputEval: $(inputs.sonarqube_project_key)
    sonarqube_report:
      type: File
      outputBinding:
        glob: sonarqube_report.json
    sonarqube_server:
      type: string
      outputBinding:
        outputEval: $(inputs.sonarqube_server)
    sonarqube_token:
      type: string
      outputBinding:
        outputEval: $(inputs.sonarqube_token)
  stdout: sonarqube_report.json

  baseCommand:
  - curl
  arguments:
  - prefix: -L
    valueFrom: |-
      $('http://' + inputs.sonarqube_server + '/api/issues/search?components=' + inputs.sonarqube_project_key)
  - prefix: -u
    valueFrom: $(inputs.sonarqube_token + ':')
  id: sonarqube_get_report_tool
