- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: ghcr.io/astral-sh/ruff:alpine
    InitialWorkDirRequirement:
      listing:
      - entryname: script.sh
        entry: |-
          cd $(inputs.source_directory.path)

          PARAMS="--output-format $(inputs.output_format) -o $HOME/$(inputs.output_file)"
          if [ "$(inputs.exit_zero)" == "true" ] ; then
            PARAMS="$PARAMS -e"
          fi
          if [ "$(inputs.no_cache)" == "true" ] ; then
            PARAMS="$PARAMS -n"
          fi
          if [ "$(inputs.verbose)" == "true" ] ; then
            PARAMS="$PARAMS -v"
          fi

          ruff check $PARAMS $(inputs.file_list.join(" "))
    InlineJavascriptRequirement: {}

  inputs:
    exit_zero:
      label: Exit with zero
      doc: Exit with status code "0", even upon detecting lint violations.
      type: boolean
      default: true
    no_cache:
      label: Disable cache
      doc: Disable cache reads.
      type: boolean
      default: true
    file_list: string[]
    output_file:
      label: Output file
      doc: Specify file to write the linter output to.
      type: string
      default: ruff_report.json
    output_format:
      label: Output format
      doc: |-
        Output serialization format for violations. Possible values: concise, full, json, json-lines, junit, grouped, github, gitlab, pylint, rdjson, azure, sarif.
      type: string
      default: json
    source_directory: Directory
    verbose: boolean

  outputs:
    ruff_report:
      type: File
      outputBinding:
        glob: $(inputs.output_file)

  baseCommand: sh
  arguments:
  - script.sh
  id: ruff_tool