- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: curlimages/curl
    InlineJavascriptRequirement: {}

  inputs:
    sonarqube_project_key:
      type: string
    sonarqube_project_name:
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
    sonarqube_server:
      type: string
      outputBinding:
        outputEval: $(inputs.sonarqube_server)
    sonarqube_token:
      type: string
      outputBinding:
        outputEval: $(inputs.sonarqube_token)

  baseCommand:
  - curl
  arguments:
  - prefix: -X
    valueFrom: POST
  - prefix: -L
    valueFrom: $('http://' + inputs.sonarqube_server + '/api/projects/create')
  - prefix: -u
    valueFrom: $(inputs.sonarqube_token + ':')
  - prefix: -d
    valueFrom: $('name=' + inputs.sonarqube_project_name)
  - prefix: -d
    valueFrom: $('project=' + inputs.sonarqube_project_key)
  id: sonarqube_create_project_tool
