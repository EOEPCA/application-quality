#!/usr/bin/env cwltool
cwlVersion: v1.0
class: Workflow

inputs:
  name:
    type: string
    default: pylint
  pipeline_id:
    type: string
  repo_path:
    type: Directory
  run_id:
    type: string
  server_url:
    type: string

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
      name: name
      pipeline_id: pipeline_id
      report: pylint_step/pylint_report
      run_id: run_id
      server_url: server_url
    run: tools/save-tool.cwl
    out: []
