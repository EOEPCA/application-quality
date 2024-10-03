#!/usr/bin/env cwltool

cwlVersion: v1.0
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: cytopia/pylint
  InlineJavascriptRequirement: {}

inputs:
  source_directory:
    type: Directory
    inputBinding:
      position: 1
      valueFrom: $(inputs.source_directory.path + "/**/*.py")

outputs:
  pylint_report:
    type: File
    outputBinding:
      glob: pylint_report.json
stdout: pylint_report.json
arguments:
- --output-format=json
- --exit-zero
