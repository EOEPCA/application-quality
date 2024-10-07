#!/usr/bin/env cwltool
cwlVersion: v1.0
class: Workflow

inputs:
  repo_path:
    type: Directory
  run_id:
    type: string
  pylint_step_id:
    type: string
    default: "1-pylint"

steps:
  pylint_step:
    run: tools/pylint-tool.cwl
    in:
      source_directory: repo_path
    out: [pylint_report]
  save_pylint_step:
    run: tools/save-tool.cwl
    in:
      run_id: run_id
      step_id: pylint_step_id
      report: pylint_step/pylint_report
    out: []

outputs:
  pylint_report:
    type: File
    outputSource: pylint_step/pylint_report
