#!/usr/bin/env cwltool

$graph:
- class: Workflow

  requirements:
    SubworkflowFeatureRequirement: {}

  inputs:
    bandit_subworkflow.bandit.verbose:
      label: Verbose
      doc: Output extra information like excluded and included files.
      type: boolean
      default: false
    bandit_subworkflow.filter.regex:
      label: regex
      type: string
      default: .*\.py
    branch:
      type: string
      default: ''
    flake8_subworkflow.filter.regex:
      label: regex
      type: string
      default: .*\.py
    flake8_subworkflow.flake8.verbose:
      label: Verbose
      doc: |-
        Increase the verbosity of Flake8’s output.
      type: boolean
      default: false
    pipeline_id: string
    pylint_subworkflow.filter.regex:
      label: regex
      type: string
      default: .*\.py
    pylint_subworkflow.pylint.disable:
      label: Disable IDs
      doc: |-
        Disable the message, report, category or checker with the given id(s). You can either give multiple identifiers separated by comma (,) or put this option multiple times (only on the command line, not in the configuration file where it should appear only once). You can also use "--disable=all" to disable everything first and then re-enable specific checks. For example, if you want to run only the similarities checker, you can use "--disable=all --enable=similarities". If you want to run only the classes checker, but have no Warning level messages displayed, use "--disable=all --enable=classes --disable=W".
      type: string
      default: E0401
    pylint_subworkflow.pylint.errors_only:
      label: Errors only
      doc: |-
        In error mode, messages with a category besides ERROR or FATAL are suppressed, and no reports are done by default. Error mode is compatible with disabling specific errors.
      type: boolean
      default: false
    pylint_subworkflow.pylint.verbose:
      label: Verbose
      doc: |-
        In verbose mode, extra non-checker-related info will be displayed.
      type: boolean
      default: false
    repo_url: string
    ruff_subworkflow.filter.regex:
      label: regex
      type: string
      default: .*\.py
    ruff_subworkflow.ruff.verbose:
      label: Verbose
      doc: |-
        Enable verbose logging.
      type: boolean
      default: false
    run_id: string
    server_url: string

  outputs: []

  steps:
    bandit_subworkflow:
      in:
        bandit.verbose: bandit_subworkflow.bandit.verbose
        filter.regex: bandit_subworkflow.filter.regex
        pipeline_id: pipeline_id
        run_id: run_id
        server_url: server_url
        source_directory: clone_step/repo_directory
      run: '#bandit_subworkflow'
      out: []
    clone_step:
      in:
        branch: branch
        repo_url: repo_url
      run: '#clone_tool'
      out:
      - repo_directory
    flake8_subworkflow:
      in:
        filter.regex: flake8_subworkflow.filter.regex
        flake8.verbose: flake8_subworkflow.flake8.verbose
        pipeline_id: pipeline_id
        run_id: run_id
        server_url: server_url
        source_directory: clone_step/repo_directory
      run: '#flake8_subworkflow'
      out: []
    pylint_subworkflow:
      in:
        filter.regex: pylint_subworkflow.filter.regex
        pipeline_id: pipeline_id
        pylint.disable: pylint_subworkflow.pylint.disable
        pylint.errors_only: pylint_subworkflow.pylint.errors_only
        pylint.verbose: pylint_subworkflow.pylint.verbose
        run_id: run_id
        server_url: server_url
        source_directory: clone_step/repo_directory
      run: '#pylint_subworkflow'
      out: []
    ruff_subworkflow:
      in:
        filter.regex: ruff_subworkflow.filter.regex
        pipeline_id: pipeline_id
        ruff.verbose: ruff_subworkflow.ruff.verbose
        run_id: run_id
        server_url: server_url
        source_directory: clone_step/repo_directory
      run: '#ruff_subworkflow'
      out: []
  id: main
- class: Workflow

  inputs:
    name:
      type: string
      default: bandit
    bandit.verbose: boolean
    filter.regex: string
    pipeline_id: string
    run_id: string
    server_url: string
    source_directory: Directory

  outputs:
    bandit_report:
      type: File
      outputSource: bandit_step/bandit_report

  steps:
    bandit_step:
      in:
        file_list: filter_bandit_step/file_list
        source_directory: source_directory
        verbose: bandit.verbose
      run: '#bandit_tool'
      out:
      - bandit_report
    filter_bandit_step:
      in:
        regex: filter.regex
        source_directory: source_directory
      run: '#filter_tool'
      out:
      - file_list
    save_bandit_step:
      in:
        name: name
        pipeline_id: pipeline_id
        report: bandit_step/bandit_report
        run_id: run_id
        server_url: server_url
      run: '#save_tool'
      out: []
  id: bandit_subworkflow
- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: cytopia/bandit
    InitialWorkDirRequirement:
      listing:
      - entryname: script.sh
        entry: |-
          cd $(inputs.source_directory.path)

          PARAMS="-f $(inputs.output_format) -o $HOME/$(inputs.output_file)"
          if [ "$(inputs.exit_zero)" == "true" ] ; then
            PARAMS="$PARAMS --exit-zero"
          fi
          if [ "$(inputs.verbose)" == "true" ] ; then
            PARAMS="$PARAMS -v"
          fi

          bandit $PARAMS $(inputs.file_list.join(" "))
    InlineJavascriptRequirement: {}

  inputs:
    exit_zero:
      label: Exit with zero
      doc: Exit with 0, even with results found.
      type: boolean
      default: true
    file_list: string[]
    output_file:
      label: Output file
      doc: Write report to filename.
      type: string
      default: bandit_report.json
    output_format:
      label: Output format
      doc: Specify output format.
      type: string
      default: json
    source_directory: Directory
    verbose: boolean

  outputs:
    bandit_report:
      type: File
      outputBinding:
        glob: $(inputs.output_file)

  baseCommand: sh
  arguments:
  - script.sh
  id: bandit_tool
- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: alpine/git
    InitialWorkDirRequirement:
      listing:
      - entryname: clone_branch.sh
        entry: |-
          set -e

          if [ $(inputs.branch) ]; then
            echo 'Branch specified: $(inputs.branch). Cloning branch...'
            git clone $(inputs.repo_url) -b $(inputs.branch)
          else
            echo 'No branch specified. Cloning default branch...'
            git clone $(inputs.repo_url)
          fi

          echo '✅ Cloned!
          '
    InlineJavascriptRequirement: {}

  inputs:
    branch: string
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
        outputEval: $(self[0].contents.split('\n').filter(line => line.trim() !==
          ''))
        loadContents: true

  baseCommand: sh
  arguments:
  - script.sh
  id: filter_tool
- class: Workflow

  inputs:
    name:
      type: string
      default: flake8
    filter.regex: string
    flake8.verbose: boolean
    pipeline_id: string
    run_id: string
    server_url: string
    source_directory: Directory

  outputs:
    flake8_report:
      type: File
      outputSource: flake8_step/flake8_report

  steps:
    filter_flake8_step:
      in:
        regex: filter.regex
        source_directory: source_directory
      run: '#filter_tool'
      out:
      - file_list
    flake8_step:
      in:
        file_list: filter_flake8_step/file_list
        source_directory: source_directory
        verbose: flake8.verbose
      run: '#flake8_tool'
      out:
      - flake8_report
    save_flake8_step:
      in:
        name: name
        pipeline_id: pipeline_id
        report: flake8_step/flake8_report
        run_id: run_id
        server_url: server_url
      run: '#save_tool'
      out: []
  id: flake8_subworkflow
- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: eoepca/appquality-flake8-json:v0.1.0
    InitialWorkDirRequirement:
      listing:
      - entryname: script.sh
        entry: |-
          cd $(inputs.source_directory.path)

          PARAMS="--format=$(inputs.output_format) --output-file=$HOME/$(inputs.output_file)"
          if [ "$(inputs.exit_zero)" == "true" ] ; then
            PARAMS="$PARAMS --exit-zero"
          fi
          if [ "$(inputs.verbose)" == "true" ] ; then
            PARAMS="$PARAMS -v"
          fi

          flake8 $PARAMS $(inputs.file_list.join(" "))
    InlineJavascriptRequirement: {}

  inputs:
    exit_zero:
      label: Exit with zero
      doc: Force Flake8 to use the exit status code 0 even if there are errors.
      type: boolean
      default: true
    file_list: string[]
    output_file:
      label: Output file
      doc: Redirect all output to the specified file.
      type: string
      default: flake8_report.json
    output_format:
      label: Output format
      doc: Select the formatter used to display errors to the user.
      type: string
      default: json
    source_directory: Directory
    verbose: boolean

  outputs:
    flake8_report:
      type: File
      outputBinding:
        glob: $(inputs.output_file)

  baseCommand: sh
  arguments:
  - script.sh
  id: flake8_tool
- class: Workflow

  inputs:
    name:
      type: string
      default: pylint
    filter.regex: string
    pipeline_id: string
    pylint.disable: string
    pylint.errors_only: boolean
    pylint.verbose: boolean
    run_id: string
    server_url: string
    source_directory: Directory

  outputs:
    pylint_report:
      type: File
      outputSource: pylint_step/pylint_report

  steps:
    filter_pylint_step:
      in:
        regex: filter.regex
        source_directory: source_directory
      run: '#filter_tool'
      out:
      - file_list
    pylint_step:
      in:
        disable: pylint.disable
        errors_only: pylint.errors_only
        file_list: filter_pylint_step/file_list
        source_directory: source_directory
        verbose: pylint.verbose
      run: '#pylint_tool'
      out:
      - pylint_report
    save_pylint_step:
      in:
        name: name
        pipeline_id: pipeline_id
        report: pylint_step/pylint_report
        run_id: run_id
        server_url: server_url
      run: '#save_tool'
      out: []
  id: pylint_subworkflow
- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: cytopia/pylint
    InitialWorkDirRequirement:
      listing:
      - entryname: script.sh
        entry: |-
          cd $(inputs.source_directory.path)

          PARAMS="--output-format=$(inputs.output_format) --output=$HOME/$(inputs.output_file) --disable=$(inputs.disable)"
          if [ "$(inputs.exit_zero)" == "true" ] ; then
            PARAMS="$PARAMS --exit-zero"
          fi
          if [ "$(inputs.errors_only)" == "true" ] ; then
            PARAMS="$PARAMS -E"
          fi
          if [ "$(inputs.verbose)" == "true" ] ; then
            PARAMS="$PARAMS -v"
          fi

          pylint $PARAMS $(inputs.file_list.join(" "))
    InlineJavascriptRequirement: {}

  inputs:
    disable: string
    errors_only: boolean
    exit_zero:
      doc: |-
        Always return a 0 (non-error) status code, even if lint errors are found. This is primarily useful in continuous integration scripts.
      type: boolean
      default: true
    file_list: string[]
    output_file:
      doc: Specify an output file.
      type: string
      default: pylint_report.json
    output_format:
      doc: |-
        Set the output format. Available formats are: text, parseable, colorized, json2 (improved json format), json (old json format) and msvs (visual studio). You can also give a reporter class, e.g. mypackage.mymodule.MyReporterClass.
      type: string
      default: json
    source_directory: Directory
    verbose: boolean

  outputs:
    pylint_report:
      type: File
      outputBinding:
        glob: $(inputs.output_file)

  baseCommand: sh
  arguments:
  - script.sh
  id: pylint_tool
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
cwlVersion: v1.0
