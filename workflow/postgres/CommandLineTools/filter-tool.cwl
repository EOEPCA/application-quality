- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: alpine:latest
    InitialWorkDirRequirement:
      listing:
      - entryname: script.sh
        entry: |-
          cd $(inputs.source_directory.path)
          find . -type f -regex "$(inputs.regex)" > $HOME/filter.out
    InlineJavascriptRequirement: {}

  inputs:
    regex: string
    source_directory: Directory

  outputs:
    file_list:
      type: string[]
      outputBinding:
        glob: filter.out
        outputEval: |-
          $(self[0].contents.split('\n').filter(function(line) {return line.trim() !== '';}))
        loadContents: true

  baseCommand: sh
  arguments:
  - script.sh
  id: filter_tool