- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: cytopia/bandit
    InitialWorkDirRequirement:
      listing:
      - entryname: script.sh
        entry: |-
          cd $(inputs.source_directory.path)

          PARAMS="-f $(inputs.output_format) -o $HOME/$(inputs.output_file)"
          if [ "$(inputs.exit_zero)" == "true" ] ; then
            PARAMS="$PARAMS --exit-zero"
          fi
          if [ "$(inputs.verbose)" == "true" ] ; then
            PARAMS="$PARAMS -v"
          fi

          bandit $PARAMS $(inputs.file_list.join(" "))
    InlineJavascriptRequirement: {}

  inputs:
    exit_zero:
      label: Exit with zero
      doc: Exit with 0, even with results found.
      type: boolean
      default: true
    file_list: string[]
    output_file:
      label: Output file
      doc: Write report to filename.
      type: string
      default: bandit_report.json
    output_format:
      label: Output format
      doc: Specify output format.
      type: string
      default: json
    source_directory: Directory
    verbose: boolean

  outputs:
    bandit_report:
      type: File
      outputBinding:
        glob: $(inputs.output_file)

  baseCommand: sh
  arguments:
  - script.sh
  id: bandit_tool