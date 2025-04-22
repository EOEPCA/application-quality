- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: python:slim
    InitialWorkDirRequirement:
      listing:
      - entryname: script.sh
        entry: |-
          pip install jsonschema
          cd $(inputs.source_directory.path)
          python ~/script.py > ~/ipynb_specs_checker_report.json
          exit 0
      - entryname: script.py
        entry: |-
          from jsonschema import Draft7Validator
          import os
          import json
          
          def process_notebook(notebook_path: str, encoding: str) -> dict:
              abs_path = os.path.abspath(notebook_path)
              home_dir = os.path.expanduser("~")
          
              result = {
                  "filename": os.path.relpath(abs_path, home_dir),
                  "schema": encoding
              }
          
              try:
                  with open(notebook_path) as f:
                      notebook = json.load(f)
              except Exception as e:
                  result["error"] = f"Error reading notebook file: {e}"
                  return result
          
              if "metadata" not in notebook:
                  result["error"] = "Notebook does not contain a 'metadata' section."
                  return result
          
              metadata = notebook["metadata"]
          
              if encoding.lower() == "eumetsat":
                  schema_file = "/home/hcremers/dev/application-quality/workflow/jsonschema/eumetsat.schema.json"
              elif encoding.lower() == "schema.org":
                  schema_file = "/home/hcremers/dev/application-quality/workflow/jsonschema/schema_org.schema.json"
              else:
                  result["error"] = f"Unknown encoding type: {encoding}"
                  return result
          
              with open(schema_file) as f:
                  schema = json.load(f)
          
              validator = Draft7Validator(schema)
              errors = sorted(validator.iter_errors(metadata), key=lambda e: e.path)  # returns an Iterable of ValidationErrors
          
              missing_mandatory_fields = []
              validation_errors = []
          
              for err in errors:
                  if err.validator == "required":
                      missing_mandatory_fields.extend(err.message.split("'")[1::2])  # gets missing fields from the message
                  else:
                      validation_errors.append(f"At {list(err.path)}: {err.message}")
          
              optional_fields = [
                  key
                  for key in schema.get("properties", {})
                  if key not in metadata and key not in schema.get("required", [])
              ]
          
              result.update(
                  {
                      "valid": len(missing_mandatory_fields) == 0 and len(validation_errors) == 0,
                      "missing_mandatory_fields": list(set(missing_mandatory_fields)),
                      "missing_optional_fields": optional_fields,
                  }
              )
          
              if validation_errors:
                  result["schema_validation_errors"] = validation_errors
          
              return result
          
          
          output = []
          
          for notebook_path in INPUTS_FILELIST:
              output.append(process_notebook(notebook_path, INPUTS_SCHEMA))
          
          print(json.dumps(output, indent=4))
    InlineJavascriptRequirement: {}

  inputs:
    schema: string
    file_list: string[]
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