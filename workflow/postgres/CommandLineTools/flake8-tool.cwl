- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: eoepca/appquality-flake8-json:v0.1.0
    InitialWorkDirRequirement:
      listing:
      - entryname: script.sh
        entry: |-
          cd $(inputs.source_directory.path)

          PARAMS="--format=$(inputs.output_format) --output-file=$HOME/$(inputs.output_file)"
          if [ "$(inputs.exit_zero)" == "true" ] ; then
            PARAMS="$PARAMS --exit-zero"
          fi
          if [ "$(inputs.verbose)" == "true" ] ; then
            PARAMS="$PARAMS -v"
          fi

          flake8 $PARAMS $(inputs.file_list.join(" "))
    InlineJavascriptRequirement: {}

  inputs:
    exit_zero:
      label: Exit with zero
      doc: Force Flake8 to use the exit status code 0 even if there are errors.
      type: boolean
      default: true
    file_list: string[]
    output_file:
      label: Output file
      doc: Redirect all output to the specified file.
      type: string
      default: flake8_report.json
    output_format:
      label: Output format
      doc: Select the formatter used to display errors to the user.
      type: string
      default: json
    source_directory: Directory
    verbose: boolean

  outputs:
    flake8_report:
      type: File
      outputBinding:
        glob: $(inputs.output_file)

  baseCommand: sh
  arguments:
  - script.sh
  id: flake8_tool