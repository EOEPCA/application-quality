#!/usr/bin/env cwltool

cwlVersion: v1.0
class: CommandLineTool

requirements:
  ShellCommandRequirement: {}
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing:
      - $(inputs.source_directory)

inputs:
  project_key:
    type: string
    default: EOEPCA-AQ-BB
    inputBinding:
      prefix: -Dsonar.projectKey=
      separate: false
  sonar_host_url:
    type: string
    default: http://localhost:9000
    inputBinding:
      prefix: -Dsonar.host.url=
      separate: false
  sonar_token:
    type: string
    inputBinding:
      prefix: -Dsonar.token=
      position: 2
      separate: false
  source_directory:
    type: Directory

outputs: []

baseCommand: sonar-scanner
arguments:
- prefix: -Dsonar.sources=
  valueFrom: $(inputs.source_directory.path)
  separate: false
- -Dsonar.scm.disabled=true
