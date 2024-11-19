#!/usr/bin/env cwltool

cwlVersion: v1.0
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: ghcr.io/astral-sh/ruff:alpine
  InlineJavascriptRequirement: {}

inputs:
  source_directory:
    type: Directory
    inputBinding:
      position: 1

outputs:
  ruff_report:
    type: File
    outputBinding:
      glob: ruff_report.json

baseCommand:
- ruff
- check
arguments:
- --exclude
- .git
- --output-format
- json
- -o
- ruff_report.json
- -en
