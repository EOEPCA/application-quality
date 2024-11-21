#!/usr/bin/env cwltool

cwlVersion: v1.0
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: cytopia/bandit
  InlineJavascriptRequirement: {}

inputs:
  source_directory:
    type: Directory
    inputBinding:
      position: 1

outputs:
  bandit_report:
    type: File
    outputBinding:
      glob: bandit_report.json

baseCommand:
- bandit
arguments:
- -x
- .git
- -f
- json
- -o
- bandit_report.json
- --exit-zero
