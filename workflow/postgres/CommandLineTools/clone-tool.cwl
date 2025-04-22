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