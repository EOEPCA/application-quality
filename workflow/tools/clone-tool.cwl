#!/usr/bin/env cwltool

cwlVersion: v1.0
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: alpine/git
  InlineJavascriptRequirement: {}

inputs:
  branch:
    type: string
  repo_url:
    type: string

outputs:
  repo_directory:
    type: Directory
    outputBinding:
      glob: $(inputs.repo_url.split('/').pop().replace('.git',''))

baseCommand: git
arguments:
- clone
- $(inputs.repo_url)
- -b
- $(inputs.branch)
