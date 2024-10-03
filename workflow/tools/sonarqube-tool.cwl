#!/usr/bin/env cwltool

cwlVersion: v1.0
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: sonarsource/sonar-scanner-cli:latest
  InlineJavascriptRequirement: {}

inputs:
  project_key:
    type: string
    inputBinding:
      prefix: -Dsonar.projectKey=
      separate: false
  sonar_host_url:
    type: string
    inputBinding:
      prefix: -Dsonar.host.url=
      separate: false
  sonar_token:
    type: string
    inputBinding:
      prefix: -Dsonar.login=
      position: 2
      separate: false
  source_directory:
    type: Directory

outputs:
  sonar_report:
    type: File
    outputBinding:
      glob: sonar-report.json

baseCommand: sonar-scanner
arguments:
- prefix: -Dsonar.sources=
  valueFrom: $(inputs.source_directory.path)
  separate: false
- -Dsonar.report.export.path=sonar-report.json
- -Dsonar.scm.disabled=true
