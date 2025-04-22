#!/usr/bin/env cwltool

$graph:
- class: Workflow

  requirements:
    SubworkflowFeatureRequirement: {}

  inputs:
    clone_subworkflow.clone.repo_branch: string
    clone_subworkflow.clone.repo_url: string
    ipynb_specs_checker_subworkflow.filter.regex: string
    ipynb_specs_checker_subworkflow.ipynb_specs_checker.schema: string
    papermill_subworkflow.filter.regex: string
    pipeline_id:
      type: string
      default: notebook
    ruff_subworkflow.filter.regex: string
    ruff_subworkflow.ruff.verbose: boolean
    run_id: string
    server_url: string

  outputs:
    ipynb_specs_checker_report:
      type: File
      outputSource: ipynb_specs_checker_subworkflow/ipynb_specs_checker_report
    papermill_output_notebooks:
      type: File[]
      outputSource: papermill_subworkflow/output_notebooks
    ruff_report:
      type: File
      outputSource: ruff_subworkflow/ruff_report

  steps:
    clone_subworkflow:
      in:
        clone.repo_branch: clone_subworkflow.clone.repo_branch
        clone.repo_url: clone_subworkflow.clone.repo_url
      run: '#clone_subworkflow'
      out:
      - repo_directory
    ipynb_specs_checker_subworkflow:
      in:
        filter.regex: ipynb_specs_checker_subworkflow.filter.regex
        ipynb_specs_checker.schema: ipynb_specs_checker_subworkflow.ipynb_specs_checker.schema
        pipeline_id: pipeline_id
        run_id: run_id
        server_url: server_url
        source_directory: clone_subworkflow/repo_directory
      run: '#ipynb_specs_checker_subworkflow'
      out:
      - ipynb_specs_checker_report
    papermill_subworkflow:
      in:
        filter.regex: papermill_subworkflow.filter.regex
        pipeline_id: pipeline_id
        run_id: run_id
        server_url: server_url
        source_directory: clone_subworkflow/repo_directory
      run: '#papermill_subworkflow'
      out:
      - output_notebooks
    ruff_subworkflow:
      in:
        filter.regex: ruff_subworkflow.filter.regex
        pipeline_id: pipeline_id
        ruff.verbose: ruff_subworkflow.ruff.verbose
        run_id: run_id
        server_url: server_url
        source_directory: clone_subworkflow/repo_directory
      run: '#ruff_subworkflow'
      out:
      - ruff_report
  id: main
- class: Workflow

  inputs:
    clone.repo_branch:
      type: string
      default: ''
    clone.repo_url: string

  outputs:
    repo_directory:
      type: Directory
      outputSource: clone_step/repo_directory

  steps:
    clone_step:
      in:
        repo_branch: clone.repo_branch
        repo_url: clone.repo_url
      run: '#clone_tool'
      out:
      - repo_directory
  id: clone_subworkflow
- class: Workflow

  inputs:
    name:
      type: string
      default: ipynb_specs_checker
    filter.regex: string
    ipynb_specs_checker.schema: string
    pipeline_id: string
    run_id: string
    server_url: string
    source_directory: Directory

  outputs:
    ipynb_specs_checker_report:
      type: File
      outputSource: ipynb_specs_checker_step/ipynb_specs_checker_report

  steps:
    filter_ipynb_specs_checker_step:
      in:
        regex: filter.regex
        source_directory: source_directory
      run: '#filter_tool'
      out:
      - file_list
    ipynb_specs_checker_step:
      in:
        file_list: filter_ipynb_specs_checker_step/file_list
        schema: ipynb_specs_checker.schema
        source_directory: source_directory
      run: '#ipynb_specs_checker_tool'
      out:
      - ipynb_specs_checker_report
    save_ipynb_specs_checker_step:
      in:
        name: name
        pipeline_id: pipeline_id
        report: ipynb_specs_checker_step/ipynb_specs_checker_report
        run_id: run_id
        server_url: server_url
      run: '#save_tool'
      out: []
  id: ipynb_specs_checker_subworkflow
- class: Workflow

  requirements:
    ScatterFeatureRequirement: {}

  inputs:
    name:
      type: string
      default: papermill
    filter.regex: string
    pipeline_id: string
    run_id: string
    server_url: string
    source_directory: Directory

  outputs:
    output_notebooks:
      type: File[]
      outputSource: papermill_step/output_nb

  steps:
    filter_papermill_step:
      in:
        regex: filter.regex
        source_directory: source_directory
      run: '#filter_tool'
      out:
      - file_list
    papermill_step:
      in:
        notebook_path: filter_papermill_step/file_list
        source_directory: source_directory
      scatter: notebook_path
      run: '#papermill_tool'
      out:
      - output_nb
    save_papermill_step:
      in:
        name: name
        pipeline_id: pipeline_id
        report: papermill_step/output_nb
        run_id: run_id
        server_url: server_url
      scatter: report
      run: '#save_tool'
      out: []
  id: papermill_subworkflow
