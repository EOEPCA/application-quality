- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: cytopia/pylint
    InitialWorkDirRequirement:
      listing:
      - entryname: script.sh
        entry: |-
          cd $(inputs.source_directory.path)

          PARAMS="--output-format=$(inputs.output_format) --output=$HOME/$(inputs.output_file) --disable=$(inputs.disable)"
          if [ "$(inputs.exit_zero)" == "true" ] ; then
            PARAMS="$PARAMS --exit-zero"
          fi
          if [ "$(inputs.errors_only)" == "true" ] ; then
            PARAMS="$PARAMS -E"
          fi
          if [ "$(inputs.verbose)" == "true" ] ; then
            PARAMS="$PARAMS -v"
          fi

          pylint $PARAMS $(inputs.file_list.join(" "))
    InlineJavascriptRequirement: {}

  inputs:
    disable: string
    errors_only: boolean
    exit_zero:
      doc: |-
        Always return a 0 (non-error) status code, even if lint errors are found. This is primarily useful in continuous integration scripts.
      type: boolean
      default: true
    file_list: string[]
    output_file:
      doc: Specify an output file.
      type: string
      default: pylint_report.json
    output_format:
      doc: |-
        Set the output format. Available formats are: text, parseable, colorized, json2 (improved json format), json (old json format) and msvs (visual studio). You can also give a reporter class, e.g. mypackage.mymodule.MyReporterClass.
      type: string
      default: json
    source_directory: Directory
    verbose: boolean

  outputs:
    pylint_report:
      type: File
      outputBinding:
        glob: $(inputs.output_file)

  baseCommand: sh
  arguments:
  - script.sh
  id: pylint_tool