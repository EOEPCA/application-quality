#!/usr/bin/env cwltool

cwlVersion: v1.0
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: alpine/git
  InlineJavascriptRequirement: {}

inputs:
  repo_url:
    type: string
    inputBinding:
      position: 1

outputs:
  repo_directory:
    type: Directory
    outputBinding:
      glob: $(inputs.repo_url.split('/').pop().replace('.git',''))
arguments:
- clone
