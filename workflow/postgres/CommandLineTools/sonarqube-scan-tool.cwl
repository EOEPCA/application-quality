- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: sonarsource/sonar-scanner-cli
    EnvVarRequirement:
      envDef:
        SONAR_HOST_URL: $('http://' + inputs.sonarqube_server)
        SONAR_TOKEN: $(inputs.sonarqube_token)
    InlineJavascriptRequirement: {}

  inputs:
    sonarqube_project_key:
      type: string
    sonarqube_server:
      type: string
      default: sonarqube-sonarqube.sonarqube:9000
    sonarqube_token:
      type: string
    source_directory:
      type: Directory

  outputs:
    sonarqube_project_key:
      type: string
      outputBinding:
        glob:
        outputEval: $(inputs.sonarqube_project_key)
    sonarqube_server:
      type: string
      outputBinding:
        glob:
        outputEval: $(inputs.sonarqube_server)
    sonarqube_token:
      type: string
      outputBinding:
        glob:
        outputEval: $(inputs.sonarqube_token)

  baseCommand:
  - sonar-scanner
  arguments:
  - prefix: -D
    valueFrom: $('sonar.projectKey=' + inputs.sonarqube_project_key)
    separate: false
  - prefix: -D
    valueFrom: $('sonar.projectBaseDir=' + inputs.source_directory.path + '/../')
    separate: false
  - prefix: -X
  id: sonarqube_scan_tool
