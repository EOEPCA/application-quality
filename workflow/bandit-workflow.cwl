#!/usr/bin/env cwltool
cwlVersion: v1.0
class: Workflow

inputs:
  name:
    type: string
    default: bandit
  pipeline_id:
    type: string
  repo_path:
    type: Directory
  run_id:
    type: string
  server_url:
    type: string

outputs:
  bandit_report:
    type: File
    outputSource: bandit_step/bandit_report

steps:
  bandit_step:
    in:
      source_directory: repo_path
    run: tools/bandit-tool.cwl
    out:
    - bandit_report
  save_bandit_step:
    in:
      name: name
      pipeline_id: pipeline_id
      report: bandit_step/bandit_report
      run_id: run_id
      server_url: server_url
    run: tools/save-tool.cwl
    out: []