- class: Workflow

  inputs:
    name:
      type: string
      default: ruff
    filter.regex: string
    pipeline_id: string
    ruff.verbose: boolean
    run_id: string
    server_url: string
    source_directory: Directory

  outputs:
    ruff_report:
      type: File
      outputSource: ruff_step/ruff_report

  steps:
    filter_ruff_step:
      in:
        regex: filter.regex
        source_directory: source_directory
      run: '#filter_tool'
      out:
      - file_list
    ruff_step:
      in:
        file_list: filter_ruff_step/file_list
        source_directory: source_directory
        verbose: ruff.verbose
      run: '#ruff_tool'
      out:
      - ruff_report
    save_ruff_step:
      in:
        name: name
        pipeline_id: pipeline_id
        report: ruff_step/ruff_report
        run_id: run_id
        server_url: server_url
      run: '#save_tool'
      out: []
  id: ruff_subworkflow
- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: alpine:latest
    InitialWorkDirRequirement:
      listing:
      - entryname: script.sh
        entry: |-
          cd $(inputs.source_directory.path)
          find . -type f -regex "$(inputs.regex)" > $HOME/filter.out
    InlineJavascriptRequirement: {}

  inputs:
    regex: string
    source_directory: Directory

  outputs:
    file_list:
      type: string[]
      outputBinding:
        glob: filter.out
        outputEval: |-
          $(self[0].contents.split('\n').filter(function(line) {return line.trim() !== '';}))
        loadContents: true

  baseCommand: sh
  arguments:
  - script.sh
  id: filter_tool
- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: curlimages/curl
    InlineJavascriptRequirement: {}

  inputs:
    name: string
    pipeline_id: string
    report: File
    run_id: string
    server_url: string

  outputs: []

  baseCommand: curl
  arguments:
  - prefix: -X
    valueFrom: POST
  - prefix: -L
    valueFrom: |-
      $('http://' + inputs.server_url + '/api/pipelines/' + inputs.pipeline_id + '/runs/' + inputs.run_id + '/jobreports/?name=' + inputs.name)
  - prefix: -H
    valueFrom: Content-Type:application/json
  - prefix: -d
    valueFrom: $('@' + inputs.report.path)
  id: save_tool
- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: alpine/git
    InitialWorkDirRequirement:
      listing:
      - entryname: clone_branch.sh
        entry: |-
          set -e

          if [ $(inputs.repo_branch) ]; then
              echo 'Branch specified: $(inputs.repo_branch). Cloning branch...'
              git clone $(inputs.repo_url) -b $(inputs.repo_branch)
          else
              echo 'No branch specified. Cloning default branch...'
              git clone $(inputs.repo_url)
          fi
    InlineJavascriptRequirement: {}

  inputs:
    repo_branch: string
    repo_url: string

  outputs:
    repo_directory:
      type: Directory
      outputBinding:
        glob: $(inputs.repo_url.split('/').pop().replace('.git',''))

  baseCommand: sh
  arguments:
  - clone_branch.sh
  id: clone_tool
- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: python:slim
    InitialWorkDirRequirement:
      listing:
      - entryname: script.sh
        entry: |-
          cd $(inputs.source_directory.path)
          python ~/script.py > ~/ipynb_specs_checker_report.json
          exit 0
      - entryname: script.py
        entry: |-
          import json
          import os

          files = '$(inputs.file_list.join(" "))'
          schema = '$(inputs.schema)'

          def read_notebook(notebook_path: str):
              result = {"filename": os.path.relpath(notebook_path, os.path.expanduser('$(inputs.source_directory.path)/..')), "schema": schema}
              try:
                  with open(notebook_path) as f:
                      notebook = json.load(f)
              except Exception as e:
                  result['error'] = (f"Error reading notebook file: {e}")
                  return result

              if "metadata" not in notebook:
                  result['error'] = ("Notebook does not contain a 'metadata' section.")
                  return result

              metadata = notebook["metadata"]

              if schema.lower() == "eumetsat":
                  mandatory_fields = ["author", "title", "description", "services"]
                  optional_fields = ["image", "tags"]
              elif schema.lower() == "schema.org":
                  mandatory_fields = ["author", "name", "description", "keywords"]
                  optional_fields = ["identifier", "image", "potentialAction", "domain", "platform", "instruments", "tags", "license"]
              else:
                  result['error'] = f"Unknown schema type: {schema}"
                  return result

              errors = []
              for field in mandatory_fields:
                  if field not in metadata:
                      errors.append(field)

              warnings = []
              for field in optional_fields:
                  if field not in metadata:
                      warnings.append(field)

              result['valid'] = (len(errors) == 0)
              result['missing_mandatory_fields'] = errors
              result['missing_optional_fields'] = warnings

              return result

          output = []

          file_list = files.split(sep=' ')
          for notebook_path in file_list:
              output.append(read_notebook(notebook_path))

          print(json.dumps(output, indent=4))
    InlineJavascriptRequirement: {}

  inputs:
    file_list: string[]
    schema: string
    source_directory: Directory

  outputs:
    ipynb_specs_checker_report:
      type: File
      outputBinding:
        glob: ipynb_specs_checker_report.json

  baseCommand: sh
  arguments:
  - script.sh
  id: ipynb_specs_checker_tool
- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: continuumio/miniconda3
    InitialWorkDirRequirement:
      listing:
      - entryname: script.sh
        entry: |-
          set -e

          cat ~/err.ipynb > ~/out.ipynb
          cd $(inputs.source_directory.path)

          pip install pyyaml

          python ~/script.py $(inputs.notebook_path) | tee ~/environment.yml

          if [ ! -s ~/environment.yml ]; then
            echo "Error: environment.yml is empty. Aborting environment creation."
            exit 1
          fi

          ENV=`grep "name: " ~/environment.yml | cut - -d' ' -f2`

          conda env create -f ~/environment.yml
          conda run -n $ENV pip install ipykernel papermill
          conda run -n $ENV ipython kernel install --user --name $ENV 
          conda run -n $ENV papermill $(inputs.notebook_path) ~/out.ipynb
      - entryname: script.py
        entry: |-
          import json
          import yaml
          import sys

          try:
              with open('$(inputs.notebook_path)') as f:
                  nb_json = json.load(f)
          except Exception as e:
              sys.stderr.write(f"Failed to load notebook: {e}\\n")
              sys.exit(1)

          try:
              env = nb_json["metadata"]["software_requirements"]["conda_environment"]
              kernelspec = nb_json["metadata"]["kernelspec"]["name"]
          except KeyError as e:
              sys.stderr.write(f"Missing key in notebook metadata: {e}\\n")
              sys.exit(1)

          if env["name"] == kernelspec:
              if env.get("dependencies"):
                  res = yaml.dump({"name": env["name"], "dependencies": env["dependencies"]})
                  print(res)
              else:
                  sys.stderr.write("No dependencies found in the environment specification.\\n")
                  sys.exit(1)
          else:
              sys.stderr.write("Kernel name does not match the conda environment name.\\n")
              sys.exit(1)
      - entryname: err.ipynb
        entry: |-
          {
            "cells": [
              {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                  "Error: The notebook could not be run."
                ]
              }
            ],
            "metadata": {
              "language_info": {
                "name": "python"
              }
            },
            "nbformat": 4,
            "nbformat_minor": 2
          }

  inputs:
    notebook_path: string
    source_directory: Directory

  outputs:
    output_nb:
      type: File
      outputBinding:
        glob: out.ipynb

  baseCommand: sh
  arguments:
  - script.sh
  id: papermill_tool
- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: ghcr.io/astral-sh/ruff:alpine
    InitialWorkDirRequirement:
      listing:
      - entryname: script.sh
        entry: |-
          cd $(inputs.source_directory.path)

          PARAMS="--output-format $(inputs.output_format) -o $HOME/$(inputs.output_file)"
          if [ "$(inputs.exit_zero)" == "true" ] ; then
            PARAMS="$PARAMS -e"
          fi
          if [ "$(inputs.no_cache)" == "true" ] ; then
            PARAMS="$PARAMS -n"
          fi
          if [ "$(inputs.verbose)" == "true" ] ; then
            PARAMS="$PARAMS -v"
          fi

          ruff check $PARAMS $(inputs.file_list.join(" "))
    InlineJavascriptRequirement: {}

  inputs:
    exit_zero:
      label: Exit with zero
      doc: Exit with status code "0", even upon detecting lint violations.
      type: boolean
      default: true
    file_list: string[]
    no_cache:
      label: Disable cache
      doc: Disable cache reads.
      type: boolean
      default: true
    output_file:
      label: Output file
      doc: Specify file to write the linter output to.
      type: string
      default: ruff_report.json
    output_format:
      label: Output format
      doc: |-
        Output serialization format for violations. Possible values: concise, full, json, json-lines, junit, grouped, github, gitlab, pylint, rdjson, azure, sarif.
      type: string
      default: json
    source_directory: Directory
    verbose: boolean

  outputs:
    ruff_report:
      type: File
      outputBinding:
        glob: $(inputs.output_file)

  baseCommand: sh
  arguments:
  - script.sh
  id: ruff_tool
cwlVersion: v1.0
