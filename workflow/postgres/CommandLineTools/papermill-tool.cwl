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