- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: nexus.spaceapplications.com/repository/docker-eoepca/ap_validator:2025-03-05.1
    InitialWorkDirRequirement:
      listing:
      - entryname: script.sh
        entry: |-
          cd $(inputs.source_directory.path)

          ap-validator \\
              --format json \\
              --detail '$(inputs.detail)' \\
              --entry-point '$(inputs.entry_point)' \\
              '$(inputs.file_path)' > ~/ap_validator_report.json

          exit 0
    InlineJavascriptRequirement: {}

  inputs:
    file_path: string
    source_directory: Directory
    detail: string
    entry_point: string

  outputs:
    ap_validator_report:
      type: File
      outputBinding:
        glob: ap_validator_report.json

  baseCommand: sh
  arguments:
  - script.sh
  id: ap_validator_tool