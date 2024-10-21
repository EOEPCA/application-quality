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
  pylint_step_id:
    type: string
    default: 1-pylint

outputs:
  pylint_report:
    type: File
    outputSource: pylint_step/pylint_report

steps:
  pylint_step:
    in:
      source_directory: repo_path
    run: tools/pylint-tool.cwl
    out:
    - pylint_report
  save_pylint_step:
    in:
      pipeline_id: pipeline_id
      report: pylint_step/pylint_report
      run_id: run_id
      server_url: server_url
      step_id: pylint_step_id
    run: tools/save-tool.cwl
    out: []
