#!/usr/bin/env cwltool

cwlVersion: v1.0
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: flake8-json

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
