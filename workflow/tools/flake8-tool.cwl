#!/usr/bin/env cwltool

cwlVersion: v1.0
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: eoepca/appquality-flake8-json:v0.1.0

inputs:
  source_directory:
    type: Directory
    inputBinding:
      position: 1

outputs:
  flake8_report:
    type: File
    outputBinding:
      glob: flake8_report.json
stdout: flake8_report.json

baseCommand: flake8
arguments:
- --format=json
