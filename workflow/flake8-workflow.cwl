#!/usr/bin/env cwltool
cwlVersion: v1.0
class: Workflow

inputs:
  repo_path:
    type: Directory
  run_id:
    type: string
  flake8_step_id:
    type: string
    default: "2-flake8"

steps:
  flake8_step:
    run: tools/flake8-tool.cwl
    in:
      source_directory: repo_path
    out: [flake8_report]
  save_flake8_step:
    run: tools/save-tool.cwl
    in:
      run_id: run_id
      step_id: flake8_step_id
      report: flake8_step/flake8_report
    out: []

outputs:
  flake8_report:
    type: File
    outputSource: flake8_step/flake8_report
