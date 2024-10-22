#!/usr/bin/env cwltool
cwlVersion: v1.0
class: Workflow

inputs:
  repo_path:
    type: Directory
  pipeline_id:
    type: string
  run_id:
    type: string
  server_url:
    type: string
  flake8_step_id:
    type: string
    default: 2-flake8

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
      pipeline_id: pipeline_id
      report: flake8_step/flake8_report
      run_id: run_id
      server_url: server_url
      step_id: flake8_step_id
    run: tools/save-tool.cwl
    out: []
