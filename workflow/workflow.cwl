#!/usr/bin/env cwltool
cwlVersion: v1.0
class: Workflow

requirements:
  SubworkflowFeatureRequirement: {}

inputs:
  repo_url:
    type: string
  run_id:
    type: string

steps:
  clone_step:
    run: tools/clone-tool.cwl
    in:
      repo_url: repo_url
    out: [repo_directory]
  pylint_workflow:
    run: pylint-workflow.cwl
    in:
      repo_path: clone_step/repo_directory
      run_id: run_id
    out: [pylint_report]
  flake8_workflow:
    run: flake8-workflow.cwl
    in:
      repo_path: clone_step/repo_directory
      run_id: run_id
    out: [flake8_report]

outputs:
#   wrap_up:
#     type: File
#     outputSource: # wrap_up_step/wrap_up
#   repo_directory:
#     type: Directory
#     outputSource: clone_step/repo_directory
  pylint_report:
    type: File
    outputSource: pylint_workflow/pylint_report
  flake8_report:
    type: File
    outputSource: flake8_workflow/flake8_report
