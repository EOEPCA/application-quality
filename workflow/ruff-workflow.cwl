#!/usr/bin/env cwltool
cwlVersion: v1.0
class: Workflow

inputs:
  name:
    type: string
    default: ruff
  pipeline_id:
    type: string
  repo_path:
    type: Directory
  run_id:
    type: string
  server_url:
    type: string

outputs:
  ruff_report:
    type: File
    outputSource: ruff_step/ruff_report

steps:
  ruff_step:
    in:
      source_directory: repo_path
    run: tools/ruff-tool.cwl
    out:
    - ruff_report
  save_ruff_step:
    in:
      name: name
      pipeline_id: pipeline_id
      report: ruff_step/ruff_report
      run_id: run_id
      server_url: server_url
    run: tools/save-tool.cwl
    out: []
