#!/usr/bin/env cwltool
cwlVersion: v1.0
class: Workflow

inputs:
  repo_url:
    type: string
  run_id:
    type: string
  pylint_step_id:
    type: string
    default: "1-pylint"
  flake8_step_id:
    type: string
    default: "2-flake8"

steps:
  clone_step:
    run: tools/clone-tool.cwl
    in:
      repo_url: repo_url
    out: [repo_directory]
  pylint_step:
    run: tools/pylint-tool.cwl
    in:
      source_directory: clone_step/repo_directory
    out: [pylint_report]
  save_pylint_step:
    run: tools/save-tool.cwl
    in:
      run_id: run_id
      step_id: pylint_step_id
      report: pylint_step/pylint_report
    out: []
  flake8_step:
    run: tools/flake8-tool.cwl
    in:
      source_directory: clone_step/repo_directory
    out: [flake8_report]
  save_flake8_step:
    run: tools/save-tool.cwl
    in:
      run_id: run_id
      step_id: flake8_step_id
      report: flake8_step/flake8_report
    out: []

outputs:
#   wrap_up:
#     type: File
#     outputSource: # wrap_up_step/wrap_up
#   repo_directory:
#     type: Directory
#     outputSource: clone_step/repo_directory
  pylint_report:
    type: File
    outputSource: pylint_step/pylint_report
  flake8_report:
    type: File
    outputSource: flake8_step/flake8_report
