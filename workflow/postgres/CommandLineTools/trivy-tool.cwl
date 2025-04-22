- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: aquasec/trivy:latest

  inputs:
    image: string

  outputs:
    trivy_report:
      type: File
      outputBinding:
        glob: trivy_report.json

  baseCommand: trivy
  arguments:
  - image
  - prefix: -f
    valueFrom: json
  - prefix: -o
    valueFrom: trivy_report.json
  - $(inputs.image)
  id: trivy_tool