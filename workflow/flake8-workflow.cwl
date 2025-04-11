#!/usr/bin/env cwltool
cwlVersion: v1.0
class: Workflow

inputs:
  name:
    type: string
    default: flake8
  pipeline_id:
    type: string
  repo_path:
    type: Directory
  run_id:
    type: string
  server_url:
    type: string

outputs:
  flake8_report:
    type: File
    outputSource: flake8_step/flake8_report

steps:
  flake8_step:
    in:
      source_directory: repo_path
    run: tools/flake8-tool.cwl
    out:
    - flake8_report
  save_flake8_step:
    in:
      name: name
      pipeline_id: pipeline_id
      report: flake8_step/flake8_report
      run_id: run_id
      server_url: server_url
    run: tools/save-tool.cwl
    out: []
