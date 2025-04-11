#!/usr/bin/env cwltool
cwlVersion: v1.0
class: Workflow

requirements:
  SubworkflowFeatureRequirement: {}

inputs:
  repo_url:
    type: string
  branch:
    type: string
  pipeline_id:
    type: string
  run_id:
    type: string
  server_url:
    type: string

outputs:
  pylint_report:
    type: File
    outputSource: pylint_workflow/pylint_report
  flake8_report:
    type: File
    outputSource: flake8_workflow/flake8_report
  ruff_report:
    type: File
    outputSource: ruff_workflow/ruff_report
  bandit_report:
    type: File
    outputSource: bandit_workflow/bandit_report

steps:
  clone_step:
    in:
      repo_url: repo_url
      branch: branch
    run: tools/clone-tool.cwl
    out:
    - repo_directory
  pylint_workflow:
    in:
      repo_path: clone_step/repo_directory
      pipeline_id: pipeline_id
      run_id: run_id
      server_url: server_url
    run: pylint-workflow.cwl
    out:
    - pylint_report
  flake8_workflow:
    in:
      repo_path: clone_step/repo_directory
      pipeline_id: pipeline_id
      run_id: run_id
      server_url: server_url
    run: flake8-workflow.cwl
    out:
    - flake8_report
  ruff_workflow:
    in:
      repo_path: clone_step/repo_directory
      pipeline_id: pipeline_id
      run_id: run_id
      server_url: server_url
    run: ruff-workflow.cwl
    out:
    - ruff_report
  bandit_workflow:
    in:
      repo_path: clone_step/repo_directory
      pipeline_id: pipeline_id
      run_id: run_id
      server_url: server_url
    run: bandit-workflow.cwl
    out:
    - bandit_report
